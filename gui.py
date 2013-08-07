import web
import thread
import socket
import threading
import struct
import hashlib
import base64
import time

render = web.template.render('templates/')
PORT = 8090
clients = []
defaultJarvisText = "hello world, i'm jarvis"
urls = (
	'/', 'index'
)
webSocket = None

class index:
	def GET(self):
		return render.index("hello")

def create_handshake_resp(handshake):
	final_line = ""
	lines = handshake.splitlines()
	print handshake
	for line in lines:
	    parts = line.partition(": ")
	    if parts[0] == "Sec-WebSocket-Key":
	        key = parts[2]


	magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

	accept_key = base64.b64encode(hashlib.sha1(key+magic).digest())

	return (
	    "HTTP/1.1 101 Switching Protocols\r\n"
	    "Upgrade: WebSocket\r\n"
	    "Connection: Upgrade\r\n"
	    "Sec-WebSocket-Accept: " + accept_key + "\r\n\r\n")

def format_resp(data):
    # 1st byte: fin bit set. text frame bits set.
    # 2nd byte: no mask. length set in 1 byte. 
    resp = bytearray([0b10000001, len(data)])
    # append the data bytes
    for d in bytearray(data):
        resp.append(d)
        
    return resp

def handle(s, addr):
	data = s.recv(1024)
	response = create_handshake_resp(data)
	s.sendto(response, addr)
	lock = threading.Lock()
	while 1:
	    print "Waiting for data from", addr
	    data = s.recv(1024)
	    print "Done"
	    if not data:
	        print "No data"
	        break

	    print 'Data from', addr, ':', data

	print 'Client closed:', addr
	lock.acquire()
	clients.remove(s)
	lock.release()
	s.close()

def start_server():
	print 'STARTING WEBSOCKET SERVER ON 8090...'
	s = socket.socket()
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(('', PORT))
	s.listen(1)
	print 'WEBSOCKET SERVER STARTED'
	while 1:
	    conn, addr = s.accept()
	    print 'NEW CONNECTION ['+str(len(clients))+'], connected by ', addr
	    clients.append(conn)
	    threading.Thread(target = handle, args = (conn, addr)).start()

def sendToBrowser(sendToString):
	listOfWords = sendToString.split()
	speechList = []
	print listOfWords
	for word in listOfWords:
		if len(speechList) == 0 or len(speechList[len(speechList)-1].split()) == 4:
			speechList.append(word)
		else:
			for i in range(0, len(speechList)):
				if len(speechList[i].split()) < 4:
					speechList[i] += " " + word
				i+=1

	for text in speechList:
		for conn in clients:
			conn.send(format_resp(text))
		if speechList[len(speechList)-1] == text:
			time.sleep(4)
		else:
			time.sleep(2)

	for conn in clients:
		conn.send(format_resp(defaultJarvisText)) 

def startAllServers():
    app = web.application(urls, globals())
    print 'STARTING HTTP SERVER ON 8080'
    thread.start_new_thread(app.run, ())
    start_server()
 	