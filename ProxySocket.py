import threading, collections
from httplib import HTTPResponse

class PROXY_HTTP: pass
class PROXY_HTTPS: pass

class ProxyFetcher():
    http_proxies = collections.deque([
                    (PROXY_HTTP, "79.99.6.168", 80),
                    (PROXY_HTTP, "80.63.56.146", 8118),
                    (PROXY_HTTP, "157.125.68.42", 80)
                ])
    http_sslproxies = collections.deque([
                    (PROXY_HTTPS, "109.74.134.246", 3128),
                ])
    
    def __init__(self):
        self.lock = threading.Lock()
    
    def get_proxy(self):
        self.lock.acquire()
        
        random_proxy = self.http_sslproxies[0]
        self.http_proxies.rotate(1)
        
        self.lock.release()
        return random_proxy
    
    def get_sslproxy(self, count=1):
        if count <= 0: return [ ]
        self.lock.acquire()
        
        random_proxy = self.http_sslproxies[:count] if count > 1 else self.http_sslproxies[0]
        self.http_sslproxies.rotate(count)
        
        self.lock.release()
        return random_proxy

proxy_fetcher = ProxyFetcher()

import socket

_socket = socket.socket

class ProxySocket(socket.socket):
    def __init__(self, chainlength=1, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, _sock=None):
        _socket.__init__(self, family, type, proto, _sock)
        self._chainlength = chainlength
        
    def connect(self, server):
        if self._chainlength > 1:
            print "* using HTTPS chaining"
            self.__https_proxies = proxy_fetcher.get_sslproxy(self._chainlength-1)
        
            _socket.connect(self, self.__https_proxies.pop())
            
            for proxy in self.__https_proxies:
                self.sendall("CONNECT %s:%d HTTP/1.1\r\n\r\n" % proxy[1:])
                
                resp = self.recv(1)
                while resp.find("\r\n\r\n")==-1:
                    resp = resp + self.recv(1)
                statusline = resp.splitlines()[0].split(" ",2)
                
                try:
                    statuscode = int(statusline[1])
                except ValueError, e:
                    print e
                    self.close()
                if statuscode != 200:
                    print "CONNECTION ERROR."
                    self.close()
        # end https proxies
        
        if self._chainlength > 0:
            print "* using http proxy --> %s:%d" % server
            _socket.connect(self, proxy_fetcher.get_proxy()[1:])
            
            """
            Connect to dest
            """
            self.sendall("CONNECT %s:%d HTTP/1.1\r\n\r\n" % server)
                
            resp = self.recv(1)
            while resp.find("\r\n\r\n")==-1:
                resp = resp + self.recv(1)
            statusline = resp.splitlines()[0].split(" ",2)
            
            try:
                statuscode = int(statusline[1])
            except ValueError, e:
                print e
                self.close()
            if statuscode != 200:
                print "CONNECTION ERROR."
                self.close()
        # end http proxies
        else:
            print "connecting directly to server: %s:%d" % server
            _socket.connect(self, server)
            print "connected."
            resp = self.recv(1)
            while resp.find("\r\n\r\n")==-1:
                resp = resp + self.recv(1)
            statusline = resp.splitlines()[0].split(" ",2)
            
            try:
                statuscode = int(statusline[1])
            except ValueError:
                self.close()
            if statuscode != 200:
                print "CONNECTION ERROR."
                self.close()
            
        
        
        
        
