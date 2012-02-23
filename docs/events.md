# Yaranullin Event List

TODO: explain the event system.

## General

### tick

### quit

## User inputs

### key-down

* *key*
* *mod*
* *unicode*

### mouse-click-single-left

* *pos*

### mouse-click-double-left

* *pos*

### mouse-click-single-right

* *pos*

### mouse-wheel-up

* *pos*

### mouse-wheel-down

* *pos*

### mouse-motion

* *pos*
* *rel*

### mouse-drag-left

* *pos*
* *rel*

## Requests to the game model

### game-request-board-new

* *name*
* *width*
* *height*

### game-request-board-del

* *board_id*

### game-request-board-change

* *board_id*

### game-request-pawn-new

* *name*
* *initiative*
* *x*
* *y*
* *width*
* *height*

### game-request-pawn-place

* *pawn_id*
* *x*
* *y*
* *rotate*

### game-request-pawn-move

* *pawn_id*
* *dx*
* *dy*
* *rotate*

### game-request-pawn-del

* *pawn_id*

### game-request-pawn-next

* *pawn_id*: optional, if omitted returns the next pawn in initiative order.

## Events from the game model

### game-event-board-new

* *name*
* *width*
* *height*
* *board_id*

### game-event-board-del

* *board_id*

### game-event-board-change

* *board_id*

### game-event-pawn-new

* *name*
* *initiative*
* *x*
* *y*
* *width*
* *height*
* *board_id*

### game-event-pawn-moved

* *board_id*
* *x*
* *y*
* *width*
* *height*

### game-event-pawn-del

* *board_id*

### game-event-pawn-next

* *board_id*

## Local I/O

### game-load

* *fname*

### game-save

* *fname*

## Network I/O

### join

* *host*
* *port*

## Resource handling

### resource-get
Request a resource with the given hash from the server.

* *hash*: sha1 hash of the resource

### resource-send
Broadcast a resource, usually from the server.

* *hash*: sha1 hash of the resource
* *string*: the resource saved a

### resource-request

* *hash*

### resource-event

* *hash*
* *image*
