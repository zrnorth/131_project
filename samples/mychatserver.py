"""The most basic chat protocol possible.

run me with twistd -y chatserver.py, and then connect with multiple
telnet clients to port 12371
"""

from twisted.protocols import basic



class MyChat(basic.LineReceiver):
    def connectionMade(self):
        print "Got new client!"
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        print "Lost a client!"
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        print "received", repr(line)
        for c in self.factory.clients:
            c.message(line)

    def message(self, message):
        self.transport.write(message + '\n')


from twisted.internet import protocol
from twisted.application import service, internet

factory = protocol.ServerFactory()
factory.protocol = MyChat
factory.clients = []

application = service.Application("chatserver")
internet.TCPServer(12371, factory).setServiceParent(application)
