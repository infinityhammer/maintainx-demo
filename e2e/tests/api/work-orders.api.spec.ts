import { test, expect, APIRequestContext } from '@playwright/test';

let suffix: string;

test.beforeEach(() => {
  suffix = `${Date.now()}-${Math.floor(Math.random() * 10_000)}`;
});

async function createAircraft(request: APIRequestContext) {
  const resp = await request.post('/aircraft', {
    data: {
      tail_number: `WO-AC-${suffix}`,
      model: 'F-22A Raptor',
      squadron: '1 FW',
    },
  });
  expect(resp.status(), await resp.text()).toBe(201);
  return resp.json();
}

async function createWorkOrder(
  request: APIRequestContext,
  aircraftId: number,
  overrides: Record<string, unknown> = {}
) {
  const resp = await request.post('/work-orders', {
    data: {
      aircraft_id: aircraftId,
      title: 'Inspect tires',
      priority: 'normal',
      ...overrides,
    },
  });
  expect(resp.status(), await resp.text()).toBe(201);
  return resp.json();
}

test.describe('Work Orders API', () => {
  test('POST /work-orders creates with valid aircraft', async ({ request }) => {
    const aircraft = await createAircraft(request);
    const wo = await createWorkOrder(request, aircraft.id);
    expect(wo.id).toBeGreaterThan(0);
    expect(wo.status).toBe('open');
    expect(wo.aircraft_id).toBe(aircraft.id);
  });

  test('POST /work-orders returns 404 when aircraft is missing', async ({ request }) => {
    const resp = await request.post('/work-orders', {
      data: { aircraft_id: 999999, title: 'Phantom job' },
    });
    expect(resp.status()).toBe(404);
  });

  test('GET /work-orders returns array', async ({ request }) => {
    const aircraft = await createAircraft(request);
    await createWorkOrder(request, aircraft.id);
    const resp = await request.get('/work-orders');
    expect(resp.status()).toBe(200);
    expect(Array.isArray(await resp.json())).toBe(true);
  });

  test('GET /work-orders?status filters', async ({ request }) => {
    const aircraft = await createAircraft(request);
    const a = await createWorkOrder(request, aircraft.id, { title: `A-${suffix}` });
    const b = await createWorkOrder(request, aircraft.id, { title: `B-${suffix}` });
    const move = await request.patch(`/work-orders/${b.id}`, {
      data: { status: 'in_progress' },
    });
    expect(move.status()).toBe(200);

    const filtered = await request.get(`/work-orders?status=in_progress&aircraft_id=${aircraft.id}`);
    expect(filtered.status()).toBe(200);
    const body = await filtered.json();
    const ids = body.map((wo: { id: number }) => wo.id);
    expect(ids).toContain(b.id);
    expect(ids).not.toContain(a.id);
  });

  test('GET /work-orders/{id} nests aircraft', async ({ request }) => {
    const aircraft = await createAircraft(request);
    const wo = await createWorkOrder(request, aircraft.id);
    const resp = await request.get(`/work-orders/${wo.id}`);
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.aircraft).toBeTruthy();
    expect(body.aircraft.id).toBe(aircraft.id);
    expect(body.aircraft.tail_number).toBe(aircraft.tail_number);
  });

  test('PATCH valid status transition open -> in_progress', async ({ request }) => {
    const aircraft = await createAircraft(request);
    const wo = await createWorkOrder(request, aircraft.id);
    const resp = await request.patch(`/work-orders/${wo.id}`, {
      data: { status: 'in_progress' },
    });
    expect(resp.status()).toBe(200);
    expect((await resp.json()).status).toBe('in_progress');
  });

  test('PATCH invalid status transition complete -> open returns 422', async ({ request }) => {
    const aircraft = await createAircraft(request);
    const wo = await createWorkOrder(request, aircraft.id);
    await request.patch(`/work-orders/${wo.id}`, { data: { status: 'in_progress' } });
    await request.patch(`/work-orders/${wo.id}`, { data: { status: 'complete' } });
    const bad = await request.patch(`/work-orders/${wo.id}`, { data: { status: 'open' } });
    expect(bad.status()).toBe(422);
    const body = await bad.json();
    expect(JSON.stringify(body)).toContain('Invalid status transition');
  });

  test('PATCH updates priority', async ({ request }) => {
    const aircraft = await createAircraft(request);
    const wo = await createWorkOrder(request, aircraft.id);
    const resp = await request.patch(`/work-orders/${wo.id}`, {
      data: { priority: 'critical' },
    });
    expect(resp.status()).toBe(200);
    expect((await resp.json()).priority).toBe('critical');
  });

  test('DELETE removes work order', async ({ request }) => {
    const aircraft = await createAircraft(request);
    const wo = await createWorkOrder(request, aircraft.id);
    const del = await request.delete(`/work-orders/${wo.id}`);
    expect(del.status()).toBe(204);
    const followup = await request.get(`/work-orders/${wo.id}`);
    expect(followup.status()).toBe(404);
  });
});
