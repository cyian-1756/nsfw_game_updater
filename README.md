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

[] Add download links for all games currently in the list

[] Add the latest version of all download links in the list

[] Write a web scraper to check if a new version of the game is out 

[X] Update main.py to allow for downloading games without using outside tools where ever possible

[] Add GUI