# Change Log

---
All notable changes and updates to this project will be documented in this file.
This includes both release notes and future changes.

The format of this file is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-03-20

---
This release is currently in development. It proposes the addition of a basic 2D vectorial editor.
The initial features that will compose this projects editing canvas are set to include:
- The drawing of a basic grid background
- The ability to switch between editing and floating modes
- The ability to manipulate vertices:
  - Move a single vertex
  - Select and move multiple vertices
  - Add vertices
  - Remove a single vertex
  - Remove multiple vertices
  - Add vertices in-between two vertices after completion of a shape
- The ability to manipulate shapes:
  - Drawing multiple independent shapes
  - Selecting a shape to edit it
  - Deleting a shape
  - Moving a shape

### Added
- ``Base editor``: The addition of a basic grid background.
- ``Base drawing logic & vertex/mouse state management``: It is now possible to add vertices, move them, and draw a 
single shape.
- ``Base shape management``: Possibility to add multiple shapes that are independent of each other.
- ``Shape selection/edition & vertex deletion``: Now possible to select a shape and edit it. Selecting multiple vertices
and deleting them is also possible.
- ``Shape vertex addition``: It is now possible to add vertices in-between two vertices after completion of a shape.
- ``Shape auto translation, shift select & shape deletion``: When resizing the window, shapes are automatically 
translated to keep a centered position. Holding shift and pressing a vertex will select it without unselecting other 
vertices. Holding control and selecting a shape will delete it.
