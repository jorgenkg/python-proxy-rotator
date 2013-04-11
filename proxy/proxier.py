import threading, collections, sys, socket, os, select, threading
from tempfile import gettempdir

class ProxyManager():
    
    def __init__(self, check_for_tmp):
        self.lock = threading.Lock()
        self.killer = threading.Lock()
        self.is_connected = False
        self.http_proxies = collections.deque()
        self.https_proxies = collections.deque()
        
        # load from file
        #threading.Thread( target=self._load_proxies, args=(self.lock,self.killer,check_for_tmp)).start()
        self._load_proxies(self.lock,self.killer,check_for_tmp)
    
    def _print_progress(self, fraction):
        size = 50
        progress = int(round(size * fraction))
        string = "="*progress+" "*int(size-progress)
        
        if fraction == 1: sys.stdout.write("\r[%s] Done!       \n" % string)
        else: sys.stdout.write("\r[%s] Loading..." % string)
        sys.stdout.flush()
    
    def _load_proxies(self, _lock, _killer, check_for_tmp=True):
        if check_for_tmp and os.path.exists(os.path.join(gettempdir(),'py_http_proxies.txt')):
            print 'Loading proxies from local tmp...'
            
            file = open(os.path.join(gettempdir(),'py_http_proxies.txt'),'r').readlines()
            for entry in file:
                entry = ( entry.split(":")[0], int(entry.split(":")[1]) )
                _lock.acquire()
                self.http_proxies.append( entry )
                _lock.release()
            
            file = open(os.path.join(gettempdir(),'py_https_proxies.txt'),'r').readlines()
            for entry in file:
                entry = ( entry.split(":")[0], int(entry.split(":")[1]) )
                _lock.acquire()
                self.https_proxies.append( entry )
                _lock.release()
        else:
            print 'Loading proxies from proxylist.txt ...'
            
            file = open(os.path.join(os.getcwd(),'proxy/proxylist.txt'),'r').readlines()
            dead = []
            for index,entry in enumerate(file):
                if _killer.locked(): break
                self._print_progress( (index+1)/float(len(file)) )
                entry = ( entry.split(":")[0], int(entry.split(":")[1]) )
                alive,chaining = self._check_proxy( entry )
                if alive:
                    _lock.acquire()
                    if chaining: self.https_proxies.append( entry )
                    else: self.http_proxies.append( entry )
                    _lock.release()
                else: dead.append(entry)
    
            print "Dead proxies: "
            for d in dead: print d[0]
        
            log = open(os.path.join(gettempdir(),'py_http_proxies.txt'),'w')
            _lock.acquire()
            for p in self.http_proxies:
                log.write('%s:%d\n' % p)
            _lock.release()
            log.close()
        
            log = open(os.path.join(gettempdir(),'py_https_proxies.txt'),'w')
            _lock.acquire()
            for p in self.https_proxies:
                log.write('%s:%d\n' % p)
            _lock.release()
            log.close()
        
        _lock.acquire()
        print len(self.https_proxies),' HTTPS proxies with chain support'
        print len(self.http_proxies),' HTTP proxies'
        _lock.release()
        
    def _test_CONNECT(self, _socket, test_server='www.vg.no'):
        if self.is_connected:
            _socket.setblocking(0)
            try:
                _socket.sendall("CONNECT %s HTTP/1.0\r\n\r\n" % test_server )
                ready = select.select([_socket], [], [], 4)
                if ready[0]:
                    resp = _socket.recv(1)
                    while resp.find("\r\n\r\n")==-1:
                        tmp = resp
                        resp = resp + _socket.recv(1)
                        if tmp == resp: raise socket.error
                    statusline = resp.splitlines()[0].split(" ",2)
                
                    statuscode = int(statusline[1])
                    return (statuscode == 200)
            except socket.error: pass
            except ValueError, e: print 'ERROR chaining: ',e
        return False
    
    def _test_alive(self, _socket, server):
        self.is_connected = False
        try:
            _socket.connect(server)
            self.is_connected = True
        except (socket.timeout, socket.error): return False
        return True
    
    def _check_proxy(self, server, _no_chain=False):
        self._socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self._socket.settimeout(1.5)
        
        if _no_chain: return self._test_alive(self._socket, server)
        
        alive = self._test_alive(self._socket, server)
        chaining = self._test_CONNECT(self._socket)

        self._socket.close()
        return (alive, chaining)
    
    def get_proxy(self):
        self.lock.acquire()
        
        random_proxy = self.http_proxies[0]
        self.http_proxies.rotate(1)
        
        self.lock.release()
        return random_proxy
    
    def get_sslproxy(self, count=1):
        self.lock.acquire()
        
        if count <= 0: return [ ]
        if count > len(self.https_proxies): count = len(self.https_proxies)
        
        random_proxy = [self.https_proxies.pop() for i in range(count)]
        self.https_proxies.extendleft(random_proxy)
        
        
        self.lock.release()
        return random_proxy
    
    def remove_proxy(self, proxy):
        self.lock.acquire()
        for i,p in enumerate(self.https_proxies):
            if proxy[0] == p[0]: self.https_proxies.remove(p)
        for i,p in enumerate(self.http_proxies):
            if proxy[0] == p[0]: self.http_proxies.remove(p)
        self.lock.release()
    
    def terminate(self):
        self.killer.acquire()