import socket, sys, select
from proxier import ProxyManager

DEBUG = True

class ProxySocket(socket.socket):
    def __init__(self, proxy_fetcher, use_ssl=True, chainlength=0, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, _sock=None):
        socket.socket.__init__(self, family, type, proto, _sock)
        self._chainlength = chainlength
        self.use_ssl=True#use_ssl
        self._proxy_fetcher = proxy_fetcher
    
    def __chainconnect_server(self, proxy):
        self.sendall("CONNECT %s:%d HTTP/1.0\r\n\r\n" % proxy)
        
        resp = self.recv(1)
        while resp.find("\r\n\r\n")==-1:
            resp = resp + self.recv(1)
        statusline = resp.splitlines()[0].split(" ",2)
    
        try:
            statuscode = int(statusline[1])
        
            if statuscode==200: 
                return
            else:
                print  "ERROR http respose from chain: connection returned %d" % statuscode
                print "telnet %s %d" % self.getpeername()
                print "CONNECT %s:%d HTTP/1.0\r\n\r\n" % proxy
                self._proxy_fetcher.remove_proxy(proxy)
                return
        except ValueError, e:
            sys.stdout.write( 'ERROR chaining: '+str(e) )
            sys.stdout.flush()
            self.close()
     
    def connect(self, server):
        info = "\rPath to server:"
        if DEBUG: sys.stdout.write( info )
        sys.stdout.flush()
        

        if self._chainlength == 0:
            info += " (no proxy) %s:%d\n" % server
            if DEBUG: sys.stdout.write( info )
            sys.stdout.flush()
            socket.socket.connect(self, server)
        else:
            if self.use_ssl or self._chainlength>1:
                info += " https -->" 
                self.__https_proxies = self._proxy_fetcher.get_sslproxy( self._chainlength )
                if DEBUG: sys.stdout.write( info )
                sys.stdout.flush()
                socket.socket.connect( self, self.__https_proxies.pop())
                for proxy in self.__https_proxies:
                    info += " https -->"
                    if DEBUG: sys.stdout.write( info )
                    sys.stdout.flush()
                    self.__chainconnect_server(proxy)        
            else:
                info += " http -->" 
                if DEBUG: sys.stdout.write( info )
                sys.stdout.flush()
                socket.socket.connect(self, self._proxy_fetcher.get_proxy())
        
            # dest
            info += " %s:%d\n" % server
            if DEBUG: sys.stdout.write( info )
            sys.stdout.flush()
            self.__chainconnect_server(server)
        
        
        
        
        
