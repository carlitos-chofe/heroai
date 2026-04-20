# Hero Adventure AI - Especificación Final MVP Build-Ready v3

## 1. Propósito

Este documento define el MVP de `Hero Adventure AI` para implementación desde cero.

Debe poder entregarse a cualquier modelo de IA o equipo de ingeniería como fuente única de verdad para construir el producto sin depender del código Python actual del repositorio.

El código existente del prototipo no debe tomarse como referencia de arquitectura ni de implementación. Si contradice este documento, prevalece este documento.

## 2. Resultado Esperado del MVP

El MVP permite que un tutor:

1. Inicie sesión con Google o correo.
2. Cree uno o varios perfiles infantiles.
3. Defina nombre, edad, intereses y avatar de cada niño.
4. Pegue un texto educativo manualmente.
5. Solicite a la IA una previsualización de guion en 5 paneles.
6. Apruebe el guion.
7. Espere la generación asíncrona de las imágenes.
8. Lea el comic final en un lector tipo libro digital.
9. Vea el comic guardado en su Biblioteca Mágica.
10. Registre reacciones por página.
11. Reutilice implícitamente ese feedback en historias futuras del mismo perfil mediante una heurística simple.

## 3. Alcance del MVP

### 3.1 En alcance

1. Frontend web en Next.js.
2. Backend API en FastAPI.
3. Autenticación de tutor con Clerk.
4. Persistencia en PostgreSQL.
5. Redis y Celery para tareas asíncronas.
6. Creación y edición de perfiles infantiles.
7. Avatar sin fotos reales.
8. Ingreso manual de texto como única fuente de contenido.
9. Generación de guion estructurado de 5 paneles.
10. Aprobación de guion antes de generar imágenes.
11. Generación de una imagen por panel.
12. Almacenamiento local de imágenes en disco.
13. Biblioteca Mágica con historias en progreso y completadas.
14. Lector tipo libro digital para desktop y tablet.
15. Modo de salida `es`, `en` o `mixed_es_en`.
16. Feedback simple por página.
17. Resumen simple de preferencias del perfil a partir del feedback.

### 3.2 Fuera de alcance

1. Ingesta por URL.
2. Procesamiento de video o YouTube.
3. Fotos reales de menores.
4. Edición manual del guion.
5. Finales múltiples o historias interactivas complejas.
6. Audio, narración sintética o doblaje.
7. WebSockets.
8. Apps móviles nativas.
9. Sistema avanzado de personalización con memoria semántica.
10. Storage cloud para imágenes en esta etapa.

## 4. Decisiones Cerradas

1. El proyecto se implementa desde cero.
2. El MVP incluye frontend y backend.
3. Clerk es obligatorio para autenticación.
4. PostgreSQL es obligatorio para persistencia.
5. La fuente de contenido del MVP es solo texto manual.
6. Las imágenes se almacenan localmente en disco.
7. El tutor solo aprueba el guion; no lo edita.
8. La lectura bilingüe es opcional y se controla con `language_target`.
9. El sistema soporta múltiples perfiles por tutor.
10. El feedback sí alimenta una heurística simple para historias futuras.

## 5. Stack Tecnológico

### 5.1 Frontend

1. Next.js 16 App Router.
2. TypeScript.
3. Clerk.
4. Fetch server/client hacia FastAPI.
5. UI responsive para desktop y tablet.

### 5.2 Backend

1. Python 3.11 o superior.
2. FastAPI.
3. SQLAlchemy o SQLModel.
4. Alembic para migraciones.
5. Pydantic v2.

### 5.3 Procesamiento asíncrono

1. Celery.
2. Redis como broker.
3. Redis como backend de resultados si se considera útil para monitoreo interno.

### 5.4 Base de datos

1. PostgreSQL 16.

### 5.5 IA

1. Proveedor principal del MVP: Google.
2. Modelo de texto obligatorio del MVP: `Gemini 2.5 Pro`.
3. Modelo de imagen obligatorio del MVP: `Gemini 2.5 Flash Image (Nano Banana)`.
4. En implementación, se debe usar el identificador oficial vigente de Google equivalente a esos modelos.
5. El modelo de texto debe soportar salida JSON estructurada.
6. El modelo de imagen se usa solo para ilustración, nunca para texto legible dentro de la imagen.

## 6. Arquitectura de Alto Nivel

### 6.1 Servicios

1. `web`: aplicación Next.js.
2. `api`: aplicación FastAPI.
3. `worker`: proceso Celery.
4. `redis`: cola y broker.
5. `postgres`: persistencia.

### 6.3 Regla de separación entre arte y texto

