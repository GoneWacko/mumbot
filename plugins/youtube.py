import re
import urlparse
import isodate

from apiclient.discovery import build
from apiclient.errors import HttpError

from Plugin import Plugin

# Get a "Server Key" for Public API Access from the Google Developer Console and paste it here:
YOUTUBE_API_KEY = "<YOUR API KEY HERE>"

# Set to True if video durations should also be retrieved.
# Incurs an extra API quota cost of 2 units per request
YOUTUBE_INCLUDE_DURATION = True
# Set to True if a clickable video thumbnail should be included.
# No extra API cost, simply links to a .jpg on the YouTube servers.
YOUTUBE_INCLUDE_THUMBNAIL = True
# If True, and YOUTUBE_INCLUDE_THUMBNAIL is True above, the thumbnails will be
# clickable links to the video. Currently the thumbnail will not use the exact
# link as it appeared in the user's message, which may cause some information
# to be lost, such as if the user's link was to a specific time in the video.
YOUTUBE_THUMBNAIL_CLICKABLE = True

# End of configuration options. Don't modify anything below this line.

class YouTubePlugin(Plugin):
    href_re = 'href="([^"]*)"'

    class YouTubeError(Exception):
        def __init__(self, msg):
            self.msg = msg
        def __str__(self):
            return 'YouTube API Error: ' + self.msg

    def __init__(self, server, adapter):
        self.server = server
        self.adapter = adapter
        self.youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    def get_video_ids(self, message):
        "Returns the set of video IDs appearing in YouTube links in a message."
        ids = set()
        uris = re.findall(self.href_re, message)
        for uri in uris:
            i = None
            res = urlparse.urlparse(uri)
            if res.netloc in ['www.youtube.com', 'youtube.com'] and res.path == '/watch':
                qs = urlparse.parse_qs(res.query)
                if 'v' in qs:
                    i = qs['v'][0]
            elif res.netloc in ['www.youtu.be', 'youtu.be']:
                i = re.match('^/(?P<vid>.*)', res.path).group('vid')
            if i is not None:
                ids.add(i)
        return ids

    def get_videos(self, ids):
        ids = set(ids)
        results = {}
        if len(ids) == 0:
            return results
        if YOUTUBE_INCLUDE_DURATION:
            parts="id,snippet,contentDetails"
        else:
            parts="id,snippet"
        request = self.youtube.videos().list(part=parts, id=",".join(ids))
        try:
            response = request.execute()
        except HttpError, err:
            raise YouTubePlugin.YouTubeError(err.content)
        return response['items']

    def sendReply(self, message, text):
        for c in message.channels:
            self.server.sendMessageChannel(c, False, text)

    def timedelta_to_string(self, delta):
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        results = []
        if (hours > 0):
            results.append("%d hours" % (hours))
        if (minutes > 0):
            results.append("%d minutes" % (minutes))
        if (seconds > 0):
            results.append("%d seconds" % (seconds))
        return ", ".join(results)

    def process(self, message, video):
        title = video['snippet']['title']
        channel = video['snippet']['channelTitle']
        if YOUTUBE_INCLUDE_DURATION:
            duration = isodate.parse_duration(video['contentDetails']['duration'])
            text = '<p><b><span style="color: red;">YouTube</span></b> video: <b>%s</b> (%s) by <b>%s</b></p>' % (title, self.timedelta_to_string(duration), channel)
        else:
            text = '<p><b><span style="color: red;">YouTube</span></b> video: <b>%s</b> by <b>%s</b></p>' % (title, channel)
        if YOUTUBE_INCLUDE_THUMBNAIL:
            thumbnail = video['snippet']['thumbnails']['medium']
            thumb_width = thumbnail['width']
            thumb_height = thumbnail['height']
            thumb_url = thumbnail['url']
            if YOUTUBE_THUMBNAIL_CLICKABLE:
                url = "https://www.youtube.com/watch?v=" + video['id']
                text += '<p><a href="%s"><img src="%s" width="%d" height="%d"></a></p>' % (url, thumb_url, thumb_width, thumb_height)
            else:
                text += '<p><img src="%s" width="%d" height="%d"></p>' % (thumb_url, thumb_width, thumb_height)
        self.sendReply(message, text)

    def userTextMessage(self, user, message, current=None):
        ids = self.get_video_ids(message.text)
        if len(ids) > 0:
            try:
                videos = self.get_videos(ids)
                for video in videos:
                    self.process(message, video)
            except YouTubePlugin.YouTubeError, err:
                self.sendReply(message, str(err))
