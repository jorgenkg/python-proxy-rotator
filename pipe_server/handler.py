from BaseHTTPServer import BaseHTTPRequestHandler
from urlparse import urlparse, urlunparse, ParseResult
from httplib import HTTPResponse
import os, random
from ssl import wrap_socket, PROTOCOL_TLSv1
from socket import socket, timeout as TimeoutException
from proxy.badgersocket import ProxySocket

class ProxiedRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self.connect_through_ssl = False
        self._proxy_fetcher = server.proxy_fetcher
        self.CHAIN = server.CHAIN
        self.DEBUG = server.DEBUG
        try: BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        except Exception as e: 
            if server.DEBUG: print e
    
    def _connect_to_host(self):
        if self.connect_through_ssl:
            self.hostname, self.port = self.path.split(':')
        else:
            u = urlparse(self.path)
            if u.scheme != 'http': print 'ERROR Unknown request scheme: %s' % repr(u.scheme)
            self.hostname = u.hostname
            self.port = u.port or 80
            self.path = urlunparse( 
                                ParseResult(
                                    scheme='http',
                                    netloc='%s' % u.hostname,
                                    params=u.params,
                                    path=u.path or '/',
                                    query=u.query,
                                    fragment=u.fragment
                                )
                            )
        # Create a pipe to the remote server
        self._pipe_socket = ProxySocket( self._proxy_fetcher, chainlength=self.CHAIN, use_ssl=self.connect_through_ssl, DEBUG=self.DEBUG )
        self._pipe_socket.connect( (self.hostname, int(self.port)) )

        # Wrap socket if SSL is required
        if self.connect_through_ssl:
           self._pipe_socket = wrap_socket(self._pipe_socket)

    def do_CONNECT(self):
        self.connect_through_ssl = True
        try:
            self._connect_to_host()
            # http://curl.haxx.se/ca/cacert.pem
            self.request = wrap_socket(
                                        self.request, 
                                        server_side = True,
                                        certfile = self.server.ca[self.path.split(':')[0]],
                                        ssl_version=PROTOCOL_TLSv1,
                                        ca_certs=os.path.join(os.getcwd(),'cacert.pem')
                                    )
        except Exception, e:
            self.send_error(500, str(e))
            return
        
        # Reload!
        self.setup()
        self.ssl_host = 'https://%s' % self.path
        self.handle_one_request()
    
    def do_RELAY(self, retried=False):
        if not self.connect_through_ssl:
            try:
                self._connect_to_host()
            except TimeoutException, e:
                if retried: self.send_error(504, "Gateway Timeout")
                else: self.do_RELAY(True)
                return
            except Exception, e:
                self.send_error(500, str(e))
                return


        request = '%s %s %s\r\n' % (self.command, self.path, self.request_version)
        request += '%s\r\n' % self.headers
        if 'Content-Length' in self.headers: request += self.rfile.read(int(self.headers['Content-Length']))
        self._pipe_socket.sendall(request)

        http_response = HTTPResponse(self._pipe_socket)
        http_response.begin()
        response = '%s %s %s\r\n' % (self.request_version, http_response.status, http_response.reason)
        response += '%s\r\n' % http_response.msg
        response += http_response.read()
        
        
        http_response.close()
        self._pipe_socket.close()

        try:
            self.request.sendall(response)
        except Exception, e:
            print 'ERROR request relay: ',e

    def do_GET(self):
        self.do_RELAY()
    
    def do_POST(self):
        self.do_RELAY()
    
    def finish(self):
        try: self._pipe_socket.close()
        except Exception: pass
        BaseHTTPRequestHandler.finish(self)