# NSFW Game Manager GUI

This GUI has been made by Dogeek (http://github.com/Dogeek) based on cyian-1756's CLI.

# Mediafire functionnality

I created a mediafire account for this app. It may or may not be useful, as of right now, it serves no purpose, but here are the credentials :

- email : nsfwgamemanager@gmail.com
- password : nsfwgame

# TO DO List :

- [ ] implement mega.nz downloading
- [x] implement auto-refresh of the game list when you add a new game
- [ ] implement updating of games
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

## Additionnal libraries :

- pyperclip
- mediafire
- requests
- praw
