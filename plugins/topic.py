class TopicPlugin:
    base_msg = "<p><b>GoneWacko's Mumble Server.</b></p><p>mumble.gwko.nl, port 64738</p>"
    def __init__(self, server, adapter):
        self.server = server
        self.adapter = adapter

    def add_topic(self, user, text):
        wt = server.getConf('welcometext')
        wt += '<hr class="topic"><div class="%s topic">%s</div>' % (user.name, text)
        print wt
        #server.setConf('welcometext', wt)

    def del_topic(self, fragment):
        wt = server.getConf('welcomtext')
        topics = wt.split('<hr class="topic">')
        for t in list(topics[1:]):
            if fragment in t:
                topics.remove(t)
                break
        wt = '<hr class="topic">'.join(topics)
        print wt
        #server.setConf('welcometext', wt)

    def userTextMessage(self, user, msg, current=None):
        if msg.text.startswith("!addtopic"):
            add_topic(user, msg.text[9:])
        elif msg.text.startswith("!deltopic"):
            del_topic(user, msg.text[9:])

