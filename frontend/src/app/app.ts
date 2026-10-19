import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { ApiHealthService } from './core/services/api-health';

type ServiceStatus = 'verificando' | 'disponivel' | 'indisponivel';

@Component({
  selector: 'app-root',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  private readonly health = inject(ApiHealthService);
  readonly processualStatus = signal<ServiceStatus>('verificando');
  readonly simulatorStatus = signal<ServiceStatus>('verificando');

  ngOnInit(): void {
    this.health.checkProcessual().subscribe({
      next: () => this.processualStatus.set('disponivel'),
      error: () => this.processualStatus.set('indisponivel'),
    });
    this.health.checkSimulator().subscribe({
      next: () => this.simulatorStatus.set('disponivel'),
      error: () => this.simulatorStatus.set('indisponivel'),
    });
  }
}
