from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import sys
import os
import psycopg2
import urlparse

urlparse.uses_netloc.append("postgres")
db_url = urlparse.urlparse(os.environ["DATABASE_URL"])



class GTTTRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('content-type','text/html')
		self.end_headers()
		if (self.path=="/" or self.path=="/version"):
			self.wfile.write("1.0.0")
		elif self.path=="/submit_hiscore":
			self.wfile.write("Send me your hiscores")
		elif self.path=="/get_hiscore":
			self.wfile.write("Have some delicious hiscores")
			hiscore_string=get_hiscores(1)
			print hiscore_string
			self.wfile.write("\n"+hiscore_string)
		else:
			self.wfile.write("BOI WHY U B HERE")
		print self.path
		sys.stdout.flush()

	def get_hiscores(self,level):
		db_conn = psycopg2.connect(
    		database=db_url.path[1:],
    		user=db_url.username,
    		password=db_url.password,
    		host=db_url.hostname,
    		port=db_url.port
		)
		cur=db_conn.cursor()
		cur.execute("CREATE TABLE LVL"+str(level)+" (id serial PRIMARY KEY,time float);")
		cur.execute("INSERT INTO LVL"+str(level)+" (time) VALUES 3")
		cur.execute("SELECT * FROM LVL"+str(level)+" ORDER BY time ASC;")
		#select from lvl x and sort by time asc
		hiscores=cur.fetchall()
		
		db_conn.commit()
		cur.close()
		db_conn.close()
		#convert to string
		hiscore_string=""
		for hiscore in hiscores:
			hiscore_string+=str(hiscore[1])+"\n"
		return hiscore_string

try:
	#Create a web server and define the handler to manage the
	#incoming request
	PORT_NUMBER=int(sys.argv[1])
	server = HTTPServer(('', PORT_NUMBER), GTTTRequestHandler)
	print 'Started httpserver on port ' , PORT_NUMBER
	sys.stdout.flush()
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()