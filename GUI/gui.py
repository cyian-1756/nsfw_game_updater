#-*- encoding:utf8 -*-
#!/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import time
import configparser
import json
import requests
import re
import platform
import os
import mediafire
import pyperclip
import webbrowser
import urllib.request
from bs4 import BeautifulSoup
import subprocess
import zipfile
import logging
import sys
import pymysql.err as pymysqlerr

from constants import *
from options import OptionGUI
from download_thread import *
from add_new import AddNewGUI
from get_from_reddit import GetFromRedditGUI
from mega_downloader import MegaDownloader
from sql import SQLHandler
from utils import *
from tkinter_ext import *

logging.basicConfig(filename='log.log', format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
sys.stdout = LoggerWriter(logging.debug)
sys.stderr = LoggerWriter(logging.warning)

class GUI(tk.Frame):
	@classmethod
	def main(cls):
		root = tk.Tk()
		root.title("NSFW Game Manager")
		try:
			root.iconbitmap(default="favicon.ico")
		except tk.TclError:
			#root.iconphoto(tk.PhotoImage("favicon.gif"))
			root.iconbitmap('@favicon.xbm')
		tk.Grid.rowconfigure(root, 0, weight=1)
		tk.Grid.columnconfigure(root, 0, weight=1)
		gui = cls(root)
		for i in range(50):
			tk.Grid.rowconfigure(gui, i, weight=1)
			tk.Grid.columnconfigure(gui, i, weight=1)
		gui.grid(row=0,column=0, sticky="nsew")
		gui.mainloop()
		return gui

	def __init__(self, master=None, from_github=False):
		logging.debug("Started NSFW Game Manager")
		logging.debug("---------------------")
		tk.Frame.__init__(self,master)
		self.init_constants()
		self.master = master
		try:
			_jsonfile = open('games.json', 'r')
			self.json_data = json.loads(_jsonfile.read())
			_jsonfile.close()
		except FileNotFoundError:
			if from_github:
				self.json_data = requests.get("https://raw.githubusercontent.com/cyian-1756/nsfw_game_updater/master/games.json").json()
			else:
				try:
					with SQLHandler() as handler:
						self.json_data = handler.retrieve_json("main")
				except pymysqlerr.MySQLError() as e:
					logging.error("PyMySQL Error : "+e)
					logging.debug("Trying to get the db from github...")
					try:
						self.json_data = requests.get("https://raw.githubusercontent.com/cyian-1756/nsfw_game_updater/master/games.json").json()
					except requests.ConnectionError() as e:
						logging.error("Requests Error : "+e)
						logging.debug("Cannot connect to github... Now exiting...")
						self.on_closing()

		self.platformToDownload = tk.StringVar()
		self.search_string = tk.StringVar()
		self.search_string.trace("w", self.on_search_change_callback)
		self.tree_items_ids = []

		self.threads = []
		self.options_gui = None
		self.add_game_gui = None
		self.reddit_gui = None
		#Other initialization methods
		self.init_contextual()
		self.init_layout()
		self.init_binds()
		pass
#INIT METHODS

	def init_constants(self):
		config = configparser.ConfigParser()
		config.read("config.cfg")
		try:
			self.download_path = config["OPTIONS"]["DOWNLOAD_PATH"]
		except KeyError:
			self.download_path = "./downloads/"
		try:
			self.installation_path = config["OPTIONS"]["INSTALLATION_PATH"]
		except KeyError:
			self.installation_path = "./install/"
		try:
			self.downloaded_games = config["DOWNLOADED_GAMES"]
		except KeyError:
			self.downloaded_games = {}
		try:
			self.use_pending_db = config["OPTIONS"]["USE_PENDING_DB"].lower() in ("yes", "true", "t", "1", "y")
		except KeyError:
			self.use_pending_db = False
		try:
			self.chunksize = int(config["OPTIONS"]["CHUNKSIZE"])
		except KeyError:
			self.chunksize = 1024
		try:
			self.rated_games = config["RATED_GAMES"]
		except KeyError:
			self.rated_games = {}
	def init_binds(self):
		self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.master.bind('<Control-c>', self.onCtrlC)
		self.master.bind('<Control-d>', self.onCtrlD)
		self.master.bind('<Control-w>', self.mark_as_downloaded)
		self.master.bind('<Control-q>', self.go_to_patreon)
		self.master.bind('<Button-3>', self.display_contextual)
		self.master.bind('<Home>', self.onHomeKey)
		self.master.bind('<End>', self.onEndKey)
		self.master.bind('<Prior>', self.onPgUpKey)
		self.master.bind('<Next>', self.onPgDnKey)
		pass

	def init_contextual(self):
		self.contextual_menu = tk.Menu(self, tearoff=0)
		self.contextual_menu.add_command(label='Copy Link to Clipboard', command=self.onCtrlD)
		self.contextual_menu.add_command(label='Copy Data to Clipboard', command=self.onCtrlC)
		self.contextual_menu.add_command(label='Visit Graphtreon Page', command=self.visit_graphtreon)
		self.contextual_menu.add_command(label='Visit Patreon Page', command=self.go_to_patreon)
		self.contextual_menu.add_command(label='Mark as Downloaded', command=self.mark_as_downloaded)
		self.contextual_menu.add_separator()
		self.contextual_menu.add_command(label="Edit Entry", command=self.edit_current_game)
		self.contextual_menu.add_command(label="Hide Item", command=self.hide_item)
		self.ratingmenu = tk.Menu(self)
		for i in range(5):
			self.ratingmenu.add_command(label=rating_as_stars(i+1), command=lambda x=i+1:self.rate_game(x))
		self.contextual_menu.add_cascade(label="Rate Game", menu=self.ratingmenu)

	def init_layout(self):
		self.menubar = tk.Menu(self)
		filemenu = tk.Menu(self)
		filemenu.add_command(label='Copy Link to Clipboard', command=self.onCtrlD)
		filemenu.add_command(label='Copy Data to Clipboard', command=self.onCtrlC)
		filemenu.add_command(label='Mark as Downloaded', command=self.mark_as_downloaded)
		filemenu.add_command(label='Visit Patreon Page', command=self.go_to_patreon)
		filemenu.add_separator()
		filemenu.add_command(label='Check for updates', command=self.check_update)
		filemenu.add_separator()
		filemenu.add_command(label='Open Download folder', command=self.open_explorer)
		editmenu = tk.Menu(self)
		editmenu.add_command(label="Add New Game", command=self.add_new_game)
		editmenu.add_command(label="Edit Selected Entry", command=self.edit_current_game)
		editmenu.add_command(label="Open Reddit Scraper", command=self.open_reddit_scraper)
		dbmenu = tk.Menu(self)
		dbmenu.add_command(label="Save main database locally", command=self.save_database)
		dbmenu.add_command(label="Remove local main database", command=self.remove_local_db)
		dbmenu.add_separator()
		dbmenu.add_command(label="Save pending database locally", command=self.save_pending_database)
		dbmenu.add_command(label="Remove local pending database", command=self.remove_local_pending_db)
		dbmenu.add_separator()
		dbmenu.add_command(label="Show all hidden items", command=self.show_hidden_items)
		toolsmenu = tk.Menu(self)
		toolsdict = {
		"unrpyc":"open:https://github.com/CensoredUsername/unrpyc/releases",
		"RPG Maker RTP":"open:http://www.rpgmakerweb.com/download/additional/run-time-packages",
		"Adobe AIR": "open:https://get.adobe.com/fr/air/",
		"Adobe Shockwave Flash Player": "open:https://get.adobe.com/fr/shockwave/",
		"Unity Web Player" : "open:https://unity3d.com/fr/webplayer"
		}
		for key, value in toolsdict.items():
			toolsmenu.add_command(label="Download {}".format(key), command=lambda x=value:self.download_tool(x))
		helpmenu = tk.Menu(self)
		helpmenu.add_command(label="About", command=self.about)
		helpmenu.add_command(label="Help", command=self.help)

		self.menubar.add_cascade(label="File", menu=filemenu)
		self.menubar.add_cascade(label="Edit", menu=editmenu)
		self.menubar.add_cascade(label="Database", menu=dbmenu)
		self.menubar.add_command(label="Options", command=self.open_options)
		self.menubar.add_cascade(label="Tools/Runtimes", menu=toolsmenu)
		self.menubar.add_cascade(label="?", menu=helpmenu)
		self.master.config(menu=self.menubar)

		self.init_treeview()
		self.search_entry = EntryWithPlaceholder(self, textvariable=self.search_string, placeholder="<category>:<search>")
		self.search_entry.grid(row=0, column=1, columnspan=14, sticky="we")
		tk.Label(self, text="Search :").grid(row=0, column=0)
		self.download_button = tk.Button(self, text="Download/Update", command=self.download_selected_game)
		self.download_button.grid(row=2, column=0, padx=0)
		tk.Button(self, text="Pause/Resume", command=self.pause_resume_download).grid(row=2, column=1, padx=0)
		self.platformCombo = ttk.Combobox(self, textvariable = self.platformToDownload, state='readonly', values=("Automatic", "Windows", "Linux", "MacOS", "Android"))
		self.platformCombo.grid(row=2, column=2)
		self.platformCombo.current(0)
		self.progress = tk.DoubleVar()
		self.progressbar = ttk.Progressbar(self, mode="determinate", maximum=100, variable=self.progress)
		self.progressbar.grid(row=2, column=3, columnspan=11, sticky="ew", padx=0)
		tk.Button(self, text="Cancel", command=self.cancel_download).grid(row=2, column=14, padx=0)


		self.custom_loop()
		pass

	def init_treeview(self):
		columns=("Developer", "Game", "Setting", "Engine", "Genre", "Visual style", "Animation", "Rating")
		self.columns = columns
		treeframe = tk.Frame(self)
		treeframe.grid(row=1, column=0, columnspan=15, sticky="nsew")

		self.treeview = ttk.Treeview(treeframe, columns = columns, show="headings", height=30)
		def treeview_sort_column(tv, col, reverse):
			l = [(tv.set(k, col), k) for k in tv.get_children('')]
			l.sort(reverse=reverse)
			# rearrange items in sorted positions
			for index, (val, k) in enumerate(l):
				tv.move(k, '', index)
			# reverse sort next time
			tv.heading(col, command=lambda _col=col: \
						treeview_sort_column(tv, col, not reverse))
		for column in columns:
			self.treeview.column(column, anchor = tk.CENTER, stretch=True)
			self.treeview.heading(column, text=column.capitalize(), command=lambda _col=column: \
									treeview_sort_column(self.treeview, _col, False))
		self.treeview.grid(row=0, column=0, columnspan=14, sticky="nsew")
		scrollbar = ttk.Scrollbar(treeframe, orient="vertical", command=self.treeview.yview)
		scrollbar.grid(row=0, column=15, sticky="ns")
		self.treeview.tag_configure('has_update', background="IndianRed2")
		self.treeview.tag_configure('paid', background="AntiqueWhite1")
		self.treeview.tag_configure('hide')
		self.treeview.tag_configure('show')
		#self.tree_tooltips = TooltipTreeWrapper(self.treeview, background="light goldenrod", foreground="black")

		self.add_games_to_tree()
		self.update_treeview()

#EVENT METHODS
	def on_search_change_callback(self, *args):
		search = self.search_string.get().lower().split(",")
		search = [s.lower() for s in search]
		if search == ['']:
			for item in self.tree_items_ids:
				self.show_item(item)
		for item in self.tree_items_ids:
			values = self.get_json_from_tree(item_to_get=self.treeview.item(item))
			if values is None:
				continue
			for subsearch in search:
				for key in values.keys():
					if subsearch.startswith(key.lower()+":"):
						subsearch = subsearch.split(":")[1]
						if subsearch not in values[key].lower() and subsearch:
							self.hide_item(item)
						else:
							self.show_item(item)
		pass

	def on_closing(self):
		config = configparser.ConfigParser()
		config["OPTIONS"] = {}
		config["OPTIONS"]["DOWNLOAD_PATH"] = self.download_path
		config["OPTIONS"]["INSTALLATION_PATH"] = self.installation_path
		config["OPTIONS"]["CHUNKSIZE"] = str(self.chunksize)
		config["OPTIONS"]["USE_PENDING_DB"] = str(self.use_pending_db)
		config["DOWNLOADED_GAMES"] = self.downloaded_games
		config["RATED_GAMES"] = self.rated_games

		with open('config.cfg', 'w') as configfile:
			config.write(configfile)
		self.master.destroy()

	def onKeypressEvent(self, event):
		pass

	def onHomeKey(self, event):
		self.treeview.yview(tk.MOVETO, 0)
		pass

	def onEndKey(self, event):
		self.treeview.yview(tk.MOVETO, 1)
		pass

	def onPgDnKey(self, event):
		self.treeview.yview(tk.SCROLL, 1, tk.PAGES)
		pass

	def onPgUpKey(self, event):
		self.treeview.yview(tk.SCROLL, -1, tk.PAGES)
		pass

	def onCtrlC(self, event=None):
		item = self.get_json_from_tree(True)
		if item is not None:
			pyperclip.copy("; ".join(item))
		pass

	def onCtrlD(self, event=None):
		game_json = self.get_json_from_tree()
		if game_json is None:
			return
		if self.platformToDownload.get() == "Automatic":
			current_os = platform.system().lower()
		else:
			current_os = self.platformToDownload.get().lower()
		if current_os != '':
			url = game_json["download_link_{}".format(current_os)]
			pyperclip.copy(url)
		pass

	def display_contextual(self, event):
		for i in range(1, 6):
			self.ratingmenu.entryconfig(i, foreground="gold2")
		try:
			iid = self.treeview.identify_row(event.y)
			if iid:
				# mouse pointer over item
				self.treeview.selection_set(iid)
				self.treeview.focus(iid)
				try:
					game = self.treeview.item(iid)["values"][self.columns.index("Game")].lower()
					rating = int(self.rated_games[game])
					self.ratingmenu.entryconfig(rating, foreground="SteelBlue3")
				except KeyError as e:
					logging.exception("Error on dict")
					pass
			self.contextual_menu.tk_popup(event.x_root, event.y_root, 0)
		except Exception as e:
			logging.exception("Error on display_contextual function : {}".format(e))
		finally:
			# make sure to release the grab (Tk 8.0a1 only)
			self.contextual_menu.grab_release()
#Update methods

	def update_treeview(self):
		if self.use_pending_db:
			with SQLHandler() as handler:
				self.add_games_to_tree(handler.retrieve_json())

	def custom_loop(self):
		for idx, thread in enumerate(self.threads):
			if not thread.is_alive:
				self.threads.pop(idx)
				self.progress.set(0)
		try:
			prg = sum([t.progress for t in self.threads])//len(self.threads)
		except ZeroDivisionError:
			prg = 0
		self.progress.set(prg)

		for item in self.treeview.tag_has("hide"):
			self.treeview.detach(item)
		for item in [i for i in self.tree_items_ids if "show" in self.treeview.item(i)["tags"]]:#self.treeview.tag_has("show"):
			self.treeview.reattach(item, self.treeview.parent(item), self.treeview.index(item))

		self.update_idletasks()
		self.update()
		self.after(50, self.custom_loop)

	def check_update(self, game=None):
		nb = 0
		for item in self.treeview.get_children():
			if game is None:
				game = self.get_json_from_tree(item_to_get=self.treeview.item(item))
			if game["game"] in self.downloaded_games.keys():
				if checkversion(game["latest_version"], self.downloaded_games[game["game"]]):
					nb += 1
					self.treeview.item(item, tags=('has_update'))
		if nb == 0:
			messagebox.showinfo("Information", "No updates found")
		elif nb == 1:
			messagebox.showinfo("Information", "1 update found")
		else:
			messagebox.showinfo("Information", "{} updates found".format(nb))

	def save_database(self):
		with open('games.json', 'w', encoding="utf-8") as f:
			 f.write(json.dumps(self.json_data, indent=4, sort_keys=True))

	def remove_local_db(self):
		if messagebox.askyesno(title="Remove local database", message="Are you sure ?"):
			os.remove("games.json")

	def save_pending_database(self):
		with SQLHandler() as handler:
			handler.retrieve_json(write_local=True)

	def remove_local_pending_db(self):
		if messagebox.askyesno(title="Remove local database", message="Are you sure ?"):
			os.remove("pending_approval.json")

	def mark_as_downloaded(self):
		game_json = self.get_json_from_tree()
		if game_json is not None:
			self.downloaded_games[game_json["game"]] = game_json["version"]
		pass

	def rate_game(self, rating):
		game = self.get_json_from_tree()
		if game["game"].lower() not in self.rated_games.keys():
			with SQLHandler() as handler:
				newrating, nb_votes = handler.update_rating(game["game"], rating)
				game["rating"] = newrating
				game["nb_votes"] = nb_votes
			self.update_game_in_tree(game)
			self.rated_games[game["game"].lower()] = str(rating)
		else:
			with SQLHandler() as handler:
				newrating, nb_votes = handler.update_rating(game["game"], rating, self.rated_games[game["game"].lower()])
				game["rating"] = newrating
				game["nb_votes"] = nb_votes
			self.update_game_in_tree(game)
			self.rated_games[game["game"].lower()] = str(rating)
		pass
#Open Toplevel windows methods
	def go_to_patreon(self):
		game_json = self.get_json_from_tree()
		page = requests.get(game_json["graphtreon"])
		soup = BeautifulSoup(page.content, "html.parser")
		for link in soup.find_all('a'):
			if str(link.get('href')).startswith("https://www.patreon.com/") and "graphtreon" not in str(link.get('href')):
				webbrowser.open(link.get('href'), new=2)
				return
	def open_explorer(self):
		p = self.download_path if ":\\" in self.download_path else os.getcwd()+self.download_path
		subprocess.Popen(r'explorer /select,"{}"'.format(p))
	def about(self):
		message = """
		NSFW Game Manager GUI by Dogeek
		For additional information, check out
		https://goo.gl/6LEQk9
		License : GPL-3.0
		"""
		messagebox.showinfo("About", message)
		pass

	def edit_current_game(self):
		if self.add_game_gui is None:
			data = self.get_json_from_tree()
			if data is not None:
				self.add_game_gui = AddNewGUI(master=self, editdata=data)
				self.add_game_gui.mainloop()
		pass

	def add_new_game(self):
		if self.add_game_gui is None:
			self.add_game_gui = AddNewGUI(master=self)
			self.add_game_gui.mainloop()
		pass

	def help(self):
		webbrowser.open("help.html", new=2)
		pass

	def open_reddit_scraper(self):
		if self.reddit_gui is None:
			self.reddit_gui = GetFromRedditGUI(master=self)
			self.reddit_gui.mainloop()
		pass

	def open_options(self):
		if self.options_gui is None:
			self.options_gui = OptionGUI(master=self)
			self.options_gui.mainloop()
		pass

	def visit_graphtreon(self):
		game_json = self.get_json_from_tree()
		if game_json is not None:
			webbrowser.open(game_json["graphtreon"], new=2)
		pass

	def hide_item(self, item=None):
		if item is None:
			item = self.treeview.focus()
		itemtags = list(self.treeview.item(item)["tags"])

		if "show" in itemtags:
			itemtags.remove("show")
			itemtags.append("hide")
		self.treeview.item(item, tags=itemtags)

	def show_item(self, item):
		itemtags = list(self.treeview.item(item)["tags"])
		if "hide" in itemtags:
			itemtags.remove("hide")
			itemtags.append("show")
		self.treeview.item(item, tags=itemtags)

	def show_hidden_items(self): #FIXME doesn't do anything???
		t = [self.treeview.item(item)["tags"] for item in self.tree_items_ids]
		for item in self.tree_items_ids:
			if "hide" in list(self.treeview.item(item)["tags"]):
				self.show_item(item)
	#Utility methods
	def download_tool(self, url):
		if url.startswith("open:"):
			webbrowser.open(url.split("open:")[1], new=2)
		else:
			r = requests.get(url, stream=True)
			with open(os.getcwd()+SEP+"tools"+SEP+url.split("/")[-1], 'wb') as f:
				for chunk in r.iter_content(chunk_size=self.chunksize):
					f.write(chunk)
	def add_games_to_tree(self, games=None):
		if games is None:
			games=self.json_data
		if type(games) != type(list()):
			tmp = []
			tmp.append(games)
			games = tmp.copy()
		for i, info in enumerate(games):
			if info["developer"] != "developer":
				formatted = (info["developer"], info["game"], info["setting"], info["engine"], info["genre"], \
				info["visual_style"], info["animation"], rating_as_stars(info["rating"]))
				tags = ['show']
				if "paid" in info["public_build"]:
					tags.append('paid')
				self.tree_items_ids.append(self.treeview.insert('', 'end', values = formatted, tags=tags))
				#self.tree_tooltips.add_tooltip(self.tree_items_ids[-1], "Current votes : {}".format(info["nb_votes"]))

	def update_game_in_tree(self, game_json):
		for iid in self.tree_items_ids:
			item = self.treeview.item(iid)
			if item["values"][self.columns.index("Game")].lower() == game_json["game"].lower():
				tmp = []
				for col in self.columns:
					if "rating" in col.lower():
						tmp.append(rating_as_stars(game_json[col.lower()]))
						continue
					elif "visual style" in col.lower():
						tmp.append(game_json["visual_style"])
					else:
						tmp.append(game_json[col.lower()])
				tmp = tuple(tmp)
				self.treeview.item(iid, values=tmp)

	def get_json_from_tree(self, return_item=False, item_to_get=None):
		try:
			if item_to_get is None:
				item = self.treeview.item(self.treeview.focus())["values"]
			else:
				item = item_to_get["values"]
			if return_item:
				return item
			i = self.columns.index("Game")
			gamename = item[i]
			for g in self.json_data:
				if g["game"] == gamename:
					return g
		except IndexError:
			messagebox.showerror("Error", message="You need to select an item first !")
			return

	def on_complete_callback(self, name, path):
		def can_install(filename):
			return ".zip" in filename

		if can_install(name):
			pwd = None
			if name.lower() == "cursed armor":
				pwd = "wolfzq"
			msg = "Do you wish to install {}?".format(name)
			#if pwd is not None:
			#	msg += "\nPassword: {}".format(pwd)
			if messagebox.askyesno(title="Install game ?", message="Do you wish to install the game?", default='no'):
				ipath = self.installation_path
				if not ipath.endswith("/") and not ipath.endswith("\\"):
					if platform.system().lower()=="windows":
						ipath += "\\"
					else:
						ipath+="/"
				zip_ref = zipfile.ZipFile(path+name, 'r')
				zip_ref.extractall(ipath+name.split(".zip")[0], pwd=pwd)
				zip_ref.close()
		#else:
		#	messagebox.showinfo("Information", message="Automatic install only works with zip files at the moment")



	def download_selected_game(self): #It would be simpler if each game had its own ID, as well as to version track later on.
		game_json = self.get_json_from_tree()
		if game_json is None:
			return
		if "paid" in game_json["public_build"].lower():
			messagebox.showinfo("Information", message="This game needs to be bought !")
			return
		item = self.treeview.item(self.treeview.focus())
		itemtags = item["tags"]
		if self.platformToDownload.get() == "Automatic":
			current_os = platform.system().lower()
		else:
			current_os = self.platformToDownload.get().lower()
		if current_os != '':
			url = game_json["download_link_{}".format(current_os)]
			version = game_json["latest_version"]
		if self.download_path=="/" or self.download_path == "":
			download = os.getcwd()+'\\'
		else:
			download = self.download_path
		if url == "-":
			messagebox.showerror("Error", "This game isn't supported by your platform yet.")
		elif url.lower() == "non-static link":
			messagebox.showerror("Error", "The link for this game is non-static.")
		elif url == "":
			messagebox.showerror("Error", "No link found in the database for this game.")
		else:
			if "has_update" in itemtags or game_json["game"] not in self.downloaded_games:
				if "has_update" in itemtags:
					self.treeview.item(item, tags=())
				if "drive.google.com" in url:
					def get_confirm_token(response):
						for key, value in response.cookies.items():
							if key.startswith('download_warning'):
								return value

						return None
					URL = "https://docs.google.com/uc?export=download"
					if 'id' in url:
						id_ = url.split("id=")[-1]
					elif "/d/" in url:
						id_ = url.split('https://drive.google.com/file/d/')[1].split('/view?usp=sharing')[0]
					session = requests.Session()
					response = session.get(URL, params = { 'id' : id_ }, stream = True)
					token = get_confirm_token(response)
					if token:
						params = { 'id' : id_, 'confirm' : token }
						r = session.get(URL, params = params, stream = True)
						name = game_json["game"].capitalize()+".zip"
				elif url.startswith("open:"):
					webbrowser.open(url.split("open:")[1], new=2)
					return
				elif "mega.nz" in url:
					self.threads.append(MegaDownloader(url, download, self.on_complete_callback))
					self.threads[-1].daemon = True
					self.threads[-1].start()
					return
				else:
					if "mediafire" in url:
						api = mediafire.MediaFireApi()
						response = api.file_get_links(url.split("/")[url.split('/').index("file")+1])
						url = response['links'][0]['normal_download']
					elif "itch.io" in url:
						headers = {
							'Pragma': 'no-cache',
							'Accept-Encoding': 'gzip, deflate, br',
							'Accept-Language': 'en-US,en;q=0.9',
							'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
							'Accept': '*/*',
							'Cache-Control': 'no-cache',
							'X-Requested-With': 'XMLHttpRequest',
							'Connection': 'keep-alive',
							'DNT': '1'
						}
						response = requests.post(url, headers=headers)
						print(response)
						url = response.json()["url"]
					r = requests.get(url, stream=True)
					if r.status_code == 200:
						size = None
						try:
							size = int(r.headers['Content-Length'])
							d = r.headers['content-disposition']
							name = re.findall("filename=(.+)", d)[0]
						except KeyError as e:
							logging.warning("Error on file downloading, name:{}, error :{}".format(game_json["game"], e))
							name = url.split("/")[-1:][0]
							if size is None:
								size = 5e6
					else:
						messagebox.showerror("Error", message="Exception in downloading, response returned error code {}".format(r.status_code))
						return
				if name == "":
					name = game_json["game"]+".zip"
				self.threads.append(DownloadThread(r, self.chunksize, size, download, name, self.on_complete_callback))
				self.threads[-1].daemon = True
				self.threads[-1].start()

			self.downloaded_games[game_json["game"]] = version
		pass
	def pause_resume_download(self):
		try:
			for thread in self.threads:
				if thread.paused:
					thread.resume()
				else:
					thread.pause()
		except AttributeError:
			messagebox.showerror("Error", message="You must be downloading a game.")
		pass

	def cancel_download(self):
		try:
			for thread in self.threads:
				thread.stop()
		except AttributeError:
			messagebox.showerror("Error", message="You must be downloading a game.")
		pass
	pass


if __name__ == "__main__":
	gui = GUI.main()
