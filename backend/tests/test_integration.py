from httpx import AsyncClient


async def test_full_maintenance_lifecycle(client: AsyncClient):
    # Create aircraft
    ac_resp = await client.post(
        "/aircraft",
        json={"tail_number": "LC-1", "model": "F-35A", "squadron": "388 FW"},
    )
    assert ac_resp.status_code == 201
    aircraft_id = ac_resp.json()["id"]

    # Create work order (open)
    wo_resp = await client.post(
        "/work-orders",
        json={
            "aircraft_id": aircraft_id,
            "title": "Replace nav radio",
            "priority": "high",
        },
    )
    assert wo_resp.status_code == 201
    wid = wo_resp.json()["id"]
    assert wo_resp.json()["status"] == "open"

    # Assign technician + move to in_progress
    assign_resp = await client.patch(
        f"/work-orders/{wid}",
        json={"assigned_to": "SrA Patel", "status": "in_progress"},
    )
    assert assign_resp.status_code == 200
    assert assign_resp.json()["assigned_to"] == "SrA Patel"
    assert assign_resp.json()["status"] == "in_progress"

    # Resolve
    done_resp = await client.patch(f"/work-orders/{wid}", json={"status": "complete"})
    assert done_resp.status_code == 200
    assert done_resp.json()["status"] == "complete"

    # Verify final state
    final = await client.get(f"/work-orders/{wid}")
    assert final.status_code == 200
    assert final.json()["status"] == "complete"

    ac_check = await client.get(f"/aircraft/{aircraft_id}")
    assert ac_check.status_code == 200


async def test_ground_aircraft_and_create_critical_order(client: AsyncClient):
    ac_resp = await client.post(
        "/aircraft",
        json={"tail_number": "GR-CRIT", "model": "F-22A", "squadron": "1 FW"},
    )
    assert ac_resp.status_code == 201
    aircraft_id = ac_resp.json()["id"]

    ground = await client.patch(f"/aircraft/{aircraft_id}", json={"status": "grounded"})
    assert ground.status_code == 200
    assert ground.json()["status"] == "grounded"

    wo_resp = await client.post(
        "/work-orders",
        json={
            "aircraft_id": aircraft_id,
            "title": "Engine FOD inspection — bird strike suspected",
            "priority": "critical",
        },
    )
    assert wo_resp.status_code == 201
    body = wo_resp.json()
    assert body["priority"] == "critical"

    nested = await client.get(f"/work-orders/{body['id']}")
    assert nested.status_code == 200
    assert nested.json()["aircraft"]["status"] == "grounded"


async def test_cascade_work_orders_on_delete(client: AsyncClient):
    # Decision: WorkOrder.aircraft has cascade="all, delete-orphan" with
    # ON DELETE CASCADE on the FK, so deleting an aircraft removes its work
    # orders. Exposed orphan work orders would be a confusing audit trail —
    # keep ownership tight by cascading.
    ac_resp = await client.post(
        "/aircraft",
        json={"tail_number": "CSC-1", "model": "F-15E", "squadron": "X"},
    )
    assert ac_resp.status_code == 201
    aircraft_id = ac_resp.json()["id"]

    wo_ids: list[int] = []
    for title in ("Tire change", "Brake inspection"):
        wo = await client.post(
            "/work-orders", json={"aircraft_id": aircraft_id, "title": title}
        )
        assert wo.status_code == 201
        wo_ids.append(wo.json()["id"])

    delete_resp = await client.delete(f"/aircraft/{aircraft_id}")
    assert delete_resp.status_code == 204

    gone = await client.get(f"/aircraft/{aircraft_id}")
    assert gone.status_code == 404

    # Cascade was applied — work orders are also gone.
    for wid in wo_ids:
        followup = await client.get(f"/work-orders/{wid}")
        assert followup.status_code == 404
