export type AircraftStatus = 'operational' | 'grounded' | 'maintenance';

export interface Aircraft {
  id: number;
  tail_number: string;
  model: string;
  squadron: string;
  status: AircraftStatus;
  created_at: string;
}
