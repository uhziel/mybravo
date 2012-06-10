#!/usr/bin/env python
from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol

from construct import LengthValueAdapter, StringAdapter, Sequence
from construct import UBInt16
from construct import Struct, MetaField

STATE_UNAUTHENTICATED, STATE_CHALLENGED = range(2)

class DoubleAdapter(LengthValueAdapter):

    def _encode(self, obj, context):
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

parsers = {
    0x02: Struct(
        'handshake',
        BetaString('username_and_host')
        )
}

class BetaProtocol(Protocol):

    def __init__(self):
        self.state = STATE_UNAUTHENTICATED

    def dataReceived(self, data):
        packet_id = ord(data[0])
        payload = data[1:]

        if packet_id in parsers and packet_id in self.handlers:
            container = parsers[packet_id].parse(payload)
            self.handlers[packet_id](self, container)
        else:
            print 'unknown packet (%d, %s)' % (packet_id, repr(payload))

    def handshake(self, container):
        print 'handshake: username_and host is %s' % container.username_and_host

        self.state = STATE_CHALLENGED
        container.username_and_host = u'-'
        self.transport.write('\x02' + parsers[0x02].build(container))

    handlers = {
        0x02: handshake,
    }


class BetaFactory(Factory):

    protocol = BetaProtocol

reactor.listenTCP(25565, BetaFactory())
reactor.run()
