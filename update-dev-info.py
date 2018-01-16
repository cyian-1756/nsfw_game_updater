import pyfuncs
import argparse

parser = argparse.ArgumentParser(description="Keep track of your NSFW games")
parser.add_argument("--dev", help="The devs who info we're updating", required=True)
parser.add_argument("--graphtreon", help="The devs graphtreon")
args = parser.parse_args()

if args.graphtreon:
    pyfuncs.update_dev_graphtreon(args.dev, args.graphtreon)