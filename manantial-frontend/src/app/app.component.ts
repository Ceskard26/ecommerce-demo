import { Component } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { CartService } from './services/cart.service';
import { map } from 'rxjs';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, CommonModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'Manantial E-commerce';
  cartCount$;

  constructor(private cartService: CartService) {
    this.cartCount$ = this.cartService.items$.pipe(
      map((items) => items.reduce((sum, i) => sum + i.quantity, 0))
    );
  }
}
