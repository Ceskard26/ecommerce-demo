# Manantial E-commerce — Backend (Flask)

Monolito Python que corre en Elastic Beanstalk (plataforma Python, Amazon Linux 2023),
conectado a RDS MySQL.

## Desarrollo local

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # edita con tus credenciales de MySQL local
export $(cat .env | xargs)      # Windows: usa un paquete como python-dotenv, o setea manualmente

flask --app application init-db     # crea las tablas
flask --app application seed-db     # inserta productos de ejemplo

python application.py           # levanta en http://localhost:8000
```

Prueba: `curl http://localhost:8000/api/health` debe responder `{"status": "ok"}`.

## Despliegue en Elastic Beanstalk

1. Zip el contenido de esta carpeta (no la carpeta en sí, su contenido):
   ```bash
   zip -r ../manantial-backend.zip . -x "venv/*" -x "__pycache__/*" -x ".env"
   ```
2. Elastic Beanstalk Console → tu environment → **Upload and deploy** → sube el `.zip`.
3. En **Configuration → Software → Environment properties**, agrega:
   - `DB_HOST` → endpoint de tu instancia RDS
   - `DB_PORT` → 3306
   - `DB_NAME` → manantial_ecommerce
   - `DB_USER` / `DB_PASSWORD` → según el secreto de Secrets Manager (o referencia el ARN si tu instance profile tiene permiso `secretsmanager:GetSecretValue`)
   - `FRONTEND_ORIGIN` → la URL real de Amplify una vez desplegada

4. Después del primer deploy exitoso, corre las migraciones iniciales una sola vez
   (vía SSH/Session Manager a una instancia, o localmente apuntando al endpoint de RDS
   a través del túnel VPN si ya está armado):
   ```bash
   flask --app application init-db
   flask --app application seed-db
   ```

## Endpoints

| Método | Ruta                    | Descripción                          |
|--------|-------------------------|---------------------------------------|
| GET    | /api/health             | Health check (usado por el ALB)       |
| GET    | /api/products           | Lista todos los productos             |
| GET    | /api/products/<id>      | Detalle de un producto                |
| POST   | /api/checkout           | Crea una orden y descuenta stock      |
| GET    | /api/orders/<id>        | Consulta una orden                    |

**Nota de seguridad:** este endpoint de checkout no procesa pagos. En un e-commerce
real, el frontend debe integrar un procesador de pagos externo (Stripe/Culqi/Niubiz)
*antes* de llamar a `/api/checkout`, para no manejar datos de tarjeta en tu propia
infraestructura (evita alcance PCI-DSS).
