# METTA server implementation
# METTA uses port 12375
# METTA talks to BRYANT(12372)


from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

class Chat(LineReceiver):
	
	def __init__(self, users):
		self.users = users
		self.name = None
		self.state = "GETNAME"

	def connectionMade(self):
		self.sendLine("What's your name?")

	def connectionLost(self, reason):
		if self.users.has_key(self.name): #it should
			del self.users[self.name]
	
	def lineReceived(self, line):
		if line=="logout": #drop user 
			self.transport.loseConnection()
		if line=="STEVEFRENCH": #standard kill
			reactor.stop()

		if self.state == "GETNAME":
			self.handle_GETNAME(line) #init
		else:
			self.handle_CHAT(line)

	def handle_GETNAME(self, name):
		if self.users.has_key(name):
			self.sendLine("Name taken, please choose another.")
			return
		self.sendLine("Welcome, %s!" % (name,))
		self.name = name
		self.users[name] = self
		self.state = "CHAT"

	def handle_CHAT(self, message):
		message = "<%s> %s" % (self.name, message)
		for name, protocol in self.users.iteritems():
			if protocol != self:
				protocol.sendLine(message)

class ChatFactory(Factory):
	def __init__(self):
		self.users = {} # we map user names to chat instances
	
	def buildProtocol(self, addr):
		return Chat(self.users)

reactor.listenTCP(12371, ChatFactory())
reactor.run()

