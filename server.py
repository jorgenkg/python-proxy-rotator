#!/usr/bin/env python
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
from handler import ProxiedRequestHandler
from ca_generator import CertificateAuthority

DEBUG = False

class PipeServer(HTTPServer):
    def __init__(self, server_address=('', 8080)):
        HTTPServer.__init__(self, 
                        server_address, 
                        ProxiedRequestHandler,
                    )
        self.ca = CertificateAuthority()


class ThreadedPipeServer(ThreadingMixIn, PipeServer):
    pass
            
if __name__ == '__main__':
    proxy = ThreadedPipeServer()
    try:
        print "Server is running."
        proxy.serve_forever()
    except KeyboardInterrupt:
        print "\nServer is shuting down. \nPlease wait for the called requests to terminate."
        proxy.server_close()
        