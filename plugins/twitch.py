import re
import urlparse
import urllib2
import json

from Plugin import Plugin

href_re = 'href="([^"]*)"'

class TwitchPlugin(Plugin):

    def __init__(self, server, adapter):
        self.server = server
        self.adapter = adapter

    def get_twitch_channels(self, message):
        channels = set()
        uris = re.findall(href_re, message)
        for uri in uris:
            i = None
            res = urlparse.urlparse(uri)
            if res.netloc in ['www.twitch.tv', 'twitch.tv']:
                path = res.path.split('/')
                if len(path) != 2:
                    continue
                channel = path[1]
                if channel in ['directory', 'products', 'p', 'user', 'manager', 'messages', 'logout', 'settings']:
                    continue
                channels.add((channel, uri))
        return channels

    def get_stream(self, stream):
        url = "https://api.twitch.tv/kraken/streams/%s/" % stream
        request = urllib2.Request(url, None, {'Accept': 'application/vnd.twitchtv.v3+json'})
        response = urllib2.urlopen(request, timeout=2)
        code = response.getcode()
        if code == 200:
            js = None
            try:
                js = json.load(response)
            except:
                return {"error": "Error parsing Twitch API response"}
            return js
        elif code == 404:
            js = None
            try:
                js = json.load(response)
            except:
                return {"error": "Error parsing Twitch API response. Channel '%s' does not seem to exist." % stream}
            return {"error": js["message"]}
        else:
            return {"error": response.read()}

    def get_channel(self, channel):
        url = "https://api.twitch.tv/kraken/channels/%s/" % channel
        request = urllib2.Request(url, None, {'Accept': 'application/vnd.twitchtv.v3+json'})
        response = urllib2.urlopen(request, timeout=2)
        code = response.getcode()
        if code == 200:
            js = None
            try:
                js = json.load(response)
            except:
                return {"error": "Error parsing Twitch API response"}
            return js
        elif code == 404:
            js = None
            try:
                js = json.load(response)
            except:
                return {"error": "Error parsing Twitch API response. Channel '%s' does not seem to exist." % channel}
            return {"error": js["message"]}
        else:
            return {"error": response.read()}

    def process(self, message, channel, url):
        stream = self.get_stream(channel)
        text = None
        if 'error' in stream:
            text = '<span style="color: red;">Error: %s</span>' % stream['error']
        else:
            s = stream["stream"]
            if s is not None:
                text = '<p><b style="color: #6441A5; background: white;">Twitch</b> stream: <b>%s</b> by <b>%s</b> playing <b>%s</b> (%d viewers)</p>' % (s["channel"]["status"], s["channel"]["display_name"],s["game"],s["viewers"])
                if "preview" in s:
                    text += '<p><a href="%s"><img src="%s" height="180" width="320"></a></p>' % (url, s["preview"]["medium"])
            else:
                chan = self.get_channel(channel)
                if 'error' in chan:
                    text = '<span style="color: red;">Error: %s</span>' % stream['error']
                else:
                    text = '<p><b style="color: #6441A5; background: white;">Twitch</b> channel <b>%s</b> is not currently streaming.</p>' % chan["display_name"]
                    if 'logo' in chan and chan['logo'] is not None:
                        text += '<p><img src="%s" height="150" width="150"></p>' % chan['logo']
        if text is not None:
            for c in message.channels:
                self.server.sendMessageChannel(c, False, text)

    def userTextMessage(self, user, message, current=None):
        for channel, uri in self.get_twitch_channels(message.text):
            self.process(message, channel, uri)
