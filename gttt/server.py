from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import sys

class GTTTRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('content-type','text/html')
		self.end_headers()
		if (self.path=="/" or self.path=="/version"):
			self.wfile.write("The is the version: 1.0.0")
		print self.path
		sys.stdout.flush()


try:
	#Create a web server and define the handler to manage the
	#incoming request
	PORT_NUMBER=8080
	server = HTTPServer(('', PORT_NUMBER), GTTTRequestHandler)
	print 'Started httpserver on port ' , PORT_NUMBER
	sys.stdout.flush()
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()