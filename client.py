import socket

connection = ("localhost",9998)

sock = socket.socket(
			socket.AF_INET,
			socket.SOCK_STREAM
		)

message = 'terminate_server'

try:
	sock.connect(connection)
	sock.sendall(message)
	response = sock.recv(1024)
	
	print "Received: {}".format(response)
finally:
	sock.close()