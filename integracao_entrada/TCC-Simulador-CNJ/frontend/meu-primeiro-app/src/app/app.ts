import { Component, signal } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, CommonModule],
  template: `
    <nav class="nav-global" [class.dark]="darkMode()">
      <div class="nav-marca">
        <img src="iesb-logonowcollege.png" alt="IESB" class="nav-logo" />
      </div>
      <div class="nav-links">
        <a routerLink="/"
           routerLinkActive="ativo"
           [routerLinkActiveOptions]="{ exact: true }"
           class="nav-link">
          🤖 Assistente
        </a>
        <a routerLink="/simulador"
           routerLinkActive="ativo"
           class="nav-link">
          📊 Simulador de Metas
        </a>
        <button class="btn-tema" (click)="toggleDark()" [title]="darkMode() ? 'Modo claro' : 'Modo escuro'">
          {{ darkMode() ? '☀️' : '🌙' }}
        </button>
      </div>
    </nav>

  <div class="conteudo" [class.dark]="darkMode()">
  <router-outlet />
</div>
  `,
  styles: [`
.nav-global {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #ffffff;
  border-bottom: 1px solid #E5E7EB;
  padding: 0 24px;
  height: 70px;        /* ← aumentado de 52px para 70px */
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 4px rgba(0,0,0,.08);
}

  .nav-marca {
    display: flex;
    align-items: center;
  }
  
.nav-logo {
  height: 54px;        /* ← aumentado de 38px para 54px */
  width: auto;
  object-fit: contain;
}

  .nav-links {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .nav-link {
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 500;
    color: #4A4E57;
    text-decoration: none;
    border-radius: 6px;
    transition: background .15s, color .15s;
  }

  .nav-link:hover {
    background: #F3F4F6;
    color: #1a1a2e;
  }

  .nav-link.ativo {
    background: #185FA5;
    color: #fff;
  }

  .btn-tema {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 1px solid #E5E7EB;
    background: #F9FAFB;
    font-size: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: 6px;
    transition: transform .2s;
  }

  .btn-tema:hover { transform: scale(1.1); }

  .conteudo {
  min-height: calc(100vh - 52px);
  background: #ffffff;
  transition: background .3s;
}

.conteudo.dark {
  background: #0f0f1e;
}
`]
})
export class AppComponent {
  darkMode = signal(false);

  toggleDark() {
    this.darkMode.update(v => !v);
    // Propaga o tema para o body para o simulador usar
    document.body.classList.toggle('tema-dark', this.darkMode());
  }
}