# Memory

## Propósito

Este archivo resume el contexto de trabajo acumulado en el proyecto hasta ahora para que futuras iteraciones puedan entender rápidamente:

1. qué se decidió
2. por qué se decidió
3. qué documentos son la fuente de verdad actual
4. qué cosas quedaron pendientes

## Estado general del proyecto

El repositorio comenzó con un prototipo en Python basado en `main.py` y `workers.py`, más varios documentos de idea y arquitectura.

Durante esta colaboración se concluyó que el prototipo actual no debía usarse como base de implementación final del MVP porque:

1. mezcla decisiones de prototipo con arquitectura objetivo
2. usa almacenamiento en memoria
3. no es coherente con el flujo real requerido para FastAPI + Celery + PostgreSQL
4. no representa fielmente el MVP acordado

Decisión tomada:

1. el MVP debe implementarse desde cero
2. los archivos Python actuales no son fuente de verdad
3. la fuente de verdad actual son los documentos de especificación

## Documentos relevantes del repo

### Fuente de verdad actual para el MVP

1. `specs-mvp.md`

### Documento base funcional del MVP

1. `mvp-idea.md`

### Documento borrador para visión final

1. `specs-final-draft.md`

### Documentos previos usados como insumo

1. `project-description.md`
2. `specs-1.md`

## Cómo evolucionó el trabajo

### Fase inicial

Se inspeccionó el contenido del proyecto y se identificó:

1. un backend FastAPI mínimo
2. workers con Celery
3. uso de Redis
4. ausencia de persistencia real
5. diferencia entre la visión documentada y la implementación existente

### Construcción del spec del MVP

Se creó y luego se reescribió `specs-mvp.md` varias veces para volverlo:

1. coherente con `mvp-idea.md`
2. independiente del código actual
3. apto para que otra IA implemente desde cero
4. prescriptivo en arquitectura, API, DB, workers, assets y Docker

### Construcción del borrador del producto final

Se creó `specs-final-draft.md` como documento exploratorio para discutir la visión final del producto más allá del MVP.

## Decisiones cerradas del MVP

Estas son las decisiones más importantes tomadas hasta ahora.

### Implementación

1. el MVP se implementa desde cero
2. no se debe basar en `main.py` ni `workers.py`
3. el MVP incluye frontend y backend

### Stack del MVP

1. frontend en Next.js
2. backend en FastAPI
3. autenticación con Clerk
4. persistencia con PostgreSQL
5. procesamiento asíncrono con Celery + Redis
6. almacenamiento local de imágenes en disco durante el MVP

### Alcance funcional del MVP

1. login del tutor
2. múltiples perfiles infantiles por tutor
3. perfil con nombre, edad, intereses y avatar
4. ingreso manual de texto como única fuente de contenido
5. generación de guion de 5 paneles
6. aprobación del guion antes de generar imágenes
7. generación asíncrona de una imagen por panel
8. Biblioteca Mágica para listar historias
9. lector tipo libro digital
10. feedback por página
11. evolución simple del perfil mediante `preference_summary`

### Fuera de alcance del MVP

1. URLs como fuente
2. vídeos o YouTube
3. fotos reales de menores
4. edición manual del guion
5. historias interactivas complejas
6. audio como feature del MVP
7. storage cloud para imágenes del MVP

## Decisiones sobre IA y contenido

### Modelos elegidos para el MVP

1. proveedor principal: Google
2. scripting: `Gemini 2.5 Pro`
3. revisión lingüística final: `Gemini 2.5 Pro`
4. imágenes: `Gemini 2.5 Flash Image (Nano Banana)`

### Regla crítica sobre texto e imagen

Se decidió explícitamente que:

1. las imágenes no deben contener texto incrustado
2. las imágenes no deben contener globos de diálogo dibujados
3. el texto mostrado al usuario se genera con el modelo de texto y se persiste en DB
4. el lector renderiza narración y diálogo como UI separada de la imagen

Motivo:

1. el producto es educativo
2. no se quiere depender de texto dentro de imágenes por riesgo de errores ortográficos, gramaticales y legibilidad deficiente

### Reglas lingüísticas definidas en el spec

1. soporte para `es`, `en` y `mixed_es_en`
2. reglas por tramos de edad `4-6`, `7-9` y `10-12`
3. validación y normalización ortográfica antes de publicar una historia
4. si la validación falla repetidamente, la historia debe marcarse como `failed`

## Contenido clave de `specs-mvp.md`

El documento del MVP ya contiene:

1. objetivo y alcance final del MVP
2. decisiones cerradas
3. stack técnico
4. arquitectura objetivo
5. estructura objetivo del repositorio
6. esquema SQL inicial
7. contratos REST
8. contratos de workers
9. reglas de prompt
10. almacenamiento local de assets
11. requerimientos del frontend y del lector
12. `docker-compose.yml` objetivo
13. Dockerfiles de referencia
14. variables de entorno
15. criterios de aceptación

## Contenido clave de `specs-final-draft.md`

El borrador de producto final contiene ideas sobre:

1. visión más allá del MVP
2. propuesta de valor para familias y escuelas
3. personalización profunda
4. múltiples formatos de entrada
5. múltiples formatos de salida
6. continuidad narrativa
7. herramientas para docentes
8. arquitectura futura posible
9. entidades y módulos futuros
10. preguntas abiertas para revisar juntos

## Estado del código existente

`main.py` y `workers.py` siguen presentes en el repo al momento de esta nota, pero se acordó que:

1. no deben ser refactorizados como base del MVP
2. pueden ser eliminados antes del desarrollo real
3. no deben condicionar el diseño final

## Estado de Docker actual del repo

El `docker-compose.yml` real del repositorio contiene una versión previa con `api`, `worker` y `redis`, pero no representa todavía la arquitectura objetivo final del MVP.

El compose objetivo detallado está documentado en `specs-mvp.md` e incluye:

1. `web`
2. `api`
3. `worker`
4. `redis`
5. `postgres`
6. volumen compartido para assets
7. volumen persistente para Postgres

## Pendientes naturales para futuras sesiones

1. revisar y cerrar la versión final del MVP si hiciera falta algún ajuste adicional
2. decidir cuándo borrar formalmente el código Python prototipo
3. convertir `specs-final-draft.md` en una especificación final real del producto futuro
4. definir si la visión final prioriza familias, escuelas o ambos desde el core

## Regla práctica para futuras conversaciones

Si en una futura sesión aparece una duda entre el código existente y las especificaciones:

1. prevalece `specs-mvp.md` para el MVP
2. `specs-final-draft.md` se usa solo como borrador de visión final
3. `main.py` y `workers.py` no deben tomarse como restricción arquitectónica
