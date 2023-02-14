_placeholder for CC badge_
# Overview
This telegram bot uses [https://github.com/hemantapkh/1337x](hemantapkh's 1337x) unofficial API to search the torrents on 1337x tracker.<br>
The bot itself built on `aiogram` and has only one command to search the torrents. It shows top ten results for the search query as inline commands. After user pressed one of the results, the bot catches callback data (which is a torrent ID on 1337x) and generates inline button with magnet link. As long Telegram won't let using non-http links, the bot uses `short.io API` to generate shorten URL with a magnet link and then send it to the user.