1. El guion, la narración y los diálogos se generan con el modelo de texto.
2. Las imágenes se generan sin texto embebido.
3. Todo texto visible para el usuario se renderiza en el lector a partir de datos persistidos en base de datos.
4. No se debe confiar en texto generado dentro de imágenes por riesgo de faltas de ortografía, errores gramaticales o baja legibilidad.

### 6.2 Flujo principal

1. El tutor inicia sesión en `web`.
2. `web` obtiene sesión de Clerk.
3. `web` llama a `api` con token del tutor.
4. `api` valida identidad y resuelve el usuario interno.
5. El tutor crea o selecciona un perfil infantil.
6. El tutor crea una historia enviando texto y modo de idioma.
7. `api` crea `story` en estado `pending`.
8. `api` encola tarea `generate_story_script`.
9. `worker` genera el guion y persiste `story` + `story_panels`.
10. `story` pasa a `script_ready`.
11. El tutor revisa y aprueba el guion.
12. `api` cambia `story` a `approved` y encola `generate_story_images`.
13. `worker` genera imágenes, las guarda en disco y actualiza `story_panels.image_url`.
14. `story` pasa a `completed`.
15. `web` lista la historia en la Biblioteca Mágica y permite leerla.
16. El tutor registra feedback por página.
17. `api` actualiza `story_feedback` y recalcula `child_profiles.preference_summary`.

## 7. Estructura Objetivo del Repositorio

La IA implementadora debe crear una estructura equivalente a esta o muy similar:

```txt
hero-ai/
  apps/
    web/
      app/
      components/
      lib/
      middleware.ts
      package.json
    api/
      app/
        main.py
        api/
          routes/
        core/
        db/
        models/
        schemas/
        services/
        workers/
      alembic/
      pyproject.toml
  storage/
    stories/
  docker-compose.yml
  .env.example
  specs-mvp.md
```

Reglas:

1. `storage/` debe persistir entre reinicios.
2. `web` y `api` pueden vivir separados en el mismo monorepo.
3. `worker` debe reutilizar el código de dominio del backend.

## 8. Modelo de Datos

## 8.1 Entidades

1. `users`
2. `child_profiles`
3. `stories`
4. `story_panels`
5. `story_feedback`

Regla adicional:

1. `story_panels.narrative_text` y `story_panels.dialogue` son la fuente única de verdad del texto mostrado en el lector.

## 8.2 Reglas generales

1. Todas las tablas usan `UUID` como clave primaria.
2. Todas las tablas usan `created_at`.
3. Tablas mutables usan `updated_at`.
4. Un tutor solo puede acceder a registros asociados a su `user_id`.
5. Toda historia pertenece a un `child_profile`.

## 8.3 SQL inicial de referencia

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clerk_id VARCHAR(255) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE child_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(120) NOT NULL,
  age INTEGER NOT NULL,
  initial_interests TEXT NOT NULL,
  avatar_config JSONB NOT NULL,
  preference_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE stories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  child_profile_id UUID NOT NULL REFERENCES child_profiles(id) ON DELETE CASCADE,
  source_content TEXT NOT NULL,
  language_target VARCHAR(20) NOT NULL,
  title VARCHAR(255),
  status VARCHAR(40) NOT NULL,
  error_message TEXT,
  script_generated_at TIMESTAMP,
  completed_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  CONSTRAINT stories_language_target_check CHECK (language_target IN ('es', 'en', 'mixed_es_en')),
  CONSTRAINT stories_status_check CHECK (status IN ('pending', 'scripting', 'script_ready', 'approved', 'generating_images', 'completed', 'failed'))
);

CREATE TABLE story_panels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  story_id UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
  panel_order INTEGER NOT NULL,
  image_prompt TEXT NOT NULL,
  scene_description TEXT NOT NULL,
  narrative_text TEXT NOT NULL,
  dialogue TEXT NOT NULL,
  image_url TEXT,
  generation_status VARCHAR(40) NOT NULL DEFAULT 'pending',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  CONSTRAINT story_panels_order_check CHECK (panel_order BETWEEN 1 AND 5),
  CONSTRAINT story_panels_generation_status_check CHECK (generation_status IN ('pending', 'generated', 'failed')),
  CONSTRAINT story_panels_unique_order UNIQUE (story_id, panel_order)
);

CREATE TABLE story_feedback (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  story_id UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
  child_profile_id UUID NOT NULL REFERENCES child_profiles(id) ON DELETE CASCADE,
  panel_order INTEGER NOT NULL,
  reaction_type VARCHAR(40) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  CONSTRAINT story_feedback_panel_order_check CHECK (panel_order BETWEEN 1 AND 5),
  CONSTRAINT story_feedback_reaction_type_check CHECK (reaction_type IN ('love', 'funny', 'scary'))
);

