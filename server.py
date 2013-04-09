#!/usr/bin/env python
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
from handler import ProxiedRequestHandler
from proxier import ProxyManager
from ca_generator import CertificateAuthority

class PipeServer(HTTPServer):
    def __init__(self, server_address=('', 8080), try_local_proxylist=True, chainlength=0):
        HTTPServer.__init__(self, 
                        server_address, 
                        ProxiedRequestHandler,
                    )
        self.ca = CertificateAuthority()
        self.proxy_fetcher = ProxyManager(try_local_proxylist)
        self.CHAIN = 1


class ThreadedPipeServer(ThreadingMixIn, PipeServer):
    
    def stop_proxy(self):
        self.proxy_fetcher.terminate()