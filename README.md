# NFSW game updater

This project allows people to keep track of NSFW games they enjoy

## Adding a game

Use `add_new_game.py`


## Usage

### Searching

The program allows search the game database by developer, game name, setting, engine and genre

Example: `python3 main.py --list-by-dev mity`

### Downloading

The program allows downloading some games

Example: `python3 main.py --download --game-name "trials in tainted space" --os windows`

## TODO

- [ ] Add download links for all games currently in the list

- [ ] Add the latest version of all download links in the list

- [ ] Write a web scraper to check if a new version of the game is out

- [x] Update main.py to allow for downloading games without using outside tools where ever possible

- [x] Add GUI

## GUI (Graphical User Interface) :

The detailled readme.md is in the GUI folder.
The gui has been made using the Tk/Tcl wrapper tkinter.

### Features :

- Adding new games to the database
- Downloading and Updating games
- Editing games in the database
- Copying the links to the clipboard
- Copying the whole line's data to the clipboard
- check for game updates
- Sorting games by genre, developer, etc.
- A super duper ugly help page
- Options to set the window size, the download path etc
- Scrape reddit r/lewdgames and r/nsfwgaming for updates, and new releases to add them to the database
- Advanced/Simple view of the tree (to show only the relevant info)
- Syncing every user's databases (WIP, database is now shared, and remote)
- Auto-Updating the database
- Visit Patreon/Graphtreon pages from the application
- Keyboard shortcuts, contextual menu, all for a better UX

### Planned :

- Improve reddit integration to automatically enter the info into the database
- Scraping games' websites to look for updates.
- Improved Help page
- Game rating (each user may rate the game, shown rating will be the average rating)
- Automatic unzipping/install of the games to the specified installation directory
- Patreon integration to pledge from the app itself
- itch.io integration to buy/donate from the app itself
