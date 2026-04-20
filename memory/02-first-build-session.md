# 02 — First Build Session

**Fecha:** 2026-04-20
**Estado al inicio:** Solo archivos de especificación, sin código implementado.
**Estado al final:** MVP completo implementado desde cero. 71 archivos, ~4800 líneas de código. Commit: `e0b1966`.

---

## Decisiones tomadas en esta sesión

| Decisión | Valor elegido | Alternativas descartadas |
|---|---|---|
| UI styling | CSS Modules básico | Tailwind, Shadcn/ui |
| Package manager web | npm | pnpm, yarn |
| Versión Next.js | 15.3.1 (latest compatible) | 16 (aún no existe) |
| ORM | SQLModel (combina SQLAlchemy + Pydantic v2) | SQLAlchemy puro |
| Retry policy | `tenacity` (backoff exponencial, max 3) | Celery native retries |
| Clerk token decode | `pyjwt` sin verificación de firma (MVP) | JWKS fetch + RS256 verify |
| Claves al inicio | Todas vacías (placeholder) | N/A |

---

## Estructura implementada

```
hero-ai/
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── main.py                    FastAPI app, CORS, static files, lifespan
│   │   │   ├── api/routes/
│   │   │   │   ├── health.py              GET /health
│   │   │   │   ├── profiles.py            GET/POST /profiles, PATCH /profiles/{id}
│   │   │   │   └── stories.py             Todos los endpoints de stories + feedback
│   │   │   ├── core/
│   │   │   │   ├── config.py              Settings (pydantic-settings), variables de entorno
│   │   │   │   └── auth.py                JWT Clerk decode + provisión lazy de User
│   │   │   ├── db/
│   │   │   │   ├── session.py             Engine + get_session dependency
│   │   │   │   └── base.py                Import de todos los modelos para Alembic
│   │   │   ├── models/
│   │   │   │   ├── user.py                Tabla users (clerk_id único)
│   │   │   │   ├── child_profile.py       Tabla child_profiles (JSONB avatar + preferences)
│   │   │   │   ├── story.py               Tabla stories (7 estados, 3 idiomas)
│   │   │   │   ├── story_panel.py         Tabla story_panels (order 1-5, image_url nullable)
│   │   │   │   └── story_feedback.py      Tabla story_feedback (love/funny/scary)
│   │   │   ├── schemas/
│   │   │   │   ├── profile.py             ProfileCreate, ProfileUpdate, ProfileResponse
│   │   │   │   └── story.py               StoryCreate, StoryDetail, StoryStatus, FeedbackCreate, etc.
│   │   │   ├── services/
│   │   │   │   ├── profile_service.py     CRUD perfiles con validación de ownership
│   │   │   │   ├── story_service.py       CRUD historias + validaciones de estado
│   │   │   │   └── feedback_service.py    Registro feedback + recálculo preference_summary
│   │   │   └── workers/
│   │   │       ├── celery_app.py          Celery configurado con Redis broker/backend
│   │   │       ├── script_worker.py       generate_story_script (Gemini 2.5 Pro, 2 pasadas)
│   │   │       └── image_worker.py        generate_story_images (Gemini Flash Image)
│   │   ├── alembic/
│   │   │   ├── env.py                     Lee DATABASE_URL de entorno
│   │   │   └── versions/0001_initial.py   Schema completo con constraints y índices
│   │   ├── alembic.ini
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   └── web/
│       ├── app/
│       │   ├── layout.tsx                 ClerkProvider + CSS global
│       │   ├── page.tsx                   Redirect → /dashboard
│       │   ├── sign-in/page.tsx           SignIn de Clerk
│       │   ├── dashboard/page.tsx         Perfiles + Biblioteca Mágica
│       │   ├── profiles/
│       │   │   ├── new/page.tsx           Formulario + AvatarBuilder
│       │   │   └── [profileId]/edit/page.tsx  Edición pre-cargada
│       │   └── stories/
│       │       ├── new/page.tsx           Selector perfil + textarea + idioma
│       │       └── [storyId]/
│       │           ├── script/page.tsx    Revisión guion + botón Aprobar
│       │           ├── progress/page.tsx  Polling cada 4s con barra de progreso
│       │           └── read/page.tsx      Lector full-screen (imagen 65% / texto 35%)
│       ├── components/
│       │   ├── ProfileCard.tsx            Tarjeta de perfil con avatar emoji y acciones
│       │   ├── StoryCard.tsx              Tarjeta de historia con estado y link contextual
│       │   ├── AvatarBuilder.tsx          5 selectores: hair, hair_color, eye_color, skin, clothing
│       │   └── ReactionBar.tsx            3 botones de reacción (love/funny/scary) → POST feedback
│       ├── lib/api.ts                     Fetch wrapper tipado hacia FastAPI
│       ├── middleware.ts                  Clerk auth middleware (rutas protegidas)
│       ├── styles/globals.css             Variables CSS, reset, paleta de colores
│       ├── next.config.ts
│       ├── package.json
│       └── Dockerfile
├── storage/stories/                       Volumen compartido api + worker (en .gitignore)
├── docker-compose.yml                     5 servicios: web, api, worker, redis, postgres
├── .env.example                           Variables mínimas sin valores secretos
└── .gitignore
```

