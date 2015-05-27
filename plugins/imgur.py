import re
import urlparse
from imgurpython import ImgurClient

from Plugin import Plugin

# Go to https://api.imgur.com/oauth2/addclient
# Log in with an imgur account, and register the application with the
# "Anonymous usage without user authorization" authorization type
# Then copy the shown ID and Secret here:
client_id = 'YOUR CLIENT ID'
client_secret = 'YOUR CLIENT SECRET'

class ImgurPlugin(Plugin):
    href_re = 'href="([^"]*)"'

    def __init__(self, server, adapter):
        self.server = server
        self.adapter = adapter
        self.client = ImgurClient(client_id, client_secret)

    def get_imgur_ids(self, message):
        images = {}
        albums = set()
        galleries = set()

        uris = re.findall(self.href_re, message)
        for uri in uris:
            i = None
            res = urlparse.urlparse(uri)
            if res.netloc == 'i.imgur.com':
                i = re.match('^/(?P<imgid>.+)\.(jpg|png|gifv?)', res.path).group('imgid')
                images[i] = uri
            elif res.netloc == 'imgur.com':
                i = re.match('^/(?P<entry>[^/]+)', res.path).group('entry')
                if i is not None:
                    if i == 'a':
                        i = re.match('^/a/(?P<albumid>.+)$', res.path).group('albumid')
                        if i is not None:
                            albums.add(i)
                    elif i == 'g':
                        i = re.match('^/g/(?P<galleryid>.+)$', res.path).group('galleryid')
                        if i is not None:
                            galleries.add(i)
                    else:
                        images[i] = uri
        return {'i': images, 'a': albums, 'g': galleries}

    text_imgur = '<span style="color: #85BF25; font-weight: bold;">Imgur</span>'
    text_album = text_imgur + ' album'
    text_img = text_imgur + ' image'
    text_gallery = text_imgur + ' gallery'

    def sendReply(self, message, text):
        for c in message.channels:
            self.server.sendMessageChannel(c, False, text)

    def image_url(self, img, thumbnail=False):
        if thumbnail:
            return 'http://i.imgur.com/{id}m.jpg'.format(id=img.id)
        elif hasattr(img, 'gifv'):
            return img.gifv
        else:
            return img.link

    def process_gallery(self, message, gallery_id):
        # Not yet implemented.
        pass

    def process_album(self, message, album_id):
        try:
            a = self.client.get_album(album_id)
            if a is not None:
                text = '<p>{text_album}: <span style="font-weight: bold;">{title}</span></p>'.format(text_album=self.text_album, title=a.title) if a.title else '<p><span style="font-weight: bold;">Untitled</span> {text_album}</p>'.format(text_album=self.text_album)
                cover = self.client.get_image(a.cover)
                if cover is not None:
                    text += '<p><a href="{link}"><img src="{coverthumb}"></a></p>'.format(link=a.link, coverthumb=self.image_url(cover, True))
            self.sendReply(message, text)
        except Exception as e:
            self.sendReply(message, '<p><b>Imgur plugin error</b>:</p><p>' + repr(e) + '</p>')

    def process_img(self, message, image_id, uri):
        try:
            img = self.client.get_image(image_id)
            if img is not None:
                text = '<p>{text_img}: <span style="font-weight: bold;">{title}</span></p>'.format(text_img=self.text_img, title=img.title) if img.title else '<p><span style="font-weight: bold;">Untitled</span> {text_img}</p>'.format(text_img=self.text_img)
                text += '<p><a href="{link}"><img src="{thumb}"></a></p>'.format(link=img.link, thumb=self.image_url(img, True))
                self.sendReply(message, text)
        except Exception as e:
            self.sendReply(message, '<p><b>Imgur plugin error</b>:</p><p>' + repr(e) + '</p>')

    def userTextMessage(self, user, message, current=None):
        ids = self.get_imgur_ids(message.text)
        if len(ids['i']) > 0:
            for imgid in ids['i']:
                self.process_img(message, imgid, ids['i'][imgid])
        if len(ids['g']) > 0:
            for gallery_id in ids['g']:
                self.process_gallery(message, gallery_id)
        if len(ids['a']) > 0:
            for album_id in ids['a']:
                self.process_album(message, album_id)
