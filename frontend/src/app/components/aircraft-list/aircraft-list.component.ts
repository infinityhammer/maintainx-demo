import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';

import { Aircraft } from '../../models/aircraft';
import { AircraftService } from '../../services/aircraft.service';

@Component({
  selector: 'app-aircraft-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './aircraft-list.component.html',
  styleUrl: './aircraft-list.component.scss',
})
export class AircraftListComponent implements OnInit {
  private readonly aircraftService = inject(AircraftService);

  readonly aircraft = signal<Aircraft[]>([]);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.aircraftService.getAll().subscribe({
      next: (rows) => {
        this.aircraft.set(rows);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err?.message ?? 'Failed to load aircraft');
        this.loading.set(false);
      },
    });
  }
}
