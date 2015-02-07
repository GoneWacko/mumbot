from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint

class HTMLStripper(HTMLParser):
    def __init__(self):
        self.reset()

    def reset(self):
        HTMLParser.reset(self)
        self.stripped = str()

    def escape(self, text):
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            self.stripped += "<%s" % tag
            for name, value in attrs:
                self.stripped += '%s="%s"' % (name, self.escape(value))
            self.stripped += ">"

    def handle_endtag(self, tag):
        if tag != 'a':
            self.stripped += "</%s>" % tag

    def handle_startendtag(self, tag, attrs):
        if tag != 'a':
            self.stripped += "<%s" % tag
            for name, value in attrs:
                self.stripped += '%s="%s"' % (name, self.escape(value))
            self.stripped += " />"

    def handle_data(self, d):
        self.stripped += d
    
    def handle_entityref(self, name):
        self.stripped += "&%s;" % name

    def handle_charref(self, name):
        self.stripped += "&#%s;" % name

    def get_data(self):
        return self.stripped
