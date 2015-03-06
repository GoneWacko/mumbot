from Plugin import Plugin

class ChannelLinkPlugin(Plugin):
    def __init__(self, server, adapter):
        self.server = server
        self.adapter = adapter
        self.links = {}

        chans = server.getChannels()
        for cid in chans:
            self.links[cid] = chans[cid].links

    def adminMessage(self, channels, text):
        admins = set()
        users = self.server.getUsers()
        for c in channels:
            groups = self.server.getACL(c)[1]
            for g in groups:
                if g.name == 'admin':
                    admins |= set(g.members)
        for u in users:
            if users[u].userid in admins:
                self.server.sendMessage(users[u].session, text)

    def channelCreated(self, channel, current=None):
        self.links[channel.id] = channel.links

    def channelRemoved(self, channel, current=None):
        if channel.id in self.links:
            del self.links[channel.id]

    def channelStateChanged(self, channel, current=None):
        oldlinks = self.links[channel.id]
        links = channel.links
        chans = set([channel.id])
        if len(oldlinks) > len(links):
            # Channels were unlinked
            dropped = [j for j in oldlinks if j not in links]
            chans |= set(dropped)
            if len(dropped) == 1:
                c = self.server.getChannelState(dropped[0]).name
                text = "Channel <b>%s</b> was unlinked from channel <b>%s</b>." % (channel.name, c)
            else:
                text = "Channel <b>%s</b> was unlinked from channels:<ul>" % channel.name
                for i in dropped:
                    c = self.server.getChannelState(i).name
                    text += "<li>%s</li>" % c
                text += "</ul>"
            self.adminMessage(chans, text)
            self.links[channel.id] = channel.links
        elif len(oldlinks) < len(links):
            # Channels were linked
            linked = [j for j in links if j not in oldlinks]
            chans |= set(linked)
            if len(linked) == 1:
                c = self.server.getChannelState(linked[0]).name
                text = "Channel <b>%s</b> was linked to channel <b>%s</b>." % (channel.name, c)
            else:
                text = "Channel <b>%s</b> was linked to channels:<ul>" % channel.name
                for i in linked:
                    c = self.server.getChannelState(i).name
                    text += "<li>%s</li>" % c
                text += "</ul>"
            self.adminMessage(chans, text)
            self.links[channel.id] = channel.links

