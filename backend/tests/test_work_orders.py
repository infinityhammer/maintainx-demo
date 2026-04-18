from httpx import AsyncClient


async def test_create_work_order_success(client: AsyncClient, sample_aircraft: dict):
    payload = {
        "aircraft_id": sample_aircraft["id"],
        "title": "Inspect ejection seat",
        "description": "Annual safety inspection",
        "priority": "normal",
    }
    resp = await client.post("/work-orders", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] > 0
    assert body["title"] == "Inspect ejection seat"
    assert body["status"] == "open"
    assert body["aircraft_id"] == sample_aircraft["id"]


async def test_create_work_order_invalid_aircraft(client: AsyncClient):
    resp = await client.post(
        "/work-orders",
        json={"aircraft_id": 99999, "title": "Phantom job"},
    )
    assert resp.status_code == 404


async def test_create_work_order_missing_title(client: AsyncClient, sample_aircraft: dict):
    resp = await client.post(
        "/work-orders", json={"aircraft_id": sample_aircraft["id"]}
    )
    assert resp.status_code == 422


async def test_list_work_orders(client: AsyncClient, sample_aircraft: dict):
    for i in range(4):
        r = await client.post(
            "/work-orders",
            json={"aircraft_id": sample_aircraft["id"], "title": f"Task {i}"},
        )
        assert r.status_code == 201
    resp = await client.get("/work-orders")
    assert resp.status_code == 200
    assert len(resp.json()) == 4


async def test_filter_work_orders_by_status(client: AsyncClient, sample_aircraft: dict):
    a = await client.post(
        "/work-orders",
        json={"aircraft_id": sample_aircraft["id"], "title": "A"},
    )
    b = await client.post(
        "/work-orders",
        json={"aircraft_id": sample_aircraft["id"], "title": "B"},
    )
    assert a.status_code == 201 and b.status_code == 201
    move = await client.patch(f"/work-orders/{b.json()['id']}", json={"status": "in_progress"})
    assert move.status_code == 200

    resp = await client.get("/work-orders", params={"status": "in_progress"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["id"] == b.json()["id"]


async def test_filter_work_orders_by_aircraft(client: AsyncClient, sample_aircraft: dict):
    other = await client.post(
        "/aircraft",
        json={"tail_number": "OTHER-1", "model": "F-16C", "squadron": "X"},
    )
    assert other.status_code == 201

    await client.post(
        "/work-orders",
        json={"aircraft_id": sample_aircraft["id"], "title": "A"},
    )
    await client.post(
        "/work-orders",
        json={"aircraft_id": other.json()["id"], "title": "B"},
    )

    resp = await client.get("/work-orders", params={"aircraft_id": other.json()["id"]})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["title"] == "B"


async def test_get_work_order_includes_aircraft(client: AsyncClient, sample_work_order: dict):
    resp = await client.get(f"/work-orders/{sample_work_order['id']}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["aircraft"] is not None
    assert body["aircraft"]["id"] == sample_work_order["aircraft_id"]
    assert "tail_number" in body["aircraft"]


async def test_get_work_order_not_found(client: AsyncClient):
    resp = await client.get("/work-orders/99999")
    assert resp.status_code == 404


async def test_update_work_order_status_valid_transition(
    client: AsyncClient, sample_work_order: dict
):
    resp = await client.patch(
        f"/work-orders/{sample_work_order['id']}", json={"status": "in_progress"}
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


async def test_update_work_order_status_invalid_transition(
    client: AsyncClient, sample_work_order: dict
):
    wid = sample_work_order["id"]
    # Walk it to complete
    await client.patch(f"/work-orders/{wid}", json={"status": "in_progress"})
    await client.patch(f"/work-orders/{wid}", json={"status": "complete"})
    # Now try to walk it backwards
    resp = await client.patch(f"/work-orders/{wid}", json={"status": "open"})
    assert resp.status_code == 422
    assert "Invalid status transition" in resp.json()["detail"]


async def test_update_work_order_assign(client: AsyncClient, sample_work_order: dict):
    resp = await client.patch(
        f"/work-orders/{sample_work_order['id']}",
        json={"assigned_to": "TSgt Rivera"},
    )
    assert resp.status_code == 200
    assert resp.json()["assigned_to"] == "TSgt Rivera"


async def test_update_work_order_priority(client: AsyncClient, sample_work_order: dict):
    resp = await client.patch(
        f"/work-orders/{sample_work_order['id']}", json={"priority": "critical"}
    )
    assert resp.status_code == 200
    assert resp.json()["priority"] == "critical"


async def test_delete_work_order(client: AsyncClient, sample_work_order: dict):
    wid = sample_work_order["id"]
    resp = await client.delete(f"/work-orders/{wid}")
    assert resp.status_code == 204
    follow_up = await client.get(f"/work-orders/{wid}")
    assert follow_up.status_code == 404
