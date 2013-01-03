# Yaranullin

Copyright (c) 2012 Marco Scopesi <marco.scopesi@gmail.com>

Yaranullin is an interactive map for role-playing games. Basically it is
a piece of software that helps role players to track the position of their
heroes when fighting against monsters and other scary things, such as
skeletons and other derivatives.

## Dependencies

This is a list of all dependencies.

* python >= 2.7
* twisted >= 11.1

## Server

To run a server for a Yaranullin game, open a terminal and type:

```bash
$ cd /path/to/yaranullin/sources
$ ./bin/yrn server --game test_1
```

The game to load (test_1 in the above example) should be a folder inside '/path/to/yaranullin/sources/data/saves/'.

## Client

To run a client for a Yaranullin game, open a terminal and type:

```bash
$ cd /path/to/yaranullin/sources
$ ./bin/yrn client --host 127.0.0.1
```

You can change the host if the server is on another machine on the network.


## Images

All pawn images are taken from http://www.immortalnights.com/tokensite/tokenpacks.html
All tiles for the maps are taken from http://www.lostgarden.com/2006/02/250-free-handdrawn-textures.html
