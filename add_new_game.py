import pyfuncs
import argparse

parser = argparse.ArgumentParser(description="Keep track of your NSFW games")
parser.add_argument("--game", help="Game name", required=True)
parser.add_argument("--public-build", help="Link to the pages public builds", required=True)
parser.add_argument("--setting", help="The setting the game takes place in")
parser.add_argument("--developer", help="The dev", required=True)
parser.add_argument("--engine", help="The engine the game uses")
parser.add_argument("--visual-style", help="The visual style of the game")
parser.add_argument("--genre", help="The game genre")
parser.add_argument("--has-animation", help="Does the game have animations (Yes or No)", default="No")
parser.add_argument("--latest-version", help="The latest version of the game")
parser.add_argument("--download-link-windows", help="The windows download link", default="Doesn't support")
parser.add_argument("--download-link-linux", help="The Linux download link", default="Doesn't support")
parser.add_argument("--download-link-mac", help="The Mac download link", default="Doesn't support")
parser.add_argument("--download-link-android", help="The android download link", default="Doesn't support")
parser.add_argument("--graphtreon", help="Link to the devs graphtreon", default="Doesn't have")
args = parser.parse_args()

json_to_add = {\
"game": args.game, \
"public_build": args.public_build,\
"setting":args.setting,\
"developer": args.developer,\
"engine": args.engine,\
"visual_style":args.visual_style,\
"genre":args.genre,\
"animation":args.has_animation,\
"latest_version":args.latest_version,\
"download_link_windows": pyfuncs.check_url(args.download_link_windows),\
"download_link_mac": pyfuncs.check_url(args.download_link_mac),\
"download_link_linux": pyfuncs.check_url(args.download_link_linux),\
"download_link_android": pyfuncs.check_url(args.download_link_android)}

pyfuncs.add_new_game(json_to_add)
