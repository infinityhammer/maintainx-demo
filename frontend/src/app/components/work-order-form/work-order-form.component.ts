import { CommonModule } from '@angular/common';
import { Component, EventEmitter, OnInit, Output, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { Aircraft } from '../../models/aircraft';
import { WorkOrderPriority } from '../../models/work-order';
import { AircraftService } from '../../services/aircraft.service';
import { WorkOrderService } from '../../services/work-order.service';

@Component({
  selector: 'app-work-order-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './work-order-form.component.html',
  styleUrl: './work-order-form.component.scss',
})
export class WorkOrderFormComponent implements OnInit {
  private readonly aircraftService = inject(AircraftService);
  private readonly workOrders = inject(WorkOrderService);

  @Output() created = new EventEmitter<void>();

  readonly aircraft = signal<Aircraft[]>([]);
  readonly submitting = signal(false);
  readonly error = signal<string | null>(null);

  title = '';
  aircraftId: number | null = null;
  priority: WorkOrderPriority = 'normal';
  description = '';

  ngOnInit(): void {
    this.aircraftService.getAll().subscribe({
      next: (rows) => this.aircraft.set(rows),
      error: (err) => this.error.set(err?.message ?? 'Failed to load aircraft'),
    });
  }

  submit(): void {
    if (!this.title.trim() || this.aircraftId == null) {
      this.error.set('Title and aircraft are required');
      return;
    }
    this.submitting.set(true);
    this.error.set(null);
    this.workOrders
      .create({
        title: this.title.trim(),
        aircraft_id: this.aircraftId,
        priority: this.priority,
        description: this.description || undefined,
      })
      .subscribe({
        next: () => {
          this.submitting.set(false);
          this.created.emit();
        },
        error: (err) => {
          this.error.set(err?.error?.detail ?? err?.message ?? 'Create failed');
          this.submitting.set(false);
        },
      });
  }
}
