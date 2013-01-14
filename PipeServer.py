#!/usr/bin/env python
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import urlparse, urlunparse, ParseResult
from SocketServer import ThreadingMixIn
from httplib import HTTPResponse
from tempfile import gettempdir
from os import path, listdir
from ssl import wrap_socket
from socket import socket, timeout as TimeoutException
from re import compile
from sys import argv
from OpenSSL.crypto import (X509Extension, X509, dump_privatekey, dump_certificate, load_certificate, load_privatekey,
                            PKey, TYPE_RSA, X509Req)
from OpenSSL.SSL import FILETYPE_PEM

import socks
debug = False

class CertificateAuthority(object):

    def __init__(self, ssl_certificate='ca.pem', cache_dir=gettempdir()):
        self.ssl_certificate = ssl_certificate
        self.cache_dir = cache_dir
        self._serial = self._get_serial()
        if not path.exists(ssl_certificate):
            self._generate_ca()
        else:
            self._read_ca(ssl_certificate)

    def _get_serial(self):
        s = 1
        for c in filter(lambda x: x.startswith('.pymp_'), listdir(self.cache_dir)):
            c = load_certificate(FILETYPE_PEM, open(path.sep.join([self.cache_dir, c])).read())
            sc = c.get_serial_number()
            if sc > s:
                s = sc
            del c
        return s

    def _generate_ca(self):
        # Generate key
        self.key = PKey()
        self.key.generate_key(TYPE_RSA, 2048)

        # Generate certificate
        self.cert = X509()
        self.cert.set_version(3)
        self.cert.set_serial_number(1)
        self.cert.get_subject().CN = 'ca.mitm.com'
        self.cert.gmtime_adj_notBefore(0)
        self.cert.gmtime_adj_notAfter(315360000)
        self.cert.set_issuer(self.cert.get_subject())
        self.cert.set_pubkey(self.key)
        self.cert.add_extensions([
            X509Extension("basicConstraints", True, "CA:TRUE, pathlen:0"),
            X509Extension("keyUsage", True, "keyCertSign, cRLSign"),
            X509Extension("subjectKeyIdentifier", False, "hash", subject=self.cert),
            ])
        self.cert.sign(self.key, "sha1")

        with open(self.ssl_certificate, 'wb+') as f:
            f.write(dump_privatekey(FILETYPE_PEM, self.key))
            f.write(dump_certificate(FILETYPE_PEM, self.cert))

    def _read_ca(self, file):
        self.cert = load_certificate(FILETYPE_PEM, open(file).read())
        self.key = load_privatekey(FILETYPE_PEM, open(file).read())

    def __getitem__(self, cn):
        cnp = path.sep.join([self.cache_dir, '.pymp_%s.pem' % cn])
        if not path.exists(cnp):
            # create certificate
            key = PKey()
            key.generate_key(TYPE_RSA, 2048)

            # Generate CSR
            req = X509Req()
            req.get_subject().CN = cn
            req.set_pubkey(key)
            req.sign(key, 'sha1')

            # Sign CSR
            cert = X509()
            cert.set_subject(req.get_subject())
            cert.set_serial_number(self.serial)
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(31536000)
            cert.set_issuer(self.cert.get_subject())
            cert.set_pubkey(req.get_pubkey())
            cert.sign(self.key, 'sha1')

            with open(cnp, 'wb+') as f:
                f.write(dump_privatekey(FILETYPE_PEM, key))
                f.write(dump_certificate(FILETYPE_PEM, cert))

        return cnp

    @property
    def serial(self):
        self._serial += 1
        return self._serial





