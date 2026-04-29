## 1. Backend: Servicio y Endpoint de Regeneración

- [x] 1.1 Modificar `app/services/story_service.py` para crear el método `regenerate_script(session, user, story_id)` que elimine paneles y devuelva el estado a `pending`.
- [x] 1.2 Añadir la ruta `POST /{story_id}/regenerate-script` en `app/api/routes/stories.py` (usando el servicio de regeneración y llamando a `generate_story_script`).
- [x] 1.3 Renombrar o refactorizar opcionalmente la ruta `delete_failed_story` a `delete_story_endpoint` en `app/api/routes/stories.py` para mayor claridad.

## 2. Frontend: Cliente de API y Gestión de Estado

- [x] 2.1 Añadir la función `regenerateStoryScript(token: string, storyId: string)` en `apps/web/lib/api.ts`.
- [x] 2.2 Agregar el estado de carga (`isDeleting`, `isRegenerating`) en `apps/web/app/stories/[storyId]/script/page.tsx`.
- [x] 2.3 Añadir las funciones `handleDelete()` con `window.confirm` y `handleRegenerate()` en la página de revisión.

## 3. Frontend: Rediseño de la UI

- [x] 3.1 Quitar el botón superior "Aprobar y generar ilustraciones" del header.
- [x] 3.2 Añadir y organizar tres botones ("Eliminar", "Nueva versión", "Aprobar y generar ilustraciones") en el footer.
- [x] 3.3 Añadir la clase `.btnDanger` en `apps/web/app/stories/[storyId]/script/page.module.css` para el botón de eliminar, y deshabilitar todos los botones mientras se procesa la acción.
