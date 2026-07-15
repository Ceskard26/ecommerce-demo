# Manantial E-commerce — Frontend (Angular 18)

## Desarrollo local

```bash
npm install
npm start          # http://localhost:4200
```

Asegúrate de que el backend Flask esté corriendo en `http://localhost:8000`
(ver `src/environments/environment.ts`), o edítalo si usas otro puerto.

## Antes de desplegar a Amplify

Edita `src/environments/environment.prod.ts` y reemplaza `apiUrl` con el DNS real
de tu Load Balancer de Elastic Beanstalk:

```ts
apiUrl: 'http://manantial-ecommerce-env.us-east-1.elasticbeanstalk.com/api'
```

## Desplegar en AWS Amplify

1. Sube este proyecto a un repo de GitHub (`git init`, `git add .`, `git commit`, `git push`).
2. Amplify Console → **Create new app → Host web app** → conecta el repo → selecciona la rama.
3. Amplify detecta Angular automáticamente y genera el build. Si necesitas ajustarlo,
   el `amplify.yml` de referencia es:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build -- --configuration production
  artifacts:
    baseDirectory: dist/manantial-ecommerce-frontend/browser
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

4. Después del primer deploy, actualiza `FRONTEND_ORIGIN` en las Environment Properties
   de Beanstalk con la URL real que te dé Amplify (`https://main.xxxxx.amplifyapp.com`),
   para que CORS deje pasar las peticiones del frontend al backend.
