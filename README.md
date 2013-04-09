#Python Proxy Rotator
####An automatic python proxy rotator. (Supports SSL proxies)

##Currently known bugs
* Has currently a static set of proxies and lacks an efficient way to check if the remote proxy server is alive.
* You may experience various "server errors" due to unstable proxy servers

##Introduction
This is a multithreaded, man-in-the-middle proxy rotator acting as a relay for HTTP-requests. The goal is to make it harder to track you as a web user.

#####Not only is it unnecessarily overkill, but it is also really cool. 

A single webpage includes mulitple files: css, images, scripts and so on. This server creates a new request for each and everyone of those objects through a new proxy, making it appear as your request acctually originates for mulitple clients ("omni browsing"). By using non-transparent SSL proxies, this will be a tough nut to crack if someone decided to listen to you outgoing data traffic.  

#####Planned features: 
* SOCKS4 and SOCKS5 support
* SMTP support

####Current features: 
* FTP support
* HTTP & HTTPS support
* Proxy chaining (technically limited to only HTTPS proxies)
* Accepts globally trusted certificates
* Correctly handles SSL
* Ability to act as a SSL Certificate Authority (for the locally recieved requests)
* Lets the browser/user decide whether to use HTTPS or not. This is a necessary feature due to the fact that not all servers support SSL encryption. And there is no reason to encrypt the data yourself, if your HTTPS proxy decrypts the data before it reaches the goal.

##It's not magic
This example describes the life of a HTTP GET/POST request.

![How it works graphics](https://github.com/jorgenkg/python-proxy-rotator/blob/master/magic.png?raw=true)

##Requirements
* `Python with SSL compiled socket.`
* `pyOpenSSL` High-level wrapper around a subset of the OpenSSL library

`$ pip install pyOpenSSL`
	
## Usage
Change directory to the download destination and run:  
```bash
$ python badger.py [-n repetitions]

OPTIONS
-p, --local_proxies				# default operation
-f, --force_proxy_refresh		# force the program to reverify the proxies 
-n CHAINLENGTH, --chainlength CHAINLENGTH # number of servers to bounce through
```

Set `127.0.0.1:8080` as the proxy in your favourite browser.

##Kudos
This project is inspired by [pymiproxy](https://github.com/allfro/pymiproxy).  
This project contains the `CertificateAuthority()` defined in `pymiproxy`
