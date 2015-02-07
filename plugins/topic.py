from Plugin import Plugin
from HTMLParser import HTMLParser

class TopicPlugin(Plugin):
    def __init__(self, server, adapter):
        self.server = server
        self.adapter = adapter
        self.htmlparser = HTMLParser()

    def add_topic(self, user, text):
        if len(text) == 0 or text.isspace():
            return
        wt = self.server.getConf('welcometext')
        wt += '<hr class="topic"><div class="%s topic">%s</div>' % (user.name, self.htmlparser.unescape(text))
        print wt
        self.server.setConf('welcometext', wt)

    def del_topic(self, fragment):
        if len(fragment) == 0 or fragment.isspace():
            return
        wt = self.server.getConf('welcometext')
        topics = wt.split('<hr class="topic">')
        for t in list(topics[1:]):
            if fragment in t:
                topics.remove(t)
                break
        wt = '<hr class="topic">'.join(topics)
        print wt
        self.server.setConf('welcometext', wt)

    def userTextMessage(self, user, msg, current=None):
        if msg.text.startswith("!addtopic"):
            self.add_topic(user, msg.text[10:])
        elif msg.text.startswith("!deltopic"):
            self.del_topic(msg.text[10:])

