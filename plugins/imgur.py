import re
import urlparse
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError

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

    def process(self, message):
        ids = set()
        subreddits = set()

        uris = re.findall(self.href_re, message.text)
        for uri in uris:
            i = None
            res = urlparse.urlparse(uri)
            if res.netloc == 'i.imgur.com':
                i = re.match('^/(?P<imgid>.+)\.(jpg|png|gifv?)', res.path).group('imgid')
                if i not in ids:
                    ids.add(i)
                    self.process_image_id(message, i, uri)
            elif res.netloc == 'imgur.com':
                i = re.match('^/(?P<item>[^/]+)', res.path).group('item')
                if i is not None:
                    if i == 'a':
                        i = re.match('^/a/(?P<albumid>[^/]+)', res.path).group('albumid')
                        if i is not None and i not in ids:
                            ids.add(i)
                            self.process_album_id(message, i, uri)
                    elif i == 'gallery':
                        i = re.match('^/gallery/(?P<galleryid>[^/]+)', res.path).group('galleryid')
                        if i is not None and i not in ids:
                            ids.add(i)
                            self.process_gallery_id(message, i, uri)
                    elif i == 'r':
                        m = re.match('^/r/(?P<subreddit>[^/]+)(/(?P<galleryid>[^/]+)?)?', res.path)
                        if m is not None:
                            subreddit = m.group('subreddit')
                            i = m.group('galleryid')
                            if i not in [None, 'new', 'top']:
                                ids.add(i)
                                self.process_subreddit_gallery_id(message, subreddit, i, uri)
                            else:
                                subreddits.add(subreddit)
                                self.process_subreddit(message, subreddit, i, uri)
                    else:
                        if res.path == '/' + i and i not in ids:
                            ids.add(i)
                            self.process_id(message, i, uri)

    def sendReply(self, message, text):
        for c in message.channels:
            self.server.sendMessageChannel(c, False, text)

    def sendError(self, message, text):
        self.sendReply(message, '<p>Imgur plugin error:</p><p>' + text + '</p>')

    class NotAGallery(Exception):
        pass

    class NotAnAlbum(Exception):
        pass

    def process_id(self, message, i, uri):
    # There does not seem to be any way to determine whether an ID belongs to
    # an album or a gallery, other than trial & error
        try:
            self.process_gallery_id(message, i, uri)
        except ImgurPlugin.NotAGallery:
            try:
                self.process_album_id(message, i, uri)
            except ImgurPlugin.NotAnAlbum:
                self.process_image_id(message, i, uri)
        except Exception as err:
            self.sendError(message, repr(err))

    def process_gallery_id(self, message, gallery_id, uri):
        try:
            item = self.client.gallery_item(gallery_id)
        except ImgurClientError as err:
            if err.status_code == 404:
                raise ImgurPlugin.NotAGallery()
            elif err.status_code == 401 or err.status_code == 403:
                # Gallery seems to exist, but we have no access.
                return
            else:
                self.sendError(message, repr(err))
                return
        except Exception as err:
            self.sendError(message, repr(err))
            return
        self.process_gallery(message, item, uri)

    def process_subreddit_gallery_id(self, message, subreddit, gallery_id, uri):
        try:
            item = self.client.subreddit_image(subreddit, gallery_id)
        except ImgurClientError as err:
            if err.status_code == 404:
                raise ImgurPlugin.NotAGallery()
            elif err.status_code == 401 or err.status_code == 403:
                # Gallery seems to exist, but we have no access.
                return
            else:
                self.sendError(message, repr(err))
                return
        except Exception as err:
            self.sendError(message, repr(err))
            return
        self.process_gallery(message, item, uri)

    def process_subreddit(self, message, subreddit, sort, uri):
        try:
            if sort == 'top':
                gallery = self.client.subreddit_gallery(subreddit, sort='top', window='month')
            else:
                gallery = self.client.subreddit_gallery(subreddit, sort='time')
        except ImgurClientError as err:
            if err.status_code == 404:
                # Subreddit doesn't seem to exist.
                return
            elif err.status_code == 401 or err.status_code == 403:
                # Gallery seems to exist, but we have no access.
                return
            else:
                self.sendError(message, repr(err))
                return
        except Exception as err:
            self.sendError(message, repr(err))
            return
        self.process_subreddit_list(message, subreddit, sort, gallery, uri)

    def process_album_id(self, message, album_id, uri):
        try:
            a = self.client.get_album(album_id)
        except ImgurClientError as err:
            if err.status_code == 404:
                raise ImgurPlugin.NotAnAlbum()
            elif err.status_code == 401 or err.status_code == 403:
                # Album seems to exist, but we have no access.
                return
            else:
                self.sendError(message, repr(err))
                return
        except Exception as err:
            self.sendError(message, repr(err))
            return
        if a is not None:
            self.process_album(message, a, uri)

    def process_image_id(self, message, image_id, uri):
        try:
            img = self.client.get_image(image_id)
        except ImgurClientError as err:
            if err.status_code == 404:
                return
            elif err.status_code == 401 or err.status_code == 403:
                # Image seems to exist, but we have no access.
                return
            else:
                self.sendError(message, repr(err))
                return
        except Exception as err:
            self.sendError(message, repr(err))
            return
        if img is not None:
            self.process_image(message, img, uri)

    def process_gallery(self, message, gallery, uri):
        if gallery.is_album:
            self.process_album(message, gallery, uri)
        else:
            self.process_image(message, gallery, uri)

    text_imgur = '<span style="color: #85BF25; font-weight: bold;">Imgur</span>'

    def process_image_thumbnail(self, image, uri, size='m'):
        thumb = 'http://i.imgur.com/{id}{size}.jpg'.format(id=image.id, size=size)
        return '<a href="{uri}"><img src="{thumb}"></a>'.format(uri=uri, thumb=thumb)

    def process_album(self, message, album, uri):
        text = '<p>{imgur} album (with {count} images): <b>{title}</b></p>' if album.title else '<p><b>Untitled</b> {imgur} album with {count} images.'
        text = text.format(imgur=self.text_imgur, title=album.title, count=len(album.images))
        if album.cover is not None:
            try:
                cover = self.client.get_image(album.cover)
                if cover is not None:
                    text += '<p>' + self.process_image_thumbnail(cover, uri) + '</p>'
            except Exception as err:
                self.sendError(message, repr(err))
        self.sendReply(message, text)

    def process_image(self, message, image, uri):
        text = '<p>' + self.process_image_thumbnail(image, uri) + '</p>'
        if image.title:
            text = '<p>{imgur} image: <b>{title}</b></p>'.format(imgur=self.text_imgur, title=image.title) + text
        self.sendReply(message, text)

    def process_subreddit_list(self, message, subreddit, sort, gallery, uri):
        sort = 'Most popular' if sort == 'top' else 'Newest'
        text = '<p>{sort} subreddit <b>/r/{subreddit}</b> images on {imgur}:</p>'.format(sort=sort, subreddit=subreddit, imgur=self.text_imgur)
        count = max(4, len(gallery))
        text += '<p>'
        for i in xrange(min(4, len(gallery))):
            text += self.process_image_thumbnail(gallery[i], uri, 's') + ' '
        text += '</p>'
        self.sendReply(message, text)

    def userTextMessage(self, user, message, current=None):
        self.process(message)
