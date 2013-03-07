# BLAKE server implementation
# BLAKE uses port 12970 
# BLAKE talks to BRYANT(12971) and HOWARD(12973)


from twisted.internet.protocol import Factory, ClientFactory, ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.python import log
import sys
log.startLogging(sys.stdout)

import time
import twitter # Google Twitter API

class Blake(LineReceiver):

	#client to talk to other servers
	class ServClient(LineReceiver):
		#client is simple: just repeats lines to other server
		def connectionMade(self):
			#TODO: debug
			print "Connected"
			self.sendLine(self.factory.line)
			self.transport.loseConnection()

	class SCFactory(ClientFactory):
		def __init__(self, line):
			self.line = line

	servername = 'Blake'
	hosts = [12971, 12973]
	#initialize our subclient to talk to other servers

	def __init__(self, user_info):
		self.user_info = user_info


	def connectionMade(self):
		self.sendLine("You have connected to Blake server. (debug)")
	def connectionLost(self, reason):
		return

	def lineReceived(self, line):
		#TODO debug
		
		print "Line received!: " + line

		# parse line (either IAMAT or WHATSAT) and send to handler
		params = line.split()
		if len(params) == 0:
			self.handle_MALFORMED(params)
			return

		if params[0] == "WHATSAT":
			self.handle_WHATSAT(params)
		elif params[0] == "IAMAT":
			self.handle_IAMAT(params)
		elif params[0] == "AT": # inter-server communications
			self.handle_AT(params)
		else: #malformed
			self.handle_MALFORMED(params)

	def handle_WHATSAT(self, params):
		#TODO: debug
		self.sendLine("Received input: WHATSAT (debug)")
		
		#check that param input is correct size
		if len(params) != 4:
			self.handle_MALFORMED(params)
			return

		# Format should be 
		# WHATSAT other_client radius_in_km upper_bound_tweets
		try:
			other_client = str(params[1])
			radius_in_km = float(params[2])
			upper_bound_tweets = int(params[3])
		except ValueError:
			self.handle_MALFORMED(params)
			return

		# also, radius must be less than 100.
		if radius_in_km > 100:
			self.handle_MALFORMED(params)
			return

		# check that the user has sent IAMAT data in the past
		if not self.user_info.has_key(other_client):
			self.handle_MALFORMED(params)
			return

		info = self.user_info[other_client]
		servername = info[0]
		latlong = info[1]
		client_time = info[2]

		time_diff = time.time() - client_time

		# here we are going to call the Twitter API to get WHATSAT data

		self.send_AT(servername, time_diff, [other_client,latlong,client_time], json)


	def handle_IAMAT(self, params):
		
		#check that param input is correct size
		if len(params) != 4:
			self.handle_MALFORMED(params)
			return

		# Format should be 
		# IAMAT client_id latlong POSIX_time
		try:
			client_id = str(params[1])
			l = params[2].split('+')[1:]
			latlong = [float(i) for i in l] #hackish way to split up the latlong
			client_time = float(params[3])
		except ValueError:
			self.handle_MALFORMED(params)
			return
	
		# check for proper latlong input	
		if len(latlong) != 2:
			self.handle_MALFORMED(params)
			return

		# need to log the client's data and return with an AT
		
		#get current POSIX time and find diff with client time
		curr_time = time.time()
		time_diff = curr_time - client_time

		
		# send off the AT without a json (no query)
		self.send_AT(self.servername, time_diff, params[1:], '')
		
		# log the AT in the user_info dict, overwriting if already exists
		# info needed: server talked to, loc, time)
		info = (self.servername, latlong, client_time)
		self.user_info[client_id] = info
	
	def handle_AT(self, params):
		try:
			server_name = str(params[1])
			time_diff = float(params[2])
			client_id = str(params[3])
			l = params[4].split('+')[1:]
			latlong = [float(i) for i in l]
			client_time = float(params[5])
		except ValueError:
			self.handle_MALFORMED(params)
			return
		
		
		info = (server_name, latlong, client_time)
		print info
		if self.user_info.has_key(client_id) and self.user_info[client_id] == info:
			return #already exists, so don't send out again.
		else:
			self.user_info[client_id] = info
			self.send_AT(server_name, time_diff, params[3:], '') # flood other servers
			return


	def handle_MALFORMED(self, params): #for when input is malformed
		r = '? ' + ' '.join(params)
		self.sendLine(r)


	def send_AT(self, servername, time_diff, params, json):
		
		if time_diff >= 0:
			td_str = '+' + str(time_diff)
		else: #time_diff < 0
			td_str = str(time_diff)
		msg = 'AT ' + servername + ' ' + td_str + ' ' + ' '.join(params) + json + '\n'
		
		self.sendLine(msg) # send line back to client
		
		if json == '': 
			# indicates that it was not a response to WHATSAT. 
			# Therefore, send the info to other servers
			fact = self.SCFactory(msg)
			fact.protocol = self.ServClient

			for port in self.hosts:
				reactor.connectTCP('localhost', port, fact)




class BlakeFactory(Factory):
	def __init__(self):
		self.user_info = {}
	def buildProtocol(self, addr):
		return Blake(self.user_info)

factory = BlakeFactory()
reactor.listenTCP(12970, factory)
reactor.run()

