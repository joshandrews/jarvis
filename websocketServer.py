from websocket import create_connection

import web, thread

render = web.template.render('templates/')

urls = (
	'/', 'index'
)

class index:
	def GET(self):
		return render.index("hello")

def startWebsocket():
	ws = create_connection("ws://localhost:8090")
	print "Sending 'Hello, World'..."
	ws.send("Hello, World")
	print "Sent"
	print "Reeiving..."
	result =  ws.recv()
	print "Received '%s'" % result
	ws.close()

if __name__ == "__main__":
    app = web.application(urls, globals())
    thread.start_new_thread(app.run, ())
    startWebsocket()