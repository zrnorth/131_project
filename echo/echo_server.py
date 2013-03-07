"""
Basic echo server. Takes any input and repeats it back to the user.
"""

from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor

### Protocol implementation

# simplest possible protocol. Echo back anything given

class Echo(Protocol): #extends Protocol
	def dataReceived(self, data):
		self.transport.loseConnection()

def main():
	f = Factory()
	f.protocol = Echo
	reactor.listenTCP(12371,f)
	reactor.run()

if __name__== '__main__':
	main()

