<a href="https://codeclimate.com/github/iwatkot/search1337bot/maintainability"><img src="https://api.codeclimate.com/v1/badges/4944cffd3dd2510067ad/maintainability" /></a>
# Overview
This telegram bot uses [hemantapkh's 1337x](https://github.com/hemantapkh/1337x) unofficial API to search the torrents on **1337x** tracker.<br>
The bot itself is built on **aiogram** and has no commands at all, it expects that every message from the user is a search request. It shows the top ten results for the search query as inline buttons. After the user pressed one of the results, the bot catches callback data (which is a torrent ID on 1337x) and generates an inline button with a magnet link. As long as Telegram does not let the usage of a non-HTTP link, the bot uses `short.io API` to generate a shortened URL with a magnet link and then send it to the user.

# Changelog
**2023/03/13** - Added message if no results were found.<br>
**2023/03/13** - Removed `Search` button, now bot expects that each message is a search query.<br>