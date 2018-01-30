# NSFW Game Manager GUI

This GUI has been made by Dogeek (http://github.com/Dogeek) based on cyian-1756's CLI.
The GUI has been made using the Tk/Tcl wrapper for python, tkinter.

## Features :

### Implemented :
- Adding new games to the database
- Downloading and Updating games from the following sources : mega.nz, patreon, dropbox, google drive, itch.io and via apache.
- Editing games in the database
- Copying the links to the clipboard
- Copying the whole line's data to the clipboard
- check for game updates
- Sorting games by genre, developer, etc.
- A super awesome help page
- Options to set the window size, the download path etc
- Syncing every user's databases
- Automatic unzipping/install of the games to the specified installation directory
- Scrape reddit r/lewdgames and r/nsfwgaming for updates, and new releases to add them to the database

### Planned :

- Scraping games' websites to look for updates.
- Auto-Updating the database
- Game rating (each user may rate the game, shown rating will be the average rating)
- Patreon integration to pledge from the app itself

# TO DO List :

## Fix :

- [x] right click on an item doesn't really select it, and results in an error when trying to perform onSelect actions.
- [x] trying to move/resize the window is still a bit glitchy (window shaking, resize snapping back to where it was...)



## v1 :
- [x] implement unzipping the downloaded files if it is an archive.
- [x] add a 'View in explorer' command
- [x] implement mega.nz downloading
- [x] implement auto-refresh of the game list when you add a new game
- [x] implement updating of games
- [x] fix toplevel windows not showing up the second time you click on the button (problem with global vars ??)
- [x] fix toplevel windows not retaining information on reopening
- [x] change geometry based on selected resolution in options window
- [x] implement mediafire download
- [x] implement options menu and window
- [x] implement barebones ui, with list of games
- [x] implement games sorting based on columns
- [x] implement add game to list window
- [x] implement editing database from the UI
- [x] implement checking for update


# Required libraries :

## Standard Python Libraries :

- tkinter
- configparser
- time
- json
- re
- platform
- os
- sys
- webbrowser
- threading
- urllib
- ftplib
- subprocess
- zipfile
- logging
- random
- binascii
- shutil
- tempfile
- base64
- struct

## Additionnal, third-party libraries :

- pyperclip
- mediafire
- requests
- praw
- beautifulsoup4
- patreon
- pycrypto (not pycryptodome)
- pymysql
