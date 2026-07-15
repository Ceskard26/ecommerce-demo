"""
Manantial E-commerce - Backend monolito en Python (Flask)
Diseñado para desplegarse en AWS Elastic Beanstalk (plataforma Python)
Base de datos: RDS MySQL (variables de entorno via Beanstalk Environment Properties)
"""
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

# ----------------------------------------------------------------------------
# Configuración
# ----------------------------------------------------------------------------
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ.get("DB_NAME", "manantial_ecommerce")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

# Origen permitido para CORS: la URL de Amplify del frontend.
# En producción, reemplaza "*" por el dominio real (ej. https://main.xxxxx.amplifyapp.com)
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "*")

application = Flask(__name__)
CORS(application, resources={r"/api/*": {"origins": FRONTEND_ORIGIN}})

application.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(application)


# ----------------------------------------------------------------------------
# Modelos
# ----------------------------------------------------------------------------
class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(300), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price),
            "stock": self.stock,
            "image_url": self.image_url,
        }


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status = db.Column(db.String(30), nullable=False, default="pending")

    items = db.relationship("OrderItem", backref="order", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "total": float(self.total),
            "status": self.status,
            "items": [item.to_dict() for item in self.items],
        }


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price),
        }


# ----------------------------------------------------------------------------
# Rutas
# ----------------------------------------------------------------------------
@application.get("/api/health")
def health():
    """Usado por el health check del ALB de Elastic Beanstalk."""
    return jsonify({"status": "ok"}), 200


@application.get("/api/products")
def list_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products]), 200


@application.get("/api/products/<int:product_id>")
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200


@application.post("/api/checkout")
def checkout():
    """
    Espera: { "items": [ { "product_id": 1, "quantity": 2 }, ... ] }
    No procesa pagos reales: eso lo delega un procesador externo (Stripe/Culqi/Niubiz)
    del lado del frontend. Este endpoint solo registra la orden y descuenta stock.
    """
    payload = request.get_json(force=True, silent=True) or {}
    items = payload.get("items", [])

    if not items:
        return jsonify({"error": "El carrito está vacío"}), 400

    order = Order(total=0, status="pending")
    db.session.add(order)

    total = 0
    for item in items:
        product = Product.query.get(item.get("product_id"))
        quantity = int(item.get("quantity", 0))

        if not product or quantity <= 0:
            db.session.rollback()
            return jsonify({"error": f"Producto inválido: {item}"}), 400

        if product.stock < quantity:
            db.session.rollback()
            return jsonify({"error": f"Stock insuficiente para {product.name}"}), 409

        product.stock -= quantity
        subtotal = float(product.price) * quantity
        total += subtotal

        order_item = OrderItem(
            order=order,
            product_id=product.id,
            quantity=quantity,
            unit_price=product.price,
        )
        db.session.add(order_item)

    order.total = total
    order.status = "confirmed"
    db.session.commit()

    return jsonify(order.to_dict()), 201


@application.get("/api/orders/<int:order_id>")
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict()), 200


# ----------------------------------------------------------------------------
# Inicialización de tablas (solo para desarrollo/demo; en producción usa
# migraciones con Alembic en vez de create_all)
# ----------------------------------------------------------------------------
@application.cli.command("init-db")
def init_db():
    db.create_all()
    print("Tablas creadas.")


@application.cli.command("seed-db")
def seed_db():
    sample_products = [
        Product(name="Camiseta básica", description="100% algodón", price=39.90, stock=50,
                image_url="/products/polo.png"),
        Product(name="Zapatos tácticos", description="Ligeras y cómodas", price=189.90, stock=20,
                image_url="/products/zapatillas.png"),
        Product(name="Mochila de viaje", description="35L, resistente al agua", price=129.00, stock=15,
                image_url="/products/mochila.png"),
        Product(name="Capacitación técnica con Javier", description="worth it", price=999.00, stock=1,
                image_url="/products/capacitacion.png"),
    ]
    db.session.bulk_save_objects(sample_products)
    db.session.commit()
    print(f"{len(sample_products)} productos insertados.")


if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0", port=8000)
