## Why

Actualmente, cuando un usuario genera un guion para una historia, la única opción disponible es aprobarlo para generar las ilustraciones. Si el usuario no está satisfecho con el resultado, no puede solicitar una nueva versión, ni tampoco puede eliminar la historia para limpiar su panel. Agregar estas opciones es fundamental para brindar flexibilidad y control sobre la generación de historias.

## What Changes

- **Nueva acción: Generar nueva versión:** Permite al usuario descartar el guion actual y solicitar al sistema que genere uno nuevo desde cero.
- **Nueva acción: Eliminar historia:** Permite al usuario borrar por completo la historia en estado de revisión de guion si ya no la necesita.
- **Cambio en la UI de revisión de guion:** Se elimina el botón de aprobación de la cabecera superior. Se centralizan todas las acciones de decisión (Eliminar, Nueva versión, Aprobar) en la parte inferior de la pantalla del guion.

## Capabilities

### New Capabilities
- `script-actions`: Gestión del ciclo de vida del guion en estado `script_ready`, incluyendo regeneración y eliminación.

### Modified Capabilities

- Ninguna

## Impact

- **Frontend (`apps/web`):** Modificación de la pantalla de revisión de guion (`apps/web/app/stories/[storyId]/script/page.tsx`), adición de nuevos métodos en el cliente de API (`lib/api.ts`), y ajustes de estilos (`page.module.css`).
- **Backend (`apps/api`):** Creación de un nuevo endpoint para regenerar el guion (`POST /api/v1/stories/{story_id}/regenerate-script`), adición de lógica en el servicio para borrar paneles previos y re-encolar la tarea de Celery, y validación de que el endpoint de eliminación actual soporta correctamente el borrado en estado `script_ready`.