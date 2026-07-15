import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CartItem, CartService } from '../../services/cart.service';

@Component({
  selector: 'app-cart',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './cart.component.html',
  styleUrl: './cart.component.css',
})
export class CartComponent {
  items$;
  checkingOut = false;
  orderConfirmation: any = null;
  error: string | null = null;

  constructor(private cartService: CartService) {
    this.items$ = this.cartService.items$;
  }

  getTotal(): number {
    return this.cartService.getTotal();
  }

  remove(productId: number): void {
    this.cartService.removeFromCart(productId);
  }

  updateQuantity(productId: number, event: Event): void {
    const value = Number((event.target as HTMLInputElement).value);
    if (value > 0) {
      this.cartService.updateQuantity(productId, value);
    }
  }

  checkout(): void {
    this.checkingOut = true;
    this.error = null;

    this.cartService.checkout().subscribe({
      next: (order) => {
        this.orderConfirmation = order;
        this.cartService.clearCart();
        this.checkingOut = false;
      },
      error: (err) => {
        this.error =
          err?.error?.error || 'No se pudo completar la orden. Intenta de nuevo.';
        this.checkingOut = false;
      },
    });
  }
}
