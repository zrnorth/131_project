from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
import sys

class EchoClient(LineReceiver):
	end = "Goodbye!"
	def connectionMade(self):
		self.sendLine("Hello world!")
		self.sendLine("What a fine day it is.")
		self.sendLine(self.end)

	def lineReceived(self,line):
		print "receive:", line
		if line==self.end:
			self.transport.loseConnection()

class EchoClientFactory(ClientFactory):
	protocol = EchoClient

	def clientConnectionFailed(self, connector, reason):
		print 'Connection failed: ', reason.getErrorMessage()
		reactor.stop()
	
	def clientConnectionLost(self, connector, reason):
		print 'Connection lost: ', reason.getErrorMessage()
		reactor.stop()

def main():
	factory = EchoClientFactory()
	reactor.connectTCP('localhost', 12371, factory)
	reactor.run()

if __name__ == '__main__':
	main()
