from httpx import AsyncClient


async def test_create_aircraft_success(client: AsyncClient):
    payload = {
        "tail_number": "F-22A-014",
        "model": "F-22A Raptor",
        "squadron": "1st Fighter Wing",
        "status": "operational",
    }
    resp = await client.post("/aircraft", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] > 0
    assert body["tail_number"] == "F-22A-014"
    assert body["model"] == "F-22A Raptor"
    assert body["squadron"] == "1st Fighter Wing"
    assert body["status"] == "operational"
    assert "created_at" in body


async def test_create_aircraft_duplicate_tail_number(client: AsyncClient):
    payload = {"tail_number": "DUP-1", "model": "F-16C", "squadron": "X"}
    first = await client.post("/aircraft", json=payload)
    assert first.status_code == 201
    second = await client.post("/aircraft", json=payload)
    assert second.status_code == 409


async def test_create_aircraft_missing_required_field(client: AsyncClient):
    resp = await client.post("/aircraft", json={"model": "F-16C", "squadron": "X"})
    assert resp.status_code == 422


async def test_list_aircraft_empty(client: AsyncClient):
    resp = await client.get("/aircraft")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_aircraft_with_data(client: AsyncClient):
    for i in range(3):
        r = await client.post(
            "/aircraft",
            json={"tail_number": f"AC-{i}", "model": "F-15E", "squadron": "Test"},
        )
        assert r.status_code == 201
    resp = await client.get("/aircraft")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


async def test_list_aircraft_filter_by_status(client: AsyncClient):
    await client.post(
        "/aircraft",
        json={"tail_number": "OP-1", "model": "F-15E", "squadron": "X", "status": "operational"},
    )
    await client.post(
        "/aircraft",
        json={"tail_number": "GR-1", "model": "F-15E", "squadron": "X", "status": "grounded"},
    )
    resp = await client.get("/aircraft", params={"status": "grounded"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["tail_number"] == "GR-1"


async def test_get_aircraft_by_id(client: AsyncClient, sample_aircraft: dict):
    resp = await client.get(f"/aircraft/{sample_aircraft['id']}")
    assert resp.status_code == 200
    assert resp.json()["tail_number"] == sample_aircraft["tail_number"]


async def test_get_aircraft_not_found(client: AsyncClient):
    resp = await client.get("/aircraft/99999")
    assert resp.status_code == 404


async def test_update_aircraft_status(client: AsyncClient, sample_aircraft: dict):
    resp = await client.patch(
        f"/aircraft/{sample_aircraft['id']}", json={"status": "grounded"}
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "grounded"


async def test_update_aircraft_partial(client: AsyncClient, sample_aircraft: dict):
    original_model = sample_aircraft["model"]
    resp = await client.patch(
        f"/aircraft/{sample_aircraft['id']}", json={"squadron": "57th Wing"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["squadron"] == "57th Wing"
    assert body["model"] == original_model
    assert body["tail_number"] == sample_aircraft["tail_number"]


async def test_delete_aircraft(client: AsyncClient, sample_aircraft: dict):
    aid = sample_aircraft["id"]
    resp = await client.delete(f"/aircraft/{aid}")
    assert resp.status_code == 204
    follow_up = await client.get(f"/aircraft/{aid}")
    assert follow_up.status_code == 404
