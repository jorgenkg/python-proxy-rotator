# Python Proxy Rotator
####An automatic python proxy rotator. (Supports SSL proxies)

##Currently known bugs
* Has currently a static set of proxies and lacks an efficient way to check if the remote proxy server is alive.
* Sometimes CSS documents doesn't load properly on the first tries (probably due to the threaded requests and `asynx="async"` tag in the HTML page.

##Introduction
This is a multithreaded, man-in-the-middle proxy rotator acting as a relay for HTTP-requests. The goal is to make it harder to track you as a web user.

#####Not only is it unnecessarily overkill, but it is also really cool. 

A single webpage includes mulitple files: css, images, scripts and so on. This server creates a news request for each of those objects through a new proxy, making it appear as your request acctually originates for mulitple clients (and potentially multiple countries). By using non-transparent, SSL proxies it will be a tough nut to crack if someone decided to listen to you outgoing data traffic.  

#####Planned features: 
* SOCKS4 and SOCKS5 support
* SMTP, FTP support

##It's not magic
This example describes the life of a HTTP GET/POST request.

![How it works graphics](https://github.com/jorgenkg/python-proxy-rotator/blob/master/magic.png?raw=true)

##Requirements
* `Python with SSL compiled socket.`
* `pyOpenSSL` High-level wrapper around a subset of the OpenSSL library

`$ pip install pyOpenSSL`
	
## Usage
Change directory to the download destination and run:  
`$ python PipeServer.py`


##Kudos
This project is inspired by [pymiproxy](https://github.com/allfro/pymiproxy).  
This project contains the `CertificateAuthority()` defined in `pymiproxy`
