import configparser

OPTIONSOPEN = False
config = configparser.ConfigParser()
config.read("config.cfg")
GEOMETRY = config["GEOMETRY"]["x"] + "x" + config["GEOMETRY"]["y"]