CREATE INDEX idx_child_profiles_user_id ON child_profiles(user_id);
CREATE INDEX idx_stories_child_profile_id ON stories(child_profile_id);
CREATE INDEX idx_stories_status ON stories(status);
CREATE INDEX idx_story_panels_story_id ON story_panels(story_id);
CREATE INDEX idx_story_feedback_profile_id ON story_feedback(child_profile_id);
```

## 8.4 Estructura de `avatar_config`

```json
{
  "hair": "short",
  "hair_color": "brown",
  "eye_color": "green",
  "skin": "light",
  "clothing": "astronaut suit"
}
```

Campos obligatorios:

1. `hair`
2. `hair_color`
3. `eye_color`
4. `skin`
5. `clothing`

## 8.5 Estructura de `preference_summary`

Implementación simple sugerida:

```json
{
  "likes": ["fun adventures", "friendly characters"],
  "avoid": ["scary scenes"],
  "last_reactions": [
    {"panel_order": 1, "reaction_type": "love"}
  ]
}
```

Reglas:

1. No usar embeddings.
2. No usar memoria semántica.
3. Se permite una heurística simple basada en conteo y reglas manuales.

## 9. Autenticación y Autorización

## 9.1 Clerk

1. `web` gestiona login y sesión con Clerk.
2. `api` valida el token del tutor en cada ruta privada.
3. Si el `clerk_id` no existe en `users`, `api` lo crea de forma lazy en el primer request autenticado.

## 9.2 Reglas de autorización

1. Un tutor solo puede listar sus perfiles.
2. Un tutor solo puede crear historias para sus perfiles.
3. Un tutor solo puede leer historias asociadas a sus perfiles.
4. Un tutor no puede registrar feedback sobre historias ajenas.

## 10. Estados de Historia

Estados válidos:

1. `pending`
2. `scripting`
3. `script_ready`
4. `approved`
5. `generating_images`
6. `completed`
7. `failed`

Transiciones válidas:

1. `pending -> scripting`
2. `scripting -> script_ready`
3. `script_ready -> approved`
4. `approved -> generating_images`
5. `generating_images -> completed`
6. `pending|scripting|script_ready|approved|generating_images -> failed`

## 11. Contrato REST

Base path: `/api/v1`

Todas las rutas excepto `/health` requieren autenticación.

## 11.1 Convenciones de error

Respuesta de error estándar:

```json
{
  "detail": {
    "code": "resource_not_found",
    "message": "Story not found"
  }
}
```

Códigos base:

1. `validation_error`
2. `unauthorized`
3. `forbidden`
4. `resource_not_found`
5. `invalid_state_transition`
6. `external_provider_error`
7. `internal_error`

## 11.2 Health

### `GET /health`

Respuesta `200`:

```json
{
  "status": "online"
}
```

## 11.3 Profiles

### `GET /api/v1/profiles`

Lista perfiles del tutor autenticado.

Respuesta `200`:

```json
[
  {
    "id": "uuid",
    "name": "Luna",
    "age": 8,
    "initial_interests": "space, dinosaurs",
    "avatar_config": {
      "hair": "curly",
      "hair_color": "black",
      "eye_color": "green",
      "skin": "brown",
      "clothing": "astronaut suit"
    },
    "preference_summary": {
      "likes": [],
      "avoid": [],
      "last_reactions": []
    },
    "created_at": "2026-04-19T15:00:00Z",
    "updated_at": "2026-04-19T15:00:00Z"
  }
]
```

### `POST /api/v1/profiles`

Request:

```json
{
  "name": "Luna",
  "age": 8,
  "initial_interests": "space, dinosaurs",
  "avatar_config": {
    "hair": "curly",
    "hair_color": "black",
    "eye_color": "green",
    "skin": "brown",
    "clothing": "astronaut suit"
  }
}
```

Respuesta `201`:

```json
{
  "id": "uuid",
  "name": "Luna",
  "age": 8,
  "initial_interests": "space, dinosaurs",
  "avatar_config": {
    "hair": "curly",
    "hair_color": "black",
    "eye_color": "green",
    "skin": "brown",
    "clothing": "astronaut suit"
  },
  "preference_summary": {
    "likes": [],
    "avoid": [],
    "last_reactions": []
  },
  "created_at": "2026-04-19T15:00:00Z",
  "updated_at": "2026-04-19T15:00:00Z"
}
```

Errores:

1. `400 validation_error`

### `PATCH /api/v1/profiles/{profile_id}`

Actualiza nombre, edad, intereses o avatar.

Request parcial permitido.

Respuesta `200` con el perfil actualizado.

Errores:

1. `404 resource_not_found`
2. `403 forbidden`

## 11.4 Stories

### `POST /api/v1/stories`

Crea una historia y dispara el pipeline de scripting.

Request:

```json
{
  "profile_id": "uuid",
  "content": "Texto educativo fuente",
  "language_target": "mixed_es_en"
}
```

Validaciones:

1. `content` mínimo 200 caracteres.
2. `content` máximo 20000 caracteres.
3. `language_target` debe ser `es`, `en` o `mixed_es_en`.

Respuesta `202`:

```json
{
  "story_id": "uuid",
  "status": "scripting"
}
```

Errores:

1. `400 validation_error`
2. `404 resource_not_found`

### `GET /api/v1/stories`

Lista historias del tutor. Esta lista es la Biblioteca Mágica del MVP.

Filtros opcionales:

1. `profile_id`
2. `status`

Respuesta `200`:

```json
[
  {
    "id": "uuid",
    "child_profile_id": "uuid",
    "title": "Mission to the Solar System",
    "status": "completed",
    "language_target": "mixed_es_en",
    "created_at": "2026-04-19T15:00:00Z",
    "completed_at": "2026-04-19T15:10:00Z"
  }
]
```

### `GET /api/v1/stories/{story_id}`

Devuelve metadata de la historia y sus paneles.

Respuesta `200`:

```json
{
  "id": "uuid",
  "child_profile_id": "uuid",
  "title": "Mission to the Solar System",
  "status": "completed",
  "language_target": "mixed_es_en",
  "error_message": null,
  "created_at": "2026-04-19T15:00:00Z",
  "completed_at": "2026-04-19T15:10:00Z",
  "panels": [
    {
      "panel_order": 1,
      "scene_description": "Luna enters a rocket classroom...",
      "narrative_text": "Luna discovered that the planets orbit the Sun.",
      "dialogue": "Wow, let's explore el sistema solar!",
      "image_url": "/assets/stories/story-uuid/panel-1.png"
    }
  ]
}
```

Errores:

1. `404 resource_not_found`
2. `403 forbidden`

### `GET /api/v1/stories/{story_id}/status`

Respuesta `200`:

```json
{
  "story_id": "uuid",
  "status": "generating_images",
  "generated_panels": 3,
  "total_panels": 5,
  "error_message": null
}
```

### `GET /api/v1/stories/{story_id}/script`

Solo para historias en `script_ready`, `approved`, `generating_images` o `completed`.

Respuesta `200`:

```json
{
  "story_id": "uuid",
  "title": "Mission to the Solar System",
  "language_target": "mixed_es_en",
  "panels": [
    {
      "panel_order": 1,
      "scene_description": "Luna enters a rocket classroom...",
      "narrative_text": "Luna discovered that the planets orbit the Sun.",
      "dialogue": "Wow, let's explore el sistema solar!"
    }
  ]
}
```

Errores:

1. `404 resource_not_found`
2. `409 invalid_state_transition` si el guion aún no existe

### `POST /api/v1/stories/{story_id}/approve`

Aprueba el guion y dispara la generación visual.

Respuesta `202`:

```json
{
  "story_id": "uuid",
  "status": "generating_images"
}
```

Errores:

1. `404 resource_not_found`
2. `409 invalid_state_transition` si la historia no está en `script_ready`

### `POST /api/v1/stories/{story_id}/feedback`

Registra reacción por página.

Request:

```json
{
  "panel_order": 2,
  "reaction_type": "love"
}
```

Respuesta `201`:

```json
{
  "id": "uuid",
  "story_id": "uuid",
  "child_profile_id": "uuid",
  "panel_order": 2,
  "reaction_type": "love",
  "created_at": "2026-04-19T15:12:00Z"
}
```

Errores:

1. `400 validation_error`
2. `404 resource_not_found`
3. `409 invalid_state_transition` si la historia no está `completed`

## 12. Contratos de Worker

El worker no debe comunicarse con la API mediante estructuras en memoria. Debe leer y escribir en PostgreSQL y en disco local compartido.

## 12.1 Job `generate_story_script`

Input:

```json
{
  "story_id": "uuid"
}
```

Pasos obligatorios:

1. Cargar `story` y `child_profile` desde base de datos.
2. Cambiar estado a `scripting`.
3. Construir prompt con `name`, `age`, `initial_interests`, `avatar_config`, `preference_summary`, `language_target` y `source_content`.
4. Llamar al modelo de texto.
5. Validar JSON parseable.
6. Validar exactamente 5 paneles.
7. Ejecutar una segunda pasada obligatoria de revisión lingüística usando `Gemini 2.5 Pro` o una validación equivalente controlada por backend.
8. Validar y normalizar ortografía, puntuación y consistencia gramatical antes de persistir el resultado final.
9. Persistir `title` y `story_panels`.
10. Cambiar `story.status` a `script_ready`.
11. Si falla, dejar `story.status = failed` y `error_message`.

Output persistido:

1. `stories.title`
2. `stories.status`
3. `stories.script_generated_at`
4. 5 filas en `story_panels`

## 12.2 Job `generate_story_images`

Input:

```json
{
  "story_id": "uuid"
}
```

Pasos obligatorios:

1. Cargar `story` y sus paneles.
2. Verificar estado `approved`.
3. Cambiar estado a `generating_images`.
4. Para cada panel, construir prompt de imagen usando avatar fijo + escena + estilo.
5. Generar imagen.
6. Guardar archivo en `storage/stories/{story_id}/panel-{n}.png`.
7. Actualizar `story_panels.image_url` con ruta relativa pública.
8. Actualizar `story_panels.generation_status`.
9. Al completar los 5 paneles, marcar `stories.status = completed` y `completed_at`.
10. Si falla cualquier panel, marcar `stories.status = failed` y registrar `error_message`.

Restricciones obligatorias:

1. El prompt de imagen debe indicar explícitamente `NO TEXT`, `NO LETTERING`, `NO SPEECH BUBBLES`, `NO CAPTIONS`.
2. El texto narrativo y los diálogos no deben enviarse como instrucción para ser dibujados dentro de la ilustración.
3. La imagen final debe representar solo la escena visual del panel.

## 12.3 Política de reintentos

1. Reintentar llamadas a proveedor IA con backoff exponencial.
2. Máximo 3 reintentos por job.
3. Si se agotan, dejar estado `failed`.

## 13. Reglas de Prompt

No es necesario fijar el prompt final exacto en este documento, pero sí las reglas de salida.

## 13.1 Prompt de guion

Debe instruir al modelo para producir:

1. Una historia educativa.
2. Un protagonista igual al nombre del perfil.
3. Exactamente 5 paneles.
4. Tono apropiado para infancia.
5. Narrativa clara según la edad.
6. Uso de `language_target`:
   `es` todo en español.
   `en` todo en inglés.
   `mixed_es_en` narración principalmente en español y diálogos con mezcla simple de inglés.
7. Ortografía y gramática correctas para uso educativo.
8. Salida estrictamente JSON con este esquema:

```json
{
  "suggested_title": "string",
  "panels": [
    {
      "page_number": 1,
      "description": "string",
      "narrative": "string",
      "dialogue": "string"
    }
  ]
}
```

## 13.2 Prompt de imagen

Debe instruir al modelo para producir:

1. Misma apariencia del personaje en todos los paneles.
2. Sin texto dentro de la imagen.
3. Sin speech bubbles incrustados.
4. Estilo ilustrado profesional y apto para público infantil.
5. No confiar en el modelo de imagen para rótulos, letras o textos educativos.

## 13.3 Configuración exacta de modelos del MVP

1. Scripting principal: `Gemini 2.5 Pro`.
2. Revisión lingüística final: `Gemini 2.5 Pro`.
3. Imágenes: `Gemini 2.5 Flash Image (Nano Banana)`.

Regla de implementación:

1. Si Google cambia el identificador exacto del modelo, la implementación debe mantener el mismo tier funcional equivalente y documentarlo.
2. No sustituir estos modelos por otros proveedores en el MVP sin cambiar este documento.

## 13.4 Reglas lingüísticas por edad

Rango de edades soportado por el MVP: `4` a `12` años.

Si el perfil recibe una edad fuera de ese rango:

1. Menor a 4: rechazar con `validation_error`.
2. Mayor a 12: rechazar con `validation_error`.

Reglas por tramo:

### Edad 4 a 6

1. Narración con frases cortas y directas.
2. Máximo recomendado de 12 palabras por frase.
3. Diálogos de máximo 8 palabras por intervención.
4. Evitar subordinadas complejas.
5. Evitar ironía, sarcasmo o ambigüedad.

### Edad 7 a 9

1. Narración clara con vocabulario escolar básico.
2. Máximo recomendado de 18 palabras por frase.
3. Diálogos de máximo 12 palabras por intervención.
4. Se permiten explicaciones simples de causa y efecto.

### Edad 10 a 12

1. Narración clara pero un poco más rica en vocabulario.
2. Máximo recomendado de 25 palabras por frase.
3. Diálogos de máximo 18 palabras por intervención.
4. Se permiten explicaciones breves con un poco más de detalle conceptual.

Reglas transversales:

1. Sin faltas de ortografía.
2. Sin errores gramaticales.
3. Puntuación consistente.
4. Sin jerga agresiva o expresiones confusas.
5. Mantener tono positivo y seguro para infancia.

## 13.5 Reglas por idioma de salida

### `es`

1. Todo el texto final debe estar en español.
2. No mezclar inglés salvo nombres propios inevitables.

### `en`

1. Todo el texto final debe estar en inglés.
2. No mezclar español salvo nombres propios inevitables.

### `mixed_es_en`

1. La narración debe estar mayoritariamente en español.
2. El diálogo puede mezclar inglés de forma simple y pedagógica.
3. La mezcla no debe impedir comprensión.
4. No usar Spanglish confuso ni estructuras incorrectas.

## 13.6 Validación lingüística obligatoria antes de publicar

Antes de persistir `title`, `narrative_text` y `dialogue`, el backend debe aplicar una validación final con estas reglas:

1. Verificar que el idioma corresponde a `language_target`.
2. Verificar ortografía y puntuación.
3. Verificar adecuación al tramo de edad.
4. Verificar que no existan contradicciones educativas obvias entre paneles.
5. Verificar que el texto final sea el que se mostrará en el lector.

Si la validación falla:

1. Reintentar una regeneración o normalización del texto hasta 2 veces dentro del job.
2. Si vuelve a fallar, marcar la historia como `failed`.

## 14. Almacenamiento Local de Assets

## 14.1 Directorio físico

Ruta base sugerida:

```txt
storage/stories/{story_id}/panel-{panel_order}.png
```

## 14.2 Ruta pública

Regla sugerida:

```txt
/assets/stories/{story_id}/panel-{panel_order}.png
```

## 14.3 Reglas

1. `api` debe servir archivos estáticos desde `LOCAL_ASSET_DIR`.
2. `worker` debe escribir en el mismo volumen compartido.
3. En base de datos se almacena la ruta pública relativa.
4. Nunca almacenar base64 en base de datos.
5. El lector siempre debe mostrar `narrative_text` y `dialogue` desde base de datos, no desde OCR ni desde la imagen.

## 15. Frontend

## 15.1 Rutas mínimas

1. `/sign-in`
2. `/dashboard`
3. `/profiles/new`
4. `/profiles/[profileId]/edit`
5. `/stories/new`
6. `/stories/[storyId]/script`
7. `/stories/[storyId]/progress`
8. `/stories/[storyId]/read`

## 15.2 Pantallas obligatorias

### Dashboard

Debe mostrar:

1. Perfiles del tutor.
2. Historias recientes.
3. Estado de cada historia.
4. Acción para crear perfil.
5. Acción para crear historia.

### Crear perfil

Campos obligatorios:

1. Nombre.
2. Edad.
3. Intereses iniciales.
4. Cabello.
5. Color de cabello.
6. Color de ojos.
7. Tono de piel.
8. Ropa.

### Crear historia

Campos obligatorios:

1. Perfil infantil.
2. Texto fuente.
3. Idioma objetivo.

### Revisión de guion

Debe mostrar:

1. Título sugerido.
2. Los 5 paneles.
3. Descripción visual.
4. Narración.
5. Diálogo.
6. Botón de aprobar.

### Progreso

Debe hacer polling a `GET /stories/{id}/status` cada 3 a 5 segundos.

### Lector

Debe mostrar por página:

1. Imagen.
2. Narración.
3. Diálogo.
4. Navegación siguiente/anterior.
5. Reacciones `Me encantó`, `Divertido`, `Me dio miedo`.

Reglas obligatorias del lector:

1. La imagen del panel se muestra limpia, sin texto incrustado.
2. La narración y el diálogo se renderizan como elementos UI del lector.
3. La interfaz puede usar globos o bloques de texto, pero el contenido debe provenir de `story_panels.narrative_text` y `story_panels.dialogue`.

Contrato visual recomendado del lector:

1. En desktop y tablet horizontal, usar un layout de dos bloques verticales dentro de una sola página.
2. El bloque superior o principal ocupa aproximadamente 60 a 70 por ciento del alto visible y contiene solo la ilustración.
3. El bloque inferior ocupa aproximadamente 30 a 40 por ciento del alto visible y contiene el texto.
4. La narración se muestra en un bloque de lectura limpio.
5. El diálogo se muestra debajo o al costado en estilo globo UI, pero nunca dibujado dentro de la imagen.
6. Debe existir separación visual clara entre arte y texto.
7. En mobile futuro puede apilarse, pero en el MVP basta con desktop y tablet.

## 16. Docker Compose Objetivo

El `docker-compose.yml` final del MVP debe incluir como mínimo:

1. `web`
2. `api`
3. `worker`
4. `redis`
5. `postgres`

## 16.1 Requisitos funcionales del compose

1. `api` y `worker` deben compartir un volumen para `storage/`.
2. `postgres` debe persistir datos en volumen.
3. `web` debe conocer `NEXT_PUBLIC_API_BASE_URL`.
4. `api` y `worker` deben compartir `DATABASE_URL`, `REDIS_URL`, `GOOGLE_API_KEY`, `LOCAL_ASSET_DIR`.

## 16.2 Archivo objetivo de referencia

La implementación debe producir un `docker-compose.yml` equivalente a este:

```yaml
version: "3.9"

