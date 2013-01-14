# Python Proxy Rotator
####An automatic python proxy rotator.

##Introduction
***
This is a multithreaded, man-in-the-middle proxy rotator acting as a relay for HTTP-requests. The goal is to make it harder to track you as a web user.  

##It's not magic
***
This expamle describes the life of a HTTP GET request.

![How it works graphics](https://github.com/jorgenkg/python-proxy-rotator/blob/master/magic.png?raw=true)

The server recieves a 
##Requirements
***
1. `Python 2.5 +`
2. `SocksiPy`
> This module was designed to allow developers of Python software that uses the Internet or another TCP/IP-based 
>network to add support for connection through a SOCKS proxy server with as much ease as possible.

	`$ pip install SocksiPy`
	
## Useage
***
Change directory to the download destination and run:  
`$ python PipeServer.py`


##Kudos
***
This project is inspired by [pymiproxy](https://github.com/allfro/pymiproxy).
