#!/usr/bin/env python
from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol


class BetaProtocol(Protocol):

    def dataReceived(self, data):
        print data

class BetaFactory(Factory):

    protocol = BetaProtocol

reactor.listenTCP(25565, BetaFactory())
reactor.run()
