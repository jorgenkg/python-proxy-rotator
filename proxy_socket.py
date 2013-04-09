import socket, sys
from proxier import ProxyManager

DEBUG = True

proxy_fetcher = ProxyManager()
_socket = socket.socket

class ProxySocket(socket.socket):
    def __init__(self, use_ssl=True, chainlength=0, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, _sock=None):
        _socket.__init__(self, family, type, proto, _sock)
        self._chainlength = chainlength
        self.use_ssl=use_ssl
    
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
                print "ERROR http respose from chain: connection returned %d" % statuscode
                return
        except ValueError, e:
            print 'ERROR chaining: - ',e
            self.close()
     
    def connect(self, server):
        info = "\rPath to server:"
        if DEBUG: sys.stdout.write( info )
        sys.stdout.flush()
        

        if self._chainlength == 0:
            info += " (no proxy) %s:%d\n" % server
            if DEBUG: sys.stdout.write( info )
            sys.stdout.flush()
            _socket.connect(self, server)
        else:
            if self.use_ssl or self._chainlength>1:
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
        
        
        
        
        
