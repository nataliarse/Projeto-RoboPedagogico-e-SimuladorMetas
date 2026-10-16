import { Routes } from '@angular/router';
import { ChatComponent } from './features/chat/chat';
import { SimuladorShellComponent } from './features/simulador/simulador-shell.component';

export const routes: Routes = [
  { path: '', component: ChatComponent },
  { path: 'simulador', component: SimuladorShellComponent },
  { path: '**', redirectTo: '' }
];
