import { test, expect, APIRequestContext } from '@playwright/test';

let suffix: string;

test.beforeEach(() => {
  suffix = `${Date.now()}-${Math.floor(Math.random() * 10_000)}`;
});

async function createAircraft(
  request: APIRequestContext,
  overrides: Record<string, unknown> = {}
) {
  const payload = {
    tail_number: `AC-${suffix}`,
    model: 'F-35A Lightning II',
    squadron: '388 FW',
    status: 'operational',
    ...overrides,
  };
  const resp = await request.post('/aircraft', { data: payload });
  expect(resp.status(), await resp.text()).toBe(201);
  return resp.json();
}

test.describe('Aircraft API', () => {
  test('GET /health returns healthy', async ({ request }) => {
    const resp = await request.get('/health');
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.status).toBe('healthy');
  });

  test('POST /aircraft creates an aircraft', async ({ request }) => {
    const body = await createAircraft(request);
    expect(body.id).toBeGreaterThan(0);
    expect(body.tail_number).toBe(`AC-${suffix}`);
    expect(body.model).toBe('F-35A Lightning II');
    expect(body.status).toBe('operational');
    expect(body.created_at).toBeTruthy();
  });

  test('GET /aircraft returns an array', async ({ request }) => {
    await createAircraft(request);
    const resp = await request.get('/aircraft');
    expect(resp.status()).toBe(200);
    expect(Array.isArray(await resp.json())).toBe(true);
  });

  test('GET /aircraft?status filters by status', async ({ request }) => {
    const op = await createAircraft(request, {
      tail_number: `OP-${suffix}`,
      status: 'operational',
    });
    const gr = await createAircraft(request, {
      tail_number: `GR-${suffix}`,
      status: 'grounded',
    });
    const resp = await request.get('/aircraft?status=grounded');
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    const ids = body.map((a: { id: number }) => a.id);
    expect(ids).toContain(gr.id);
    expect(ids).not.toContain(op.id);
  });

  test('GET /aircraft/{id} returns matching record', async ({ request }) => {
    const created = await createAircraft(request);
    const resp = await request.get(`/aircraft/${created.id}`);
    expect(resp.status()).toBe(200);
    const fetched = await resp.json();
    expect(fetched.id).toBe(created.id);
    expect(fetched.tail_number).toBe(created.tail_number);
  });

  test('GET /aircraft/{id} returns 404 when missing', async ({ request }) => {
    const resp = await request.get('/aircraft/999999');
    expect(resp.status()).toBe(404);
  });

  test('PATCH /aircraft/{id} updates status', async ({ request }) => {
    const created = await createAircraft(request);
    const resp = await request.patch(`/aircraft/${created.id}`, {
      data: { status: 'maintenance' },
    });
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.status).toBe('maintenance');
  });

  test('POST /aircraft with duplicate tail_number returns 409', async ({ request }) => {
    await createAircraft(request, { tail_number: `DUP-${suffix}` });
    const dup = await request.post('/aircraft', {
      data: {
        tail_number: `DUP-${suffix}`,
        model: 'F-16C',
        squadron: 'Test',
      },
    });
    expect(dup.status()).toBe(409);
  });
});
