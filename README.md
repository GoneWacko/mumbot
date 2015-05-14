# mumbot
A simple python-based bot for Mumble.

Very much a work in progress and impulsively hacked together.

## Requirements
Mumbot communicates with the Mumble server using *ZeroC Ice*.
`apt-get install python-zeroc-ice` or `pip install zeroc-ice`

## Plugins
Selection and loading of plugins is currently hardcoded in `mumbot.py`.

The available plugins are:
* **ChannelLinkPlugin**: Sends messages to members of the *admin* groups of the relevant channels when channels are linked and unlinked. 
* **TopicPlugin**: Allows users to modify the `welcometext` (aka MOTD) by using the `!addtopic` and `!deltopic` commands. **Warning:** HTML is allowed!
* **TwitchPlugin**: Looks up stream information (Channel name, stream title, number of viewers, game being played, thumbnail) for Twitch.tv streams when users send messages containing links to twitch.tv, and posts the information to the mumble channel(s).
* **YouTubePlugin**: Similar to `TwitchPlugin`, but for YouTube. Looks up video name, duration, channel name, and thumbnail and posts them to the mumble channel(s). Has some configuration settings in `plugins/youtube.py`.

The YouTube Plugin requires the following libraries:
* [isodate](https://pypi.python.org/pypi/isodate)
* [google-api-python-client](https://developers.google.com/api-client-library/python/apis/youtube/v3)