---

## Flujo completo implementado

```
Tutor → /sign-in → Clerk auth
      → /dashboard → lista perfiles + historias
      → /profiles/new → crea perfil (name, age, interests, avatar)
      → /stories/new → elige perfil + pega texto + elige idioma
                     → POST /api/v1/stories → story status=pending
                     → Celery: generate_story_script
                       1. status → scripting
                       2. Gemini 2.5 Pro: genera JSON 5 paneles
                       3. Segunda pasada: validación lingüística
                       4. Persiste story_panels
                       5. status → script_ready
      → /stories/{id}/progress → polling cada 4s
      → /stories/{id}/script → revisa guion (5 paneles con narrativa + diálogo)
                             → botón Aprobar → POST /approve
                             → Celery: generate_story_images
                               1. status → generating_images
                               2. Gemini Flash Image x5 (NO TEXT, NO SPEECH BUBBLES)
                               3. Guarda en storage/stories/{id}/panel-{n}.png
                               4. Actualiza image_url en story_panels
                               5. status → completed
      → /stories/{id}/read → lector full-screen
                            → imagen limpia (65% alto)
                            → narrative_text + dialogue desde DB (35% alto)
                            → navegación anterior/siguiente
                            → reacciones por panel → POST /feedback
                            → recálculo preference_summary del perfil
```

---

## Contratos REST implementados

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Health check (sin auth) |
| GET | `/api/v1/profiles` | Lista perfiles del tutor |
| POST | `/api/v1/profiles` | Crea perfil (age 4-12 validado) |
| PATCH | `/api/v1/profiles/{id}` | Actualiza perfil parcialmente |
| POST | `/api/v1/stories` | Crea historia + encola script |
| GET | `/api/v1/stories` | Lista historias (filtros: profile_id, status) |
| GET | `/api/v1/stories/{id}` | Detalle historia + paneles |
| GET | `/api/v1/stories/{id}/status` | Estado + paneles generados |
| GET | `/api/v1/stories/{id}/script` | Guion (solo en script_ready/approved/completed) |
| POST | `/api/v1/stories/{id}/approve` | Aprueba guion + encola imágenes |
| POST | `/api/v1/stories/{id}/feedback` | Registra reacción + recalcula preferencias |

---

## Detalles técnicos relevantes para futuras sesiones

### Autenticación Clerk (apps/api/app/core/auth.py)
- Usa `pyjwt` con `verify_signature=False` en el MVP.
- Provisión lazy: si `clerk_id` no existe en `users`, se crea en el primer request.
- Con `CLERK_SECRET_KEY` vacío: lanza 401 con mensaje descriptivo.
- **Mejora pendiente para producción**: verificar firma RS256 con JWKS de Clerk.