services:
  web:
    build:
      context: ./apps/web
    container_name: hero-web
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_BASE_URL: http://localhost:8000
      NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: ${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
      CLERK_SECRET_KEY: ${CLERK_SECRET_KEY}
    depends_on:
      api:
        condition: service_started

  api:
    build:
      context: ./apps/api
    container_name: hero-api
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+psycopg://hero:hero@postgres:5432/hero_ai
      REDIS_URL: redis://redis:6379/0
      GOOGLE_API_KEY: ${GOOGLE_API_KEY}
      GOOGLE_TEXT_MODEL: ${GOOGLE_TEXT_MODEL:-gemini-2.5-pro}
      GOOGLE_IMAGE_MODEL: ${GOOGLE_IMAGE_MODEL:-gemini-2.5-flash-image}
      CLERK_SECRET_KEY: ${CLERK_SECRET_KEY}
      LOCAL_ASSET_DIR: /app/storage
      CORS_ALLOW_ORIGINS: http://localhost:3000
    volumes:
      - story_assets:/app/storage
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 5

  worker:
    build:
      context: ./apps/api
    container_name: hero-worker
    command: celery -A app.workers.celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql+psycopg://hero:hero@postgres:5432/hero_ai
      REDIS_URL: redis://redis:6379/0
      GOOGLE_API_KEY: ${GOOGLE_API_KEY}
      GOOGLE_TEXT_MODEL: ${GOOGLE_TEXT_MODEL:-gemini-2.5-pro}
      GOOGLE_IMAGE_MODEL: ${GOOGLE_IMAGE_MODEL:-gemini-2.5-flash-image}
      LOCAL_ASSET_DIR: /app/storage
    volumes:
      - story_assets:/app/storage
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started

  redis:
    image: redis:7-alpine
    container_name: hero-redis
    ports:
      - "6379:6379"

  postgres:
    image: postgres:16-alpine
    container_name: hero-postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: hero_ai
      POSTGRES_USER: hero
      POSTGRES_PASSWORD: hero
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hero -d hero_ai"]
      interval: 10s
      timeout: 5s
      retries: 10

volumes:
  postgres_data:
  story_assets:
```

## 16.3 Reglas obligatorias del compose

1. `web` expone el puerto `3000`.
2. `api` expone el puerto `8000`.
3. `postgres` expone el puerto `5432` para desarrollo local.
4. `redis` expone el puerto `6379` para desarrollo local.
5. `api` y `worker` deben montar el mismo volumen `story_assets`.
6. `postgres` debe usar un volumen persistente `postgres_data`.
7. `api` debe servir los archivos generados desde `LOCAL_ASSET_DIR`.
8. `worker` no expone puertos públicos.
9. `web` depende de `api`.
10. `api` y `worker` dependen de `postgres` y `redis`.

## 16.4 Dockerfiles esperados

La implementación debe incluir al menos:

1. `apps/web/Dockerfile`
2. `apps/api/Dockerfile`

Reglas:

1. `web` debe arrancar con `next dev --hostname 0.0.0.0 --port 3000` en desarrollo local via compose.
2. `api` debe incluir dependencias para FastAPI, PostgreSQL, Redis y Celery.
3. `api` debe incluir `curl` o una utilidad equivalente si se usa el `healthcheck` de ejemplo.

## 16.4.1 `apps/web/Dockerfile` de referencia

```dockerfile
FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3000"]
```

Notas:

1. Si se usa `pnpm` o `yarn`, puede cambiar el comando de instalación, pero el comportamiento final debe ser equivalente.
2. El contenedor `web` está definido para desarrollo local del MVP vía Docker Compose.

## 16.4.2 `apps/api/Dockerfile` de referencia

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

Notas:

1. El mismo `Dockerfile` de `api` debe reutilizarse para el servicio `worker`, cambiando solo el `command` en `docker-compose.yml`.
2. Si la implementación usa `requirements.txt` en lugar de `pyproject.toml`, se permite cambiar la estrategia de instalación, pero debe mantenerse equivalente funcionalmente.
3. La imagen final debe incluir dependencias para FastAPI, Pydantic, SQLAlchemy o SQLModel, Alembic, psycopg, Celery, Redis y el cliente HTTP necesario para Google.

## 16.5 Notas de implementación

1. El compose de arriba es la referencia objetivo del MVP, no una obligación de nombres exactos de contenedor.
2. Si la IA implementadora decide usar `env_file`, el resultado final debe seguir exponiendo las mismas variables.
3. Si cambia el driver de PostgreSQL, `DATABASE_URL` puede ajustarse, pero debe mantenerse equivalente funcionalmente.

## 17. Variables de Entorno Mínimas

```txt
DATABASE_URL=
REDIS_URL=
GOOGLE_API_KEY=
GOOGLE_TEXT_MODEL=gemini-2.5-pro
GOOGLE_IMAGE_MODEL=gemini-2.5-flash-image
CLERK_SECRET_KEY=
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
NEXT_PUBLIC_API_BASE_URL=
LOCAL_ASSET_DIR=
```

## 18. Observabilidad y Robustez

1. Loggear inicio y fin de cada job.
2. Loggear errores de proveedor IA.
3. Guardar `error_message` legible en `stories`.
4. No perder estado por reinicio de `api` o `web`.
5. No depender de memoria compartida de proceso.

## 19. Criterios de Aceptación

El MVP está aceptado cuando se verifica lo siguiente:

1. Un tutor puede iniciar sesión y acceder a su dashboard.
2. Un tutor puede crear más de un perfil infantil.
3. Un perfil infantil guarda nombre, edad, intereses y avatar completo.
4. Un tutor puede crear una historia pegando texto.
5. La historia pasa por `pending -> scripting -> script_ready`.
6. El guion contiene exactamente 5 paneles persistidos en DB.
7. El tutor puede aprobar el guion.
8. La historia pasa por `approved -> generating_images -> completed`.
9. Se generan 5 archivos de imagen en disco local.
10. La historia aparece en la Biblioteca Mágica.
11. El lector muestra imagen, narración y diálogo por página.
12. El lector soporta `es`, `en` o `mixed_es_en`.
13. Las imágenes no contienen texto ni globos de diálogo dibujados.
14. La narración y el diálogo mostrados al usuario provienen de la base de datos y no de la imagen.
15. El texto persistido pasa por validación y normalización ortográfica antes de publicarse.
16. El texto respeta el rango de edad del perfil y las reglas del idioma seleccionado.
17. El tutor puede registrar feedback por página.
18. El perfil actualiza `preference_summary` tras recibir feedback.
19. Una historia futura del mismo perfil incluye ese resumen en el contexto de scripting.
20. Reiniciar contenedores no elimina historias ni imágenes.
21. Un tutor no puede leer recursos de otro tutor.

## 20. Plan de Implementación Recomendado

### Fase 1

1. Crear monorepo base.
2. Configurar `web`, `api`, `worker`.
3. Configurar `postgres` y `redis` en Docker.
4. Crear `.env.example`.

### Fase 2

1. Implementar autenticación con Clerk.
2. Implementar tabla `users` y provision lazy.
3. Implementar CRUD de perfiles.

### Fase 3

1. Implementar tablas `stories`, `story_panels`, `story_feedback`.
2. Implementar endpoints REST.
3. Implementar estados.

### Fase 4

1. Implementar job `generate_story_script`.
2. Persistir guion y paneles.
3. Implementar aprobación.

### Fase 5

1. Implementar job `generate_story_images`.
2. Guardar imágenes en disco.
3. Servir assets locales.

### Fase 6

1. Implementar dashboard, biblioteca y lector.
2. Implementar feedback.
3. Implementar recálculo de `preference_summary`.

### Fase 7

1. Probar flujo end-to-end.
2. Verificar autorización por tutor.
3. Verificar persistencia tras reinicios.

## 21. Regla Final

La IA implementadora debe construir el MVP según este documento, no según archivos Python previos del repositorio.
