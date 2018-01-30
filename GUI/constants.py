import configparser
import os
import platform

if platform.system().lower() == "windows":
	SEP = "\\"
else:
	SEP = "/"

config = configparser.ConfigParser()
config.read("config.cfg")
try:
	GEOMETRY = config["OPTIONS"]["GEOMETRY"]
except KeyError:
	GEOMETRY = "800x600"
try:
	DOWNLOAD_PATH = config["OPTIONS"]["DOWNLOAD_PATH"]
except KeyError:
	DOWNLOAD_PATH = "./downloads/"
try:
	INSTALLATION_PATH = config["OPTIONS"]["INSTALLATION_PATH"]
except KeyError:
	INSTALLATION_PATH = "./install/"
try:
	DOWNLOADED_GAMES = config["DOWNLOADED_GAMES"]
except KeyError:
	DOWNLOADED_GAMES = {}
try:
	USE_PENDING_DB = config["OPTIONS"]["USE_CONFIG_DB"].lower() in ("yes", "true", "t", "1", "y")
except KeyError:
	USE_PENDING_DB = False
try:
	CHUNKSIZE = int(config["OPTIONS"]["CHUNKSIZE"])
except KeyError:
	CHUNKSIZE = 1024

#####---------GRAPHICS----------#######

#Folder icon image, as an xbm image, the mask is separated by the '-' character.
FOLDER_ICON = """#define folder_width 16
#define folder_height 16
static unsigned char folder_bits[] = {
   0x00, 0x00, 0x3f, 0x00, 0xf1, 0x7f, 0x01, 0x40, 0xfd, 0xff, 0x07, 0x80,
   0x03, 0x80, 0x03, 0x80, 0x03, 0x80, 0x03, 0x80, 0x01, 0xc0, 0x01, 0x40,
   0x01, 0x40, 0x01, 0x40, 0xfe, 0x7f, 0x00, 0x00 };-#define folder_mask_width 16
#define folder_mask_height 16
static unsigned char folder_mask_bits[] = {
   0x00, 0x00, 0x3f, 0x00, 0xff, 0x7f, 0xff, 0x7f, 0xff, 0xff, 0xff, 0xff,
   0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x7f,
   0xff, 0x7f, 0xff, 0x7f, 0xfe, 0x7f, 0x00, 0x00 };
"""
