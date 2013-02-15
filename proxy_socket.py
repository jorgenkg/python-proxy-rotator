import threading, collections
import socket, sys

DEBUG = True
USE_SSL = False

class ProxyFetcher():
    http_proxies = collections.deque([
                    ("107.18.121.126", 8080), # dead
                ])
    http_sslproxies = collections.deque([
                    ("74.221.211.117", 8080), # dead
                ])
    
    def test_proxies(self):
        pass
    
    def _test_CONNECT(self, proxy):
        pass
    
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
    def __init__(self, use_ssl=False, chainlength=0, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, _sock=None):
        _socket.__init__(self, family, type, proto, _sock)
        self._chainlength = chainlength
        USE_SSL = use_ssl
    
    def __chainconnect_server(self, proxy):
        self.sendall("CONNECT %s:%d HTTP/1.1\r\n\r\n" % proxy)
        
        resp = self.recv(1)
        while resp.find("\r\n\r\n")==-1:
            resp = resp + self.recv(1)
        statusline = resp.splitlines()[0].split(" ",2)
        
        try:
            statuscode = int(statusline[1])
            
            if statuscode==200: 
                return
            else:
                self.close()
                print "ERROR: connection returned %d" % statuscode
                return
        except ValueError, e:
            print e
            self.close()
     
    def connect(self, server):
        info = "\rPath to server:"
        if DEBUG: sys.stdout.write( info )
        sys.stdout.flush()
        
        if self._chainlength == 0:
            info += " %s:%d\n" % server
            if DEBUG: sys.stdout.write( info )
            sys.stdout.flush()
            _socket.connect(self, server)
            return
        
        if self._chainlength > 0 and USE_SSL:   
            info += " https -->" 
            self.__https_proxies = proxy_fetcher.get_sslproxy( self._chainlength )
            if DEBUG: sys.stdout.write( info )
            sys.stdout.flush()
            _socket.connect( self, self.__https_proxies.pop())
            for proxy in self.__https_proxies:
                info += " https -->"
                if DEBUG: sys.stdout.write( info )
                sys.stdout.flush()
                self.__chainconnect_server(proxy)        
        else:
            info += " http -->" 
            if DEBUG: sys.stdout.write( info )
            sys.stdout.flush()
            _socket.connect(self, proxy_fetcher.get_proxy())
        
        # dest
        info += " %s:%d\n" % server
        if DEBUG: sys.stdout.write( info )
        sys.stdout.flush()
        self.__chainconnect_server(server)
        
        
        
        
        
