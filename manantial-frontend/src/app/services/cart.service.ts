import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Product } from '../models/product.model';

export interface CartItem {
  product: Product;
  quantity: number;
}

@Injectable({
  providedIn: 'root',
})
export class CartService {
  private apiUrl = environment.apiUrl;
  private itemsSubject = new BehaviorSubject<CartItem[]>([]);
  items$: Observable<CartItem[]> = this.itemsSubject.asObservable();

  constructor(private http: HttpClient) {}

  private get currentItems(): CartItem[] {
    return this.itemsSubject.value;
  }

  addToCart(product: Product): void {
    const items = [...this.currentItems];
    const existing = items.find((i) => i.product.id === product.id);

    if (existing) {
      existing.quantity += 1;
    } else {
      items.push({ product, quantity: 1 });
    }
    this.itemsSubject.next(items);
  }

  removeFromCart(productId: number): void {
    const items = this.currentItems.filter((i) => i.product.id !== productId);
    this.itemsSubject.next(items);
  }

  updateQuantity(productId: number, quantity: number): void {
    const items = this.currentItems.map((i) =>
      i.product.id === productId ? { ...i, quantity } : i
    );
    this.itemsSubject.next(items);
  }

  getTotal(): number {
    return this.currentItems.reduce(
      (sum, i) => sum + i.product.price * i.quantity,
      0
    );
  }

  clearCart(): void {
    this.itemsSubject.next([]);
  }

  checkout(): Observable<any> {
    const payload = {
      items: this.currentItems.map((i) => ({
        product_id: i.product.id,
        quantity: i.quantity,
      })),
    };
    return this.http.post(`${this.apiUrl}/checkout`, payload);
  }
}
