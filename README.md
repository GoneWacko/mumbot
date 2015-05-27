# mumbot
A simple python-based bot for Mumble, providing a simple plugin-based framework that can act on callbacks from the Mumble server.

Very much a work in progress and impulsively hacked together.

## Requirements
Mumbot communicates with the Mumble server using *ZeroC Ice*.
`apt-get install python-zeroc-ice` or `pip install zeroc-ice`

The plugins below also require some packages, which can also be installed through `pip`:
* YouTube Plugin
  * [google-api-python-client](https://developers.google.com/api-client-library/python/apis/youtube/v3), the official Google API client library for Python
  * [isodate](https://pypi.python.org/pypi/isodate)
* Imgur Plugin
  * [imgurpython](https://github.com/Imgur/imgurpython), the official Imgur Python library

## Installation
In order for mumbot to work, the `Murmur.ice` slice of your installed Mumble server needs to be translated to Python using `slice2py`. Simply run `slice2py /path/to/Murmur.ice` inside the directory containing `mumbot.py`. You may need to provide extra options for slice2py to find the files included from Murmur.ice.

For example, with Debian: with the `mumble-server` and `python-zeroc-ice` packages installed, run:
```sh
$ slice2py -I/usr/share/Ice/slice /usr/share/slice/Murmur.ice
```

The bot can then be started using
```sh
$ python mumbot.py
```
or executed in the background using
```sh
$ python mumbot.py -d
```
The host and port used for connecting with the Mumble server are currently hardcoded in `mumbot.py`.

## Plugins
Selection and loading of plugins is currently hardcoded in `mumbot.py`.

The available plugins are:
* **ChannelLinkPlugin**: Sends messages to members of the *admin* groups of the relevant channels when channels are linked and unlinked. 
* **TopicPlugin**: Allows users to modify the `welcometext` (aka MOTD) by using the `!addtopic` and `!deltopic` commands. **Warning:** HTML is allowed!
* **TwitchPlugin**: Looks up stream information (Channel name, stream title, number of viewers, game being played, thumbnail) for Twitch.tv streams when users send messages containing links to twitch.tv, and posts the information to the mumble channel(s).
* **YouTubePlugin**: Similar to `TwitchPlugin`, but for YouTube. Looks up video name, duration, channel name, and thumbnail and posts them to the mumble channel(s). Has some configuration settings, including the necessary Google API key, in `plugins/youtube.py`.
* **ImgurPlugin**: Looks up image/album title and thumbnail for imgur.com links in chat messages, and prints them to the channel. Requires the configuration of Imgur API authentication details, in `plugins/imgur.py`.
