## Context

Actualmente en el MVP, una vez generado el guion, el usuario es redirigido a `/stories/[storyId]/script` (estado `script_ready`). En este punto solo puede "Aprobar y generar ilustraciones". Si el usuario encuentra errores o simplemente no le gusta el guion generado por Gemini, no tiene opciones nativas para descartarlo de forma limpia. 

## Goals / Non-Goals

**Goals:**
- Proporcionar un endpoint idempotente para regenerar guiones que elimine los paneles anteriores.
- Reutilizar la lógica de cola de Celery ya existente (`generate_story_script`).
- Proporcionar UI clara y segura para eliminar historias desde la vista de revisión del guion.

**Non-Goals:**
- Mantenimiento de un historial de versiones o borradores de los guiones.
- Uso de modales complejos en frontend; se usará la API nativa de `window.confirm` para mayor simplicidad en el borrado.
- Reescritura del flujo de estado principal de la aplicación.

## Decisions

**Decisión 1: Endpoint de regeneración de guion**
- **Alternativa 1:** Modificar el endpoint de retry `POST /{story_id}/retry` para que acepte estados `script_ready`.
- **Alternativa 2 (Elegida):** Crear un nuevo endpoint dedicado `POST /{story_id}/regenerate-script`.
- **Razón:** `retry` está conceptualmente ligado a errores y estados `failed`. Regenerar es una acción de usuario voluntaria sobre un estado "exitoso" (`script_ready`). El nuevo endpoint asegura que se borren los paneles antes de volver a estado `pending`.

**Decisión 2: Reutilización de `delete_failed_story`**
- **Análisis:** La función del backend en `app/api/routes/stories.py` se llama `delete_failed_story` y usa el método subyacente `delete_story(session, user, story_id)`. `delete_story` borra en cascada feedbacks, paneles y la historia. No impone restricciones de estado estricto en la base de datos (solo lee y borra).
- **Decisión:** Mantendremos el uso de este endpoint subyacente (`DELETE /api/v1/stories/{story_id}`) para eliminar la historia en revisión. Su implementación actual es suficientemente robusta porque elimina los paneles correctamente. Renombrar la función a nivel de API route de `delete_failed_story` a algo más genérico (como `delete_story_endpoint`) puede ser opcional para la claridad del código, pero no estrictamente necesario si ya funciona.

**Decisión 3: Rediseño de UI**
- **Decisión:** Agrupar todos los Call to Actions (CTAs) en el `footer` del componente React y eliminar el de la cabecera.
- **Razón:** Evita acciones precipitadas (forzando a hacer scroll y ver todo el guion antes de decidir) y organiza la pantalla visualmente con una jerarquía clara: Eliminar a la izquierda, acciones del ciclo de vida a la derecha.

## Risks / Trade-offs

- **Risk**: El borrado de paneles deja artefactos huérfanos.
  - **Mitigación**: Los paneles en `script_ready` no tienen imágenes generadas todavía, por lo que el borrado es puramente en base de datos. El método actual `session.delete(panel)` en SQLAlchemy/SQLModel es suficiente.
- **Risk**: El usuario pulsa múltiple veces "Regenerar".
  - **Mitigación**: Deshabilitar los botones de acción (`disabled`) en el frontend tan pronto como inicie cualquier solicitud (eliminar, regenerar o aprobar).
