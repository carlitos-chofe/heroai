#### 1. Copia .env.example a .env y completa las claves:
```
GOOGLE_API_KEY=tu-clave
CLERK_SECRET_KEY=sk_live_xxx
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_xxx
```

#### 2. Levanta todos los servicios:

`docker-compose up --build`

#### 3. Aplica las migraciones (primera vez):

`docker exec hero-api alembic upgrade head`

#### 4. Abre http://localhost:3000 