import Murmur
import Ice

plugins = []

class Mumbot(Murmur.ServerCallback):
    def __init__(self, server, adapter):
        self.server = server
        self.adapter = adapter

    def userConnected(self, user, current=None):
        for p in plugins:
            p.userConnected(user, current)

    def userDisconnected(self, user, current=None):
        for p in plugins:
            p.userDisconnected(user, current)

    def userTextMessage(self, user, msg, current=None):
        for p in plugins:
            p.userTextMessage(user, msg, current)

    def userStateChanged(self, user, current=None):
        for p in plugins:
            p.userStateChanged(user, current)

    def channelCreated(self, channel, current=None):
        for p in plugins:
            p.channelCreated(channel, current)

    def channelRemoved(self, channel, current=None):
        for p in plugins:
            p.channelRemoved(channel, current)

    def channelStateChanged(self, channel, current=None):
        for p in plugins:
            p.channelStateChanged(channel, current)

def daemonize():
    import os
    pid = os.fork()
    if pid == 0:
        os.setsid()
        pid = os.fork()
        if pid == 0:
            os.chdir("/")
            os.umask(0)
        else:
            os._exit(0)
    else:
        os._exit(0)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg == '-d':
                daemonize()

    # Set up ICE. No clue how it works, so hands off.
    comm = Ice.initialize()
    proxy = comm.stringToProxy("Meta:tcp -p 6502")
    meta = Murmur.MetaPrx.checkedCast(proxy)
    server = meta.getServer(1)

    # Here. Take callback.
    adapter = comm.createObjectAdapterWithEndpoints("Callback.Client", "tcp -h 127.0.0.1")
    adapter.activate()
    callback = Murmur.ServerCallbackPrx.uncheckedCast(adapter.addWithUUID(Mumbot(server, adapter)))
    server.addCallback(callback)

    # Load plugins
    from plugins.youtube import YouTubePlugin
    from plugins.twitch import TwitchPlugin
    from plugins.topic import TopicPlugin
    plugins.append(YouTubePlugin(server, adapter))
    plugins.append(TwitchPlugin(server, adapter))
    plugins.append(TopicPlugin(server, adapter))

    # And now we wait.
    import time
    while True:
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            sys.exit(0)

