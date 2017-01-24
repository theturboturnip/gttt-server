from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import sys
import os
import psycopg2
import urlparse,traceback

urlparse.uses_netloc.append("postgres")
try:
	db_url = urlparse.urlparse(os.environ["DATABASE_URL"])
except:
	pass
port = int(os.environ["PORT"])
print (port)
sys.stdout.flush()



class GTTTRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('content-type','text/html')
		self.end_headers()
		split_path=filter(None,self.path.split("/"))
		if (split_path==[] or split_path[0]=="version"):
			self.wfile.write("1.0.0")
		elif split_path[0]=="submit_time" and len(split_path)>=4:
			level=split_path[1]
			ip=split_path[2]
			time=float(split_path[3])
			try:
				if self.add_level_time(level,time,ip):
					self.wfile.write("Added time "+str(time)+" to ip "+ip+" on level "+str(level))
				else:
					self.wfile.write("Didn't add time, probably because it was longer than before")
			except:
				self.wfile.write("Failed to add time, something went wrong")
				traceback.print_exc()
				print "FAILED TO ADD TIME"

			#interpret 
		elif split_path[0]=="get_times":
			self.wfile.write("Have some delicious hiscores")
			hiscore_string=self.get_level_times(split_path[1])
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
		#"""try:
		#	cur.execute("CREATE TABLE LVL"+str(level)+" (id serial PRIMARY KEY,ip varchar,time float);")
		#	#cur.execute("INSERT INTO LVL"+str(level)+" (time) VALUES (3)")
		#except ProgrammingError:
		#cur.execute("SELECT * FROM LVL"+str(level)+" ORDER BY time ASC;")"""
		try:
			cur.execute("CREATE TABLE IF NOT EXISTS TIMES (id serial PRIMARY KEY,ip varchar,LVL1 float,LVL2 float,LVL3 float);")
			#cur.execute("INSERT INTO LVL"+str(level)+" (time) VALUES (3)")
		except:
			pass #the table already existed
		cur.execute("SELECT LVL"+str(level)+" FROM TIMES ORDER BY LVL"+str(level)+" ASC;")
		#select from lvl x and sort by time asc
		hiscores=cur.fetchall()
		
		db_conn.commit()
		cur.close()
		db_conn.close()
		#convert to string
		hiscore_string=""
		for hiscore in hiscores:
			hiscore_string+=str(hiscore[0])+"\n"
		return hiscore_string

	def get_level_times(self,level):
		db_conn = psycopg2.connect(
    		database=db_url.path[1:],
    		user=db_url.username,
    		password=db_url.password,
    		host=db_url.hostname,
    		port=db_url.port
		)
		cur=db_conn.cursor()
		try:
			cur.execute("CREATE TABLE IF NOT EXISTS TIMES (id serial PRIMARY KEY,IP varchar,LEVEL varchar, time float);")
			#cur.execute("INSERT INTO LVL"+str(level)+" (time) VALUES (3)")
		except:
			pass #the table already existed
		#cur.execute("SELECT PROC-"+procgen_seed+" FROM TIMES")
		#if (cur.fetchone() is None):
		#	cur.execute("ALTER TABLE TIMES ADD PROC-"+procgen_seed+" float")
		cur.execute("SELECT * FROM TIMES WHERE LEVEL=\'"+level+"\' ORDER BY time ASC;")
		#select from lvl x and sort by time asc
		hiscores=cur.fetchall()
		
		db_conn.commit()
		cur.close()
		db_conn.close()
		#convert to string
		hiscore_string=""
		for hiscore in hiscores:
			hiscore_string+=str(hiscore[2])+"\n"
		return hiscore_string

	def add_level_time(self,level,time,ip):
		db_conn = psycopg2.connect(
    		database=db_url.path[1:],
    		user=db_url.username,
    		password=db_url.password,
    		host=db_url.hostname,
    		port=db_url.port
		)
		cur=db_conn.cursor()
		cur.execute("CREATE TABLE IF NOT EXISTS TIMES (id serial PRIMARY KEY,IP varchar,LEVEL varchar, time float);")
		cur.execute("SELECT * FROM TIMES WHERE IP=\'"+ip+"\' AND LEVEL=\'"+level+"\';")
		player_row=cur.fetchone()
		to_return=True
		if player_row is None:
			cur.execute("INSERT INTO TIMES (IP,LEVEL,time) VALUES (\'"+ip+"\',\'"+level+"\',"+str(time)+");")
		elif player_row[2]>time:
			cur.execute("UPDATE TIMES SET time="+str(time)+" WHERE IP=\'"+ip+"\' AND LEVEL=\'"+level+"\';")
		else:
			to_return=False
		db_conn.commit()
		cur.close()
		db_conn.close()
		return to_return

	def add_procgen_hiscore(self,procgen_seed,time,ip):
		db_conn = psycopg2.connect(
    		database=db_url.path[1:],
    		user=db_url.username,
    		password=db_url.password,
    		host=db_url.hostname,
    		port=db_url.port
		)
		cur=db_conn.cursor()
		try:
			cur.execute("CREATE TABLE IF NOT EXISTS TIMES (id serial PRIMARY KEY,IP varchar,LVL1 float,LVL2 float,LVL3 float);")
			#cur.execute("INSERT INTO LVL"+str(level)+" (time) VALUES (3)")
		except:
			pass #the table already existed
		cur.execute("SELECT PROC-"+procgen_seed+" FROM TIMES")
		if (cur.fetchone() is None):
			cur.execute("ALTER TABLE TIMES ADD PROC-"+procgen_seed+" float")
		cur.execute("SELECT PROC-"+procgen_seed+" FROM TIMES WHERE IP=\'"+ip+"\';")
		player_row=cur.fetchone()
		if player_row is None:
			cur.execute("INSERT INTO TIMES (IP,PROC-"+procgen_seed+") VALUES (\'"+ip+"\',"+str(time)+");")
		elif player_row[0]>time:
			cur.execute("UPDATE TIMES SET PROC-"+procgen_seed+"="+str(time)+" WHERE IP='"+ip+"';")
		db_conn.commit()
		cur.close()
		db_conn.close()


try:
	#Create a web server and define the handler to manage the
	#incoming request
	PORT_NUMBER=int(sys.argv[1])
	if PORT_NUMBER<0:
		PORT_NUMBER=port
	server = HTTPServer(('', PORT_NUMBER), GTTTRequestHandler)
	print 'Started httpserver on port' , PORT_NUMBER
	sys.stdout.flush()
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()