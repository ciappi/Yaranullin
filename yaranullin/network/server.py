# yaranullin/network/server.py
#
# Copyright (c) 2012 Marco Scopesi <marco.scopesi@gmail.com>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


from time import sleep
from SocketServer import ThreadingTCPServer, BaseRequestHandler

from base import EndPoint, NetworkView, NetworkController, NetworkSpinner
from yaranullin.spinner import CPUSpinner


class ServerNetworkController(NetworkController):

    pass


class ServerNetworkView(NetworkView):

    handle_game_event_update = NetworkView.add_to_out_queue
    handle_game_event_pawn_next = NetworkView.add_to_out_queue
    handle_game_event_pawn_updated = NetworkView.add_to_out_queue
    handle_game_event_board_change = NetworkView.add_to_out_queue
    handle_texture_update = NetworkView.add_to_out_queue


class ServerEndPoint(BaseRequestHandler, EndPoint):

    def setup(self):
        """Setup a server end point for every connected client."""
        # Create in and out queues.
        EndPoint.setup(self)
        self.request.setblocking(False)
        # Create the view of the connected client.
        view = ServerNetworkView(self.server.event_manager)
        view.end_point = self
        # Create the controller of the connected client.
        controller = ServerNetworkController(self.server.event_manager)
        controller.end_point = self
        # Save a reference to them.
        self.view = view
        self.controller = controller
        self.keep_going = True

    def handle(self):
        """Handle the connection.

        Simply pull and push data from and to the socket.
        Exit the loop if EOFError is raised (the client drop the
        connection) and the get a quit event from Yaranullin.

        """
        try:
            while self.keep_going:
                self.pull()
                self.push()
                sleep(0.01)
        except EOFError:
            pass

    def handle_quit(self, ev_type):

        self.keep_going = False


class ServerNetworkSpinner(NetworkSpinner, ThreadingTCPServer):

    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, event_manager, server_address):
        ThreadingTCPServer.__init__(self,
                                    server_address,
                                    ServerEndPoint,
                                    bind_and_activate=True)
        CPUSpinner.__init__(self, event_manager)

    def run_network(self):

        self.serve_forever()

    def handle_quit(self, ev_type):

        self.keep_going = False
        self.shutdown()
