## ADDED Requirements

### Requirement: Generar nueva versión de guion
El sistema DEBE permitir a los usuarios solicitar una nueva versión del guion cuando éste se encuentra en estado de revisión (`script_ready`).

#### Scenario: Solicitud de nueva versión de guion
- **WHEN** un usuario solicita generar una nueva versión de una historia en estado `script_ready`
- **THEN** el sistema elimina los paneles previos asociados a la historia
- **THEN** el sistema restablece el estado de la historia a `pending` o `scripting`
- **THEN** el sistema vuelve a encolar la tarea asíncrona de generación de guion

#### Scenario: Flujo de interfaz de usuario para regeneración
- **WHEN** el usuario hace clic en el botón "Nueva versión" en la vista del guion
- **THEN** el sistema envía una solicitud al backend para regenerarlo
- **THEN** el usuario es redirigido a la pantalla de progreso (`/stories/[storyId]/progress`) para observar el estado de la generación

### Requirement: Eliminar historia en revisión
El sistema DEBE permitir a los usuarios eliminar completamente una historia que está en estado de revisión de guion (`script_ready`).

#### Scenario: Borrado de historia desde la vista de guion
- **WHEN** un usuario confirma la eliminación mediante el botón "Eliminar" en la pantalla del guion
- **THEN** la historia es eliminada permanentemente de la base de datos junto con cualquier información asociada (como paneles o feedback)
- **THEN** el usuario es redirigido de vuelta al dashboard principal

### Requirement: Interfaz consolidada de revisión
La interfaz de revisión de guion DEBE agrupar todas las acciones de toma de decisión en la parte inferior de la pantalla.

#### Scenario: Disposición de los botones de acción
- **WHEN** un usuario visualiza la pantalla del guion
- **THEN** el botón de "Aprobar y generar ilustraciones" ya no se muestra en la cabecera superior
- **THEN** el pie de la página muestra tres botones: "Eliminar" (estilo secundario/peligro), "Nueva versión" (estilo secundario) y "Aprobar y generar ilustraciones" (estilo primario/éxito)
