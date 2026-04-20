## Documento de Arquitectura de Software: Hero Adventure AI

---

## 1. Arquitectura de Alto Nivel [cite: 32]
El sistema utiliza una arquitectura de **Microservicios Orquestados** con un enfoque en procesamiento asíncrono.

### Componentes Principales: [cite: 34]
* **Identity Layer:** Gestión de usuarios mediante Clerk.
* **Client App (Frontend):** Next.js 14 (App Router).
* **API Gateway (Backend):** FastAPI (Python).
* **Worker Service:** Celery + Redis para el procesamiento de IA.

---

## 2. Definición del Modelo de Datos (Esquema Relacional) [cite: 39]
### Entidades Actualizadas: [cite: 40]
* **User:** `clerk_id` (PK), `email`, `created_at`.
* **ChildProfile:** `id`, `user_id`, `name`, `avatar_config` (JSON).
* **Source Material:** `id`, `user_id`, `raw_text`, `status` (processed, pending).
* **ComicBook:** `id`, `profile_id`, `source_id`, `title`, `status` (draft, scripting, generating, ready).
* **ComicPage:** `id`, `comic_id`, `page_number`, `image_url`, `narrative_text`, `audio_url`.
* **InteractionLog:** `id`, `profile_id`, `page_id`, `tag`, `timestamp`.

---

## 3. Especificación de la API (REST Endpoints)
> **Nota:** Todos los endpoints (excepto webhooks) requieren el header `Authorization: Bearer <clerk_token>`.

### A. Perfiles de Niños
* **GET `/profiles`:** Lista los perfiles asociados al usuario.
* **POST `/profiles`:** Crea un nuevo perfil e incluye la configuración del avatar.
* **PATCH `/profiles/{id}`:** Actualiza el nombre o la configuración del avatar.

### B. Gestión de Historias (Comic Pipeline)
* **POST `/stories/ingest`:** * **Input:** `{ "text": "...", "profile_id": "..." }`.
    * **Acción:** Crea un `SourceMaterial`, inicia la tarea de "Scripting" y retorna el `comic_id`.
* **GET `/stories/{id}/script`:** Obtiene el guion generado por la IA para la aprobación del padre.
* **POST `/stories/{id}/approve-script`:** Cambia el estado a `generating` y dispara el worker de imágenes.
* **GET `/stories/{id}/status`:** Retorna el progreso de generación (ej. "3 de 5 páginas listas").

### C. Consumo (Lector)
* **GET `/stories/{id}`:** Obtiene la metadata del cómic y la lista de sus páginas.
* **POST `/stories/{id}/feedback`:** * **Input:** `{ "page_id": "...", "tag": "me gusto" }`.
    * **Acción:** Registra la interacción para la memoria semántica.

---

## 4. Pipeline de Generación de Contenido
1. **Normalization:** Limpieza del texto y adaptación según la edad.
2. **Scripting:** Generación de un JSON estructurado con descripciones de escenas y diálogos.
3. **Image Generation:** Worker asíncrono que combina la descripción de la escena con la configuración del avatar (`scene_description` + `avatar_config`).
4. **Notification:** El backend actualiza el estado y el frontend realiza polling o recibe una señal vía WebSocket.

---

## 5. Stack de Infraestructura
* **Backend:** FastAPI, PostgreSQL, Redis, Celery.
* **Frontend:** Next.js, Framer Motion (para animaciones de libro), Zustand.
* **IA:** Gemini 1.5 Pro (Texto), Flux.1 / SDXL (Imágenes).


