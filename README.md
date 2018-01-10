# NFSW game updater

This project allows people to keep track of NSFW games they enjoy

## Adding a game

To add a game you have to edit games.csv. When adding a game you have to include 

* The developer (Under developer)

* The games title (Under game)

* The game engine (Under engine)

* The genre (Under genre)

* Where updates to the game will be posted (Under public_build)

* The latest version (Under latest_version)

* A download link to all the OSs the game was compiled for (Under download_link_$OS)

When adding a game you may include

* The visual style (Under visual_style)

* The setting (Under setting)

* A link to the devs graphtreon (Under graphtreon)


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