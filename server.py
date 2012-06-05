import socket,threading,sys,SocketServer,time

connection = ("localhost", 9998)
class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        response = data.upper()
        self.request.sendall(response)
		
        global server
        server.shutdown()

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

server = ThreadedTCPServer(connection, ThreadedTCPRequestHandler)

if __name__ == "__main__":
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = False
    server_thread.start()