import threading, collections
class ProxyFetcher():
    http_proxies = collections.deque([
                    (socks.PROXY_TYPE_HTTP, "216.6.146.14", 8080),
                    (socks.PROXY_TYPE_HTTP, "100.42.231.109", 8080),
                    (socks.PROXY_TYPE_HTTP, "66.35.68.146", 3128),
                    (socks.PROXY_TYPE_HTTP, "63.141.249.37", 3128),
                    (socks.PROXY_TYPE_HTTP, "63.141.249.37", 8080),
                    (socks.PROXY_TYPE_HTTP, "198.154.114.100", 8080),
                    (socks.PROXY_TYPE_HTTP, "198.23.128.136", 3128),
                    (socks.PROXY_TYPE_HTTP, "198.154.114.118", 8080),
                    (socks.PROXY_TYPE_HTTP, "66.35.68.145", 3128),
                    (socks.PROXY_TYPE_HTTP, "198.24.131.80", 3128),
                    (socks.PROXY_TYPE_HTTP, "198.23.128.126", 3128),
                    (socks.PROXY_TYPE_HTTP, "76.74.219.138", 3128),
                    (socks.PROXY_TYPE_HTTP, "198.144.176.54", 3128),
                    (socks.PROXY_TYPE_HTTP, "74.221.211.117", 3128),
                    (socks.PROXY_TYPE_HTTP, "37.98.226.66", 8080),
                    (socks.PROXY_TYPE_HTTP, "216.244.71.143", 3128),
                    (socks.PROXY_TYPE_HTTP, "37.143.13.194", 8080)
                ])
    http_sslproxies = collections.deque([
                    (socks.PROXY_TYPE_HTTP, "65.79.56.15", 80),
                    (socks.PROXY_TYPE_HTTP, "82.137.247.134", 80),
                    (socks.PROXY_TYPE_HTTP, "146.12.3.6", 80),
                    (socks.PROXY_TYPE_HTTP, "148.233.159.58", 3128),
                    (socks.PROXY_TYPE_HTTP, "148.233.229.236", 80),
                    (socks.PROXY_TYPE_HTTP, "163.28.80.40", 3128),
                    (socks.PROXY_TYPE_HTTP, "165.228.128.11", 80)
                    
                ])
    
    def __init__(self):
        self.lock = threading.Lock()
        
    def get_proxy(self):
        self.lock.acquire()
        
        random_proxy = self.http_proxies[0]
        self.http_proxies.rotate(1)
        
        self.lock.release()
        return random_proxy
    
    def get_sslproxy(self):
        self.lock.acquire()
        
        random_proxy = self.http_sslproxies[0]
        self.http_sslproxies.rotate(1)
        
        self.lock.release()
        return random_proxy

proxy_fetcher = ProxyFetcher()

class ProxiedRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self.connect_through_ssl = False
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
    
    def _connect_to_host(self):
        if self.connect_through_ssl:
            self.hostname, self.port = self.path.split(':')
        else:
            u = urlparse(self.path)
            if u.scheme != 'http': raise Exception('Unknown scheme %s' % repr(u.scheme))
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
        self._pipe_socket = socks.socksocket()
        self._pipe_socket.settimeout(10)
        self._http_proxy = proxy_fetcher.get_sslproxy() if self.connect_through_ssl else proxy_fetcher.get_proxy()
        self._pipe_socket.setproxy(*self._http_proxy)
        self._pipe_socket.connect(
                            (self.hostname, int(self.port) )
                        )

        # Wrap socket if SSL is required
        if self.connect_through_ssl:
            self._pipe_socket = wrap_socket(self._pipe_socket)

    def do_CONNECT(self):
        self.connect_through_ssl = True
        try:
            self._connect_to_host()
            self.send_response(200, 'Connection established')
            self.end_headers()
            self.wrap_socket(
                            self.request, 
                            server_side = True, 
                            certfile = self.server.ca[ self.path.split(':')[0] ]
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
            except socks.HTTPError, e:
                if retried: self.send_error(e.value[0], e.value[1])
                else: self.do_RELAY(True)
                return
            except TimeoutException, e:
                if retried: self.send_error(504, "Gateway Timeout")
                else: self.do_RELAY(True)
                return
            except Exception, e:
                print type(e)
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


        self.request.sendall(response)

    def do_GET(self):
        self.do_RELAY()
    
    def do_POST(self):
        self.do_RELAY()


class PipeServer(HTTPServer):
    def __init__(self, proxy_fetcher, server_address=('', 8080), ssl_certificate = 'ca.pem'):
        HTTPServer.__init__(self, 
                        server_address, 
                        ProxiedRequestHandler,
                    )
        self.ca = CertificateAuthority(ssl_certificate)


class ThreadedPipeServer(ThreadingMixIn, PipeServer):
    pass
            
if __name__ == '__main__':
    proxy = ThreadedPipeServer(ProxyFetcher())
    try:
        print "Server is running."
        proxy.serve_forever()
    except KeyboardInterrupt:
        print "\nServer is shuting down."
        proxy.server_close()