### Workers (apps/api/app/workers/)
- `script_worker.py`: dos llamadas a Gemini 2.5 Pro. Primera genera el guion JSON, segunda valida y corrige ortografía/idioma/edad. Hasta 2 reintentos de validación antes de usar el guion original.
- `image_worker.py`: una llamada a Gemini Flash Image por panel. El prompt incluye descripción de avatar fijo + escena + `NO TEXT. NO LETTERING. NO SPEECH BUBBLES. NO CAPTIONS. NO WORDS IN IMAGE.`
- Ambos usan `tenacity` con backoff exponencial (min=2s, max=10s para texto; min=4s, max=30s para imágenes).
- En fallo de cualquier panel de imagen: toda la historia queda en `failed`.

### Preference Summary (apps/api/app/services/feedback_service.py)
- Heurística simple sin embeddings ni ML.
- `likes` = ["fun adventures", "friendly characters"] si hay reacciones love/funny.
- `avoid` = ["scary scenes", "dark themes"] si hay más de 2 reacciones scary.
- `last_reactions` = últimas 10 reacciones (se inyectan en el prompt de scripting).

### Lector (/stories/[storyId]/read)
- Layout CSS puro: `flex-direction: column` en mobile/tablet, `flex-direction: row` en desktop (≥1024px).
- Imagen: `object-fit: contain` sobre fondo oscuro (#0f0818).
- Texto proviene exclusivamente de `narrative_text` y `dialogue` en DB.
- `ReactionBar` es stateful: una vez enviada la reacción, los botones se desactivan.

### Asset serving
- FastAPI monta `/assets` → `LOCAL_ASSET_DIR` con `StaticFiles`.
- Ruta pública: `/assets/stories/{story_id}/panel-{n}.png`
- Volumen Docker `story_assets` compartido entre `hero-api` y `hero-worker`.

---

## Comandos para levantar el proyecto

```bash
# 1. Copiar y completar variables de entorno
cp .env.example .env
# Editar .env con GOOGLE_API_KEY, CLERK_SECRET_KEY, NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY

# 2. Levantar todos los servicios
docker-compose up --build

# 3. Primera vez: aplicar migraciones
docker exec hero-api alembic upgrade head

# 4. Abrir la app
open http://localhost:3000

# Puertos expuestos:
# 3000 → web (Next.js)
# 8000 → api (FastAPI)
# 5432 → postgres (desarrollo local)
# 6379 → redis (desarrollo local)
```

---

## Dependencias principales

### Backend (pyproject.toml)
```
fastapi, uvicorn[standard], sqlmodel, alembic, psycopg[binary],
pydantic>=2, pydantic-settings, celery, redis, google-generativeai,
tenacity, httpx, python-jose[cryptography], pyjwt, cryptography, Pillow
```

### Frontend (package.json)
```
next@15.3.1, react@19, react-dom@19, @clerk/nextjs@6
```

---

## Pendientes / mejoras identificadas

1. **Verificación de firma JWT Clerk**: actualmente el MVP decodifica sin verificar firma. Para producción, implementar JWKS fetch y verificación RS256.
2. **Modelo de imagen**: el identificador `gemini-2.5-flash-preview-image-generation` puede cambiar. Verificar con Google AI Studio el nombre oficial vigente antes del primer deploy.
3. **Validación lingüística más robusta**: la segunda pasada usa el mismo modelo. Se podría agregar validación determinista de longitud de frases por edad.
4. **Rate limiting**: no implementado en el MVP. Agregar si se abre a múltiples tutores.
5. **WebSockets**: fuera de alcance del MVP. El polling cada 4s es el mecanismo actual.
6. **Tests**: no hay tests unitarios ni de integración. Agregar pytest para el backend como siguiente paso.
7. **Error handling en frontend**: los errores de red muestran mensajes genéricos. Mejorar con códigos específicos del backend.
