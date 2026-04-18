import { test, expect, APIRequestContext } from '@playwright/test';

const PERF_BUDGET_MS = 2000;

async function timed<T>(label: string, fn: () => Promise<T>): Promise<T> {
  const start = performance.now();
  const result = await fn();
  const elapsed = performance.now() - start;
  expect(
    elapsed,
    `${label} should complete in < ${PERF_BUDGET_MS}ms (took ${elapsed.toFixed(1)}ms)`,
  ).toBeLessThan(PERF_BUDGET_MS);
  return result;
}

test('full maintenance lifecycle via HTTP', async ({ request }) => {
  const suffix = `${Date.now()}-${Math.floor(Math.random() * 10_000)}`;

  const ac = await timed('create aircraft', () =>
    request.post('/aircraft', {
      data: {
        tail_number: `LC-${suffix}`,
        model: 'F-35A Lightning II',
        squadron: '388 FW',
      },
    }),
  );
  expect(ac.status()).toBe(201);
  const aircraft = await ac.json();

  const wo = await timed('create work order', () =>
    request.post('/work-orders', {
      data: {
        aircraft_id: aircraft.id,
        title: 'Replace pitot tube',
        priority: 'high',
      },
    }),
  );
  expect(wo.status()).toBe(201);
  const workOrder = await wo.json();
  expect(workOrder.status).toBe('open');

  const assigned = await timed('assign + in_progress', () =>
    request.patch(`/work-orders/${workOrder.id}`, {
      data: { assigned_to: 'SrA Patel', status: 'in_progress' },
    }),
  );
  expect(assigned.status()).toBe(200);
  const assignedBody = await assigned.json();
  expect(assignedBody.assigned_to).toBe('SrA Patel');
  expect(assignedBody.status).toBe('in_progress');

  const completed = await timed('mark complete', () =>
    request.patch(`/work-orders/${workOrder.id}`, {
      data: { status: 'complete' },
    }),
  );
  expect(completed.status()).toBe(200);
  expect((await completed.json()).status).toBe('complete');

  const final = await timed('final fetch', () =>
    request.get(`/work-orders/${workOrder.id}`),
  );
  expect(final.status()).toBe(200);
  const finalBody = await final.json();
  expect(finalBody.status).toBe('complete');
  expect(finalBody.aircraft.id).toBe(aircraft.id);
});
