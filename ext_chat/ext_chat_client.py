from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
import sys
import random #for random client name

class EchoClient(LineReceiver):
	end = "Goodbye!"
	
	def lineReceived(self,line):
		if line=="What's your name?":
			r = str(random.random()) #generates a random username
			self.sendLine(r)
			self.sendLine("Good to be here!")
		
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
