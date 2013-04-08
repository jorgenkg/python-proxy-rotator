import threading, collections

class ProxyFetcher():
    http_proxies = collections.deque([
                    ("76.191.98.246", 8085),
                ])
    http_sslproxies = collections.deque([
                    #("50.7.99.156", 3128),
                    ("192.161.49.25", 3128)
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