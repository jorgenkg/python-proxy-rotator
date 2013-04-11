import socket, sys, select
from proxier import ProxyManager

class ProxySocket(socket.socket):
    def __init__(self, proxy_fetcher, use_ssl=True, chainlength=0, DEBUG=False, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, _sock=None):
        socket.socket.__init__(self, family, type, proto, _sock)
        self._chainlength = int(chainlength)
        self.use_ssl=True#use_ssl
        self._proxy_fetcher = proxy_fetcher
        self.DEBUG = DEBUG
    
    def __chainconnect_server(self, proxy):
        remote = proxy[0] if proxy[0].startswith('www') else '%s:%d' % proxy
        self.sendall("CONNECT %s HTTP/1.0\r\n\r\n" % remote)
        
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
                self._proxy_fetcher.remove_proxy(proxy)
                return
        except ValueError, e:
            sys.stdout.write( 'ERROR chaining: '+str(e) )
            sys.stdout.flush()
            self.close()
     
    def connect(self, server):
        info = "\rPath to server:"
        if self.DEBUG: sys.stdout.write( info )
        sys.stdout.flush()

        if self._chainlength == 0:
            info += " (no proxy) %s:%d\n" % server
            if self.DEBUG: sys.stdout.write( info )
            sys.stdout.flush()
            socket.socket.connect(self, server)
        else:
            if self.use_ssl or self._chainlength>1:
                info += " https -->" 
                self.__https_proxies = self._proxy_fetcher.get_sslproxy( self._chainlength )
                if self.DEBUG: sys.stdout.write( info )
                sys.stdout.flush()
                socket.socket.connect( self, self.__https_proxies.pop())
                for proxy in self.__https_proxies:
                    info += " https -->"
                    if self.DEBUG: sys.stdout.write( info )
                    sys.stdout.flush()
                    self.__chainconnect_server(proxy)        
            else:
                info += " http -->" 
                if self.DEBUG: sys.stdout.write( info )
                sys.stdout.flush()
                socket.socket.connect(self, self._proxy_fetcher.get_proxy())
        
            # dest
            info += " %s:%d\n" % server
            if self.DEBUG: sys.stdout.write( info )
            sys.stdout.flush()
            self.__chainconnect_server(server)
        
        
        
        
        
