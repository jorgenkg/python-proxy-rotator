import threading, collections
import socket

class PROXY_HTTP: pass
class PROXY_HTTPS: pass

DEBUG = True

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
        
        random_proxy = [self.http_sslproxies.pop() for i in range(count)]
        self.http_sslproxies.extendleft(random_proxy)
        
        self.lock.release()
        return random_proxy

proxy_fetcher = ProxyFetcher()



_socket = socket.socket
class ProxySocket(socket.socket):
    def __init__(self, chainlength=2, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, _sock=None):
        _socket.__init__(self, family, type, proto, _sock)
        self._chainlength = chainlength
    
    def __chainconnect_server(self, proxy):
        self.sendall("CONNECT %s:%d HTTP/1.1\r\n\r\n" % proxy)
        
        resp = self.recv(1)
        while resp.find("\r\n\r\n")==-1:
            resp = resp + self.recv(1)
        statusline = resp.splitlines()[0].split(" ",2)
        
        try:
            if int(statusline[1]) == 200: return True
        except ValueError, e:
            print e
            self.close()
        if statuscode != 200:
            self.close()
            print "ERROR: connection returned %d" % statuscode
        return False
     
    def connect(self, server):
        if DEBUG:
            tmp = int(self._chainlength)-1
            desired_path = "https proxy --> " * tmp
            desired_path += "http proxy --> " if self._chainlength>=1 else ""
            desired_path += "%s:%d" % server
            print "Path to server: %s" % desired_path
        
        if self._chainlength == 0:
            _socket.connect(self, server)
            return
        
        if self._chainlength > 1:    
            # https
            self.__https_proxies = proxy_fetcher.get_sslproxy( self._chainlength-1 )
            _socket.connect( self, self.__https_proxies.pop()[1:])
            # ad hoc
            for proxy in self.__https_proxies:
                self.__chainconnect_server(proxy[1:])
                
        elif self._chainlength == 1:
            # http
            _socket.connect(self, proxy_fetcher.get_proxy()[1:])
        # dest
        self.__chainconnect_server(server)
        
        
        
        
        
