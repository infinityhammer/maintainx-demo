import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { WorkOrder, WorkOrderStatus } from '../../models/work-order';
import { WorkOrderService } from '../../services/work-order.service';

const NEXT_STATUSES: Record<WorkOrderStatus, WorkOrderStatus[]> = {
  open: ['in_progress', 'cancelled'],
  in_progress: ['awaiting_parts', 'complete', 'cancelled'],
  awaiting_parts: ['in_progress', 'complete', 'cancelled'],
  complete: [],
  cancelled: [],
};

@Component({
  selector: 'app-work-order-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './work-order-detail.component.html',
  styleUrl: './work-order-detail.component.scss',
})
export class WorkOrderDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly workOrders = inject(WorkOrderService);

  readonly workOrder = signal<WorkOrder | null>(null);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);

  assignee = '';

  readonly nextStatuses = computed<WorkOrderStatus[]>(() => {
    const wo = this.workOrder();
    return wo ? NEXT_STATUSES[wo.status] : [];
  });

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (Number.isFinite(id)) {
      this.load(id);
    }
  }

  private load(id: number): void {
    this.loading.set(true);
    this.error.set(null);
    this.workOrders.getById(id).subscribe({
      next: (wo) => {
        this.workOrder.set(wo);
        this.assignee = wo.assigned_to ?? '';
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err?.error?.detail ?? err?.message ?? 'Failed to load');
        this.loading.set(false);
      },
    });
  }

  transition(status: WorkOrderStatus): void {
    const wo = this.workOrder();
    if (!wo) return;
    this.workOrders.update(wo.id, { status }).subscribe({
      next: (updated) => this.workOrder.set(updated),
      error: (err) => this.error.set(err?.error?.detail ?? err?.message ?? 'Update failed'),
    });
  }

  saveAssignee(): void {
    const wo = this.workOrder();
    if (!wo) return;
    this.workOrders.update(wo.id, { assigned_to: this.assignee || undefined }).subscribe({
      next: (updated) => this.workOrder.set(updated),
      error: (err) => this.error.set(err?.error?.detail ?? err?.message ?? 'Update failed'),
    });
  }
}
