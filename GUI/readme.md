# NSFW Game Manager GUI

This GUI has been made by Dogeek (http://github.com/Dogeek) based on cyian-1756's CLI.
The GUI has been made using the Tk/Tcl wrapper for python, tkinter.

## Features :

### Implemented :
- Adding new games to the database
- Downloading and Updating games
- Editing games in the database
- Copying the links to the clipboard
- Copying the whole line's data to the clipboard
- check for game updates
- Sorting games by genre, developer, etc.
- A super duper ugly help page
- Options to set the window size, the download path etc

### Planned :

- Scrape reddit r/lewdgames and r/nsfwgaming for updates, and new releases to add them to the database
- Syncing every user's databases
- Scraping games' websites to look for updates.
- Auto-Updating the database
- Improved Help page
- Game rating (each user may rate the game, shown rating will be the average rating)
- Advanced/Simple view of the tree (to show only the relevant info)
- Automatic unzipping/install of the games to the specified installation directory
- Patreon integration to pledge from the app itself
- itch.io integration to buy/donate from the app itself

# Mediafire functionnality

I created a mediafire account for this app. It may or may not be useful, as of right now, it serves no purpose, but here are the credentials :

- email : nsfwgamemanager@gmail.com
- password : nsfwgame

# TO DO List :

- [x] implement unzipping the downloaded files if it is an archive.
- [x] add a 'View in explorer' command
- [ ] implement mega.nz downloading
- [x] implement auto-refresh of the game list when you add a new game
- [x] implement updating of games
- [x] fix toplevel windows not showing up the second time you click on the button (problem with global vars ??)
- [x] fix toplevel windows not retaining information on reopening
- [x] change geometry based on selected resolution in options window
- [ ] add a tab in the options window for advanced options, such as setting up a reddit account to use with praw, mediafire account, mega.nz account, instead of the default ones (in case of download cap if too many users)
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

## Additionnal, third-party libraries :

- pyperclip
- mediafire
- requests
- praw
- beautifulsoup4
- patreon
