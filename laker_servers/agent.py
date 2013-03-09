from pprint import pformat

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
from twisted.web.http_headers import Headers

global_json = ''

class BeginningPrinter(Protocol):
	def __init__(self, finished):
		self.finished = finished
		self.remaining = 1024 * 10
		self.json = ""

	def dataReceived(self,bytes):
		self.json += bytes

	def connectionLost(self, reason):
		print 'Finished receiving body:', reason.getErrorMessage()
		global_json =  self.json
		self.finished.callback(None)

agent = Agent(reactor)

http = 'http://search.twitter.com/search.json?geocode=+37.781157,-122.398720,1mi&rpp=20&result_type=mixed'

d = agent.request(
	'GET',
	http,
	Headers({'User-Agent': ['Twisted Web Client Example']}),
	None)


def cb_print(response):
	print response.version
	print response.code
	print response.phrase
	print pformat(list(response.headers.getAllRawHeaders()))


	print response.phrase
	finished = Deferred()
	json = response.deliverBody(BeginningPrinter(finished))
	return finished

d.addCallback(cb_print)
print 'a'

def cb_shutdown(ignored):
	reactor.stop()


reactor.run()

