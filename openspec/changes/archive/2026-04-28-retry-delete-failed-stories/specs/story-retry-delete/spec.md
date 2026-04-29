## ADDED Requirements

### Requirement: Delete failed story
The system MUST allow users to delete a story that has failed during generation.

#### Scenario: User deletes a failed story
- **WHEN** the user clicks the "Eliminar" button on a failed story card
- **THEN** the system deletes the story record from the database
- **AND** the system deletes all associated story panels
- **AND** the system deletes any generated physical image assets from the file system
- **AND** the story is removed from the user's dashboard

### Requirement: Retry failed story
The system MUST allow users to retry the generation of a story that has failed.

#### Scenario: User retries a story that failed during script generation
- **WHEN** the user clicks the "Reintentar" button on a story that failed before having an approved script
- **THEN** the system resets the story status to `pending`
- **AND** the system clears any previous error message
- **AND** the system enqueues a new `generate_story_script` background task

#### Scenario: User retries a story that failed during image generation
- **WHEN** the user clicks the "Reintentar" button on a story that failed after script approval
- **THEN** the system resets the story status to `approved`
- **AND** the system clears any previous error message
- **AND** the system enqueues a new `generate_story_images` background task