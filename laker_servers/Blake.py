# BLAKE server implementation
# BLAKE uses port 12970 
# BLAKE talks to BRYANT(12971) and HOWARD(12973)


from twisted.internet.protocol import Factory, ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

import time

class Blake(LineReceiver):
	servername = 'Blake'

	def __init__(self, user_info):
		self.user_info = user_info

	def connectionMade(self):
		self.sendLine("You have connected to Blake server. (debug)")

	#def connectionLost(self, reason):
		# does nothing right now. Might need it later

	def lineReceived(self, line):
		# parse line (either IAMAT or WHATSAT) and send to handler
		params = line.split()
		if len(params) == 0:
			self.handle_MALFORMED(params)
			return

		if params[0] == "WHATSAT":
			self.handle_WHATSAT(params)
		elif params[0] == "IAMAT":
			self.handle_IAMAT(params)
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
		# WHATSAT other_client_id radius_in_km upper_bound_tweet_#
		other_client_id = params[1]
		radius_in_km = params[2]
		upper_bound_tweets = params[3]

		# need to check for malformed input. Not very pythonic, but whatever.
		if not (isinstance(other_client_id,str)):
			self.handle_MALFORMED(params)
			return
		if not isinstance(radius_in_km,(int, long, float)):
			self.handle_MALFORMED(params)
			return
		if not isinstance(upper_bound_tweets,(int,long)):
			self.handle_MALFORMED(params)
			return

		# also, radius must be less than 100.
		if radius_in_km > 100:
			self.handle_MALFORMED(params)
			return

		# here we are going to call the Twitter API to get WHATSAT data

		self.send_AT(time_diff, at_params, json) # send off the AT with a json attached


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

		#cast to string. If positive, need to add a '+' to front. If negative, no need.
		
		if time_diff >= 0:
			td_str = '+' + str(time_diff)
		else: #time_diff < 0
			td_str = str(time_diff)
		
		
		# send off the AT without a json (no query)
		self.send_AT(self.servername, td_str, params[1:], '')
		
		# log the AT in the user_info dict, overwriting if already exists
		# info needed: server talked to, loc, time)
		info = (self.servername, latlong, curr_time)
		self.user_info[client_id] = info
	

	def handle_MALFORMED(self, params): #for when input is malformed
		r = '? ' + ' '.join(params)
		self.sendLine(r)


	def send_AT(self, servername, td_str, params, json):
		msg = 'AT ' + servername + ' ' + td_str + ' ' + ' '.join(params) + json + '\n'
		self.sendLine(msg)



class BlakeFactory(Factory):
	def __init__(self):
		self.user_info = {} # map users based on AT statements

	def buildProtocol(self, addr):
		return Blake(self.user_info)

factory = BlakeFactory()
reactor.listenTCP(12970, factory)
reactor.run()

