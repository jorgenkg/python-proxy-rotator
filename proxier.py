import threading, collections, sys, socket


class ProxyManager():
    
    def __init__(self):
        self.lock = threading.Lock()
        self.is_connected = False
        self.http_proxies = collections.deque()
        self.https_proxies = collections.deque()
        # load from file
        self._load_proxies()
    
    def _print_progress(self, fraction):
        size = 50
        progress = int(round(size * fraction))
        string = "="*progress+" "*int(size-progress)
        
        if progress == size: sys.stdout.write("\r[%s]\n" % string)
        else: sys.stdout.write("\r[%s]" % string)
        sys.stdout.flush()
    
    def _load_proxies(self):
        print 'Check for proxy liveliness...'
        
        file = open('proxylist.txt','r').readlines()
        for index,entry in enumerate(file):
            self._print_progress( (index+1)/float(len(file)) )
            entry = (entry.split(":")[0],int(entry.split(":")[1]))
            alive,chaining = self._check_proxy(
                        entry
                    )
            if alive:
                if chaining:
                    self.https_proxies.append( entry )
                else:
                    self.http_proxies.append( entry )
        print len(self.https_proxies),' HTTPS proxies'
        print len(self.http_proxies),' HTTP proxies'
            
        
    def _test_CONNECT(self, test_server='www.vg.no', _level=1):
        if self.is_connected:
            self._socket.sendall("CONNECT %s HTTP/1.0\r\n\r\n" % test_server)
            
            try:
                resp = self._socket.recv(1)
                while resp.find("\r\n\r\n")==-1:
                    resp = resp + self._socket.recv(1)
                statusline = resp.splitlines()[0].split(" ",2)
            except socket.error:
                return False
        
            try:
                statuscode = int(statusline[1])
                return (statuscode == 200)
            except ValueError, e:
                print 'ERROR chaining: - ',e
                self._socket.close()
        return False
    
    def _test_alive(self, server):
        self.is_connected = False
        self._socket.settimeout(1.5)
        try:
            self._socket.connect(server)
            self.is_connected = True
        except (socket.timeout, socket.error):
            return False
        return True
        
    
    def _check_proxy(self, server):
        self._socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        
        alive = self._test_alive(server)
        chaining = self._test_CONNECT()

        self._socket.close()
        return (alive, chaining)
    
    def get_proxy(self):
        self.lock.acquire()
        
        random_proxy = self.http_proxies[0]
        self.http_proxies.rotate(1)
        
        self.lock.release()
        return random_proxy
    
    def get_sslproxy(self, count=1):
        if count <= 0: return [ ]
        self.lock.acquire()
        
        random_proxy = [self.https_proxies.pop() for i in range(count)]
        self.https_proxies.extendleft(random_proxy)
        
        
        self.lock.release()
        return random_proxy