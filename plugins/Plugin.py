class Plugin:
    def __init__(self, server, adapter):
        self.server = server
        self.adapter = adapter

    def userConnected(self, user, current=None):
        pass

    def userDisconnected(self, user, current=None):
        pass

    def userTextMessage(self, user, msg, current=None):
        pass

    def userStateChanged(self, user, current=None):
        pass

    def channelCreated(self, channel, current=None):
        pass

    def channelRemoved(self, channel, current=None):
        pass

    def channelStateChanged(self, channel, current=None):
        pass

