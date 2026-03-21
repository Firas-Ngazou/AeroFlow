# Change Log

All notable changes and updates to this project will be documented in this file.
This includes both release notes and future changes.

The format of this file is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-20

This is the first editor release. It consists of a basic 2D vectorial editor. It permits the user to draw 
shapes and manipulate them.

Pressing right-click lets the user switch between editing and floating modes.

- Manipulating vertices:
  - By pressing **_left-click while in edit mode_**, the user may place a vertex at the mouse position.
  - By pressing **_left-click while in floating mode over a vertex_**, the user may move it to the mouse position.
  - By pressing **_left-click while in floating mode over nothing_**, the use may start a new selection area. He can 
  then keep **_holding left-click and move the mouse_** to select multiple vertices. Doing so while **_holding Ctrl_** 
  will delete the selected vertices.
  - When multiple vertices are selected, the user may move them all at once by **_pressing left-click while in floating 
  mode_**.
  - **_Shift-clicking a vertex while in floating_** mode will select it without unselecting other vertices.
  - If a shape is completed (closed), the user may add vertices in-between two vertices by **_pressing left-click while 
  in floating mode and hovering over the correct positions_**.
- Manipulating shapes:
  - By **_pressing left-click over a shape while in floating mode_**, the user may select it.
  - By **_pressing left-click and holding Ctrl while in floating mode over nothing_**, the user may start a new 
  selection area inside which any shape may be deleted **_on left-click release_**.
  - By **_switching modes_**, he may exit the current shape to start a new one or edit an existing one.

- Shortcuts:
  - A: Select all vertices.
  - Backspace: Delete selected
  - Escape: Exit the current selected shape and close it.

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
- ``Shortcuts``: A few shortcuts are now available.
