#!/usr/bin/env python
from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol

from construct import LengthValueAdapter, StringAdapter, Sequence
from construct import UBInt16
from construct import Struct, MetaField

class DoubleAdapter(LengthValueAdapter):

    def _encode(self, obj):
        return len(obj) / 2, obj

def BetaString(name):
    return StringAdapter(
            DoubleAdapter(
                Sequence(name,
                    UBInt16("length"),
                    MetaField("data", lambda ctx: ctx["length"] * 2),
                    )
                ),
            encoding="utf_16_be",
            )

def handshake(payload):
    parser = Struct('handshake',
            BetaString('username_and_host')
            )

    container = parser.parse(payload)

    print 'handshake: username_and host is %s' % container.username_and_host

packets = {
    2: handshake,
}

class BetaProtocol(Protocol):

    def dataReceived(self, data):
        packet_id = ord(data[0])
        payload = data[1:]
        print '::::packet_id =', packet_id
        print '::::payload =', repr(payload)

        if packet_id in packets:
            handler = packets[packet_id]
            handler(payload)

class BetaFactory(Factory):

    protocol = BetaProtocol

reactor.listenTCP(25565, BetaFactory())
reactor.run()
