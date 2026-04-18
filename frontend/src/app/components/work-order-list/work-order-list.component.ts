import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { Router } from '@angular/router';

import { WorkOrder } from '../../models/work-order';
import { WorkOrderService } from '../../services/work-order.service';
import { WorkOrderFormComponent } from '../work-order-form/work-order-form.component';

@Component({
  selector: 'app-work-order-list',
  standalone: true,
  imports: [CommonModule, WorkOrderFormComponent],
  templateUrl: './work-order-list.component.html',
  styleUrl: './work-order-list.component.scss',
})
export class WorkOrderListComponent implements OnInit {
  private readonly workOrders = inject(WorkOrderService);
  private readonly router = inject(Router);

  readonly orders = signal<WorkOrder[]>([]);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);
  readonly showForm = signal(false);

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.workOrders.getAll().subscribe({
      next: (rows) => {
        this.orders.set(rows);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err?.message ?? 'Failed to load work orders');
        this.loading.set(false);
      },
    });
  }

  open(id: number): void {
    this.router.navigate(['/work-orders', id]);
  }

  toggleForm(): void {
    this.showForm.update((v) => !v);
  }

  onCreated(): void {
    this.showForm.set(false);
    this.load();
  }
}
