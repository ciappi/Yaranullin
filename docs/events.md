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
* *uid*

### game-request-board-del

* *uid*

### game-request-board-change

* *uid*

### game-request-pawn-new

* *name*
* *initiative*
* *x*
* *y*
* *width*
* *height*
* *uid*

### game-request-pawn-place

* *uid*
* *x*
* *y*
* *rotate*

### game-request-pawn-move

* *uid*
* *dx*
* *dy*
* *rotate*

### game-request-pawn-del

* *uid*

### game-request-pawn-next

* *uid*: optional, if omitted returns the next pawn in initiative order.

## Events from the game model

### game-event-board-new

* *name*
* *width*
* *height*
* *uid*

### game-event-board-del

* *uid*

### game-event-board-change

* *uid*

### game-event-pawn-new

* *name*
* *initiative*
* *x*
* *y*
* *width*
* *height*
* *uid*

### game-event-pawn-moved

* *uid*
* *x*
* *y*
* *width*
* *height*

### game-event-pawn-del

* *uid*

### game-event-pawn-next

* *uid*

## Local I/O

### game-load

* *dname*

### game-save


## Network I/O

### join

* *host*
* *port*

## Texture loading

### texture-request
Request a resource from the server.

* *name*: the file name of the resource

### texture-update
Broadcast a resource, usually from the server.

* *name*: the file name of the resource
* *data*: the content of the file

