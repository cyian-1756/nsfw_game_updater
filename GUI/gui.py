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

from constants import *
from functions import *
from options import OptionGUI
from download_thread import *
from add_new import AddNewGUI
from get_from_reddit import GetFromRedditGUI
from mega_downloader import MegaDownloader
from sql import SQLHandler
from utils import *

logging.basicConfig(filename='log.log', format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
sys.stdout = LoggerWriter(logging.debug)
sys.stderr = LoggerWriter(logging.warning)

class GUI(tk.Frame): #TODO: lua mem usage filter to display in a separate widget to not clutter the text widget, add scroll bar, try to auto reload if the lua file is deleted & add a about/options menu
	def __init__(self, master=None):
		tk.Frame.__init__(self,master)
		self.master = master
		try:
			_jsonfile = open('games.json', 'r')
			self.json_data = json.loads(_jsonfile.read())
			_jsonfile.close()
		except FileNotFoundError:
			self.json_data = requests.get("https://raw.githubusercontent.com/cyian-1756/nsfw_game_updater/master/games.json").json()

		self.downloaded_games = {} if DOWNLOADED_GAMES is None else DOWNLOADED_GAMES
		self.platformToDownload = tk.StringVar()
		self.thread = None
		self.options_gui = None
		self.add_game_gui = None
		self.reddit_gui = None
		#Other initialization methods
		self.init_contextual()
		self.init_layout()
		self.init_binds()
		pass
#INIT METHODS
	def init_binds(self):
		self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.master.bind('<Control-c>', self.onCtrlC)
		self.master.bind('<Control-d>', self.onCtrlD)
		self.master.bind('<Control-w>', self.mark_as_downloaded)
		self.master.bind('<Control-q>', self.go_to_patreon)
		self.master.bind('<Button-3>', self.display_contextual)
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
		editmenu.add_command(label="Save main database locally", command=self.save_database)
		editmenu.add_command(label="Remove local main database", command=self.remove_local_db)
		editmenu.add_separator()
		editmenu.add_command(label="Save pending database locally", command=self.save_pending_database)
		editmenu.add_command(label="Remove local pending database", command=self.remove_local_pending_db)
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
		self.menubar.add_command(label="Options", command=self.open_options)
		self.menubar.add_cascade(label="Tools/Runtimes", menu=toolsmenu)
		self.menubar.add_cascade(label="?", menu=helpmenu)
		self.master.config(menu=self.menubar)

		self.init_treeview()

		self.download_button = tk.Button(self, text="Download/Update", command=self.download_selected_game)
		self.download_button.grid(row=1, column=0)
		self.platformCombo = ttk.Combobox(self, textvariable = self.platformToDownload, state='readonly', values=("Automatic", "Windows", "Linux", "MacOS", "Android"))
		self.platformCombo.grid(row=1, column=1)
		self.platformCombo.current(0)
		self.progress = tk.DoubleVar()
		self.progressbar = ttk.Progressbar(self, mode="determinate", maximum=100, variable=self.progress)
		self.progressbar.grid(row=1, column=2, columnspan=13, sticky="ew")

		self.custom_loop()
		pass

	def init_treeview(self):
		columns=("Developer", "Game", "Setting", "Engine", "Genre", "Visual style", "Animation")
		self.columns = columns
		self.treeview = ttk.Treeview(self, columns = columns, show="headings", height=30)
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
			self.treeview.column(column, anchor = tk.CENTER)
			self.treeview.heading(column, text=column.capitalize(), command=lambda _col=column: \
									treeview_sort_column(self.treeview, _col, False))
		self.treeview.grid(row=0, column=0, columnspan=15, sticky="nsew")
		self.treeview.tag_configure('has_update', background="red")
		self.treeview.tag_configure('paid', background="AntiqueWhite1")
		self.add_games_to_tree()
		self.update_treeview()

#EVENT METHODS
	def on_closing(self):
		config = configparser.ConfigParser()
		config["OPTIONS"] = {}
		config["OPTIONS"]["DOWNLOAD_PATH"] = DOWNLOAD_PATH
		config["OPTIONS"]["INSTALLATION_PATH"] = INSTALLATION_PATH
		config["OPTIONS"]["CHUNKSIZE"] = str(CHUNKSIZE)
		config["OPTIONS"]["USE_PENDING_DB"] = str(USE_PENDING_DB)
		config["DOWNLOADED_GAMES"] = self.downloaded_games

		with open('config.cfg', 'w') as configfile:
			config.write(configfile)
		self.master.destroy()

	def onKeypressEvent(self, event):
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
		try:
			iid = self.treeview.identify_row(event.y)
			if iid:
				# mouse pointer over item
				self.treeview.selection_set(iid)
				self.treeview.focus(iid)
			self.contextual_menu.tk_popup(event.x_root, event.y_root, 0)
		except Exception as e:
			logging.error("Error on display_contextual function : {}".format(e))
		finally:
			# make sure to release the grab (Tk 8.0a1 only)
			self.contextual_menu.grab_release()
#Update methods

	def update_treeview(self):
		columns=("Developer", "Game", "Setting", "Engine", "Genre", "Visual style", "Animation")
		self.columns = columns
		for column in columns:
			self.treeview.column(column, anchor = tk.CENTER)
		if USE_PENDING_DB:
			with SQLHandler as handler:
				self.add_games_to_tree(handler.retrieve_json())

	def custom_loop(self):
		if self.thread is not None:
			if self.thread.is_alive:
				self.progress.set(self.thread.progress)
			else:
				self.progress.set(0)
		self.update_idletasks()
		self.update()
		self.after(50, self.custom_loop)

	def check_update(self, game=None):
		nb = 0
		for item in self.treeview.get_children():
			if game is None:
				game = self.get_json_from_tree(item_to_get=self.treeview.item(item))
			if game["game"] in self.downloaded_games.keys():
				if checkversion(game["latest_version"], DOWNLOADED_GAMES[game["game"]]):
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
		p = DOWNLOAD_PATH if ":\\" in DOWNLOAD_PATH else os.getcwd()+DOWNLOAD_PATH
		subprocess.Popen(r'explorer /select,"{}"'.format(p))
	def about(self):
		message = """
		NSFW Game Manager by Dogeek
		For additional information, check out
		https://github.com/cyian-1756/nsfw_game_updater
		License : GPL-3.0
		"""
		messagebox.showinfo("About", message)
		pass
		a
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
#Utility methods
	def download_tool(self, url):
		if url.startswith("open:"):
			webbrowser.open(url.split("open:")[1], new=2)
		else:
			r = requests.get(url, stream=True)
			with open(os.getcwd()+SEP+"tools"+SEP+url.split("/")[-1], 'wb') as f:
				for chunk in r.iter_content(chunk_size=CHUNKSIZE):
					f.write(chunk)
	def add_games_to_tree(self, games=None):
		if games is None:
			for i, info in enumerate(self.json_data):
				if i != 0:
					formatted = (info["developer"], info["game"], info["setting"], info["engine"], info["genre"], \
					info["visual_style"], info["animation"])
					if "paid" in info["public_build"]:
						self.treeview.insert('', 'end', values = formatted, tags=["paid"])
					else:
						self.treeview.insert('', 'end', values = formatted)
		else:
			for i, info in enumerate(games):
				formatted = (info["developer"], info["game"], info["setting"], info["engine"], info["genre"], \
				info["visual_style"], info["animation"])
				if "paid" in info["public_build"]:
					self.treeview.insert('', 'end', values = formatted, tags=["paid"])
				else:
					self.treeview.insert('', 'end', values = formatted)
		pass

	def update_game_in_tree(self, game_json):
		for item in self.treeview.get_children():
			if item["values"][self.columns.index("Game")].lower() == game_json["game"].lower():
				tmp = []
				for col in self.columns:
					tmp.append(game_json[col.lower()])
				tmp = tuple(tmp)
				self.treeview.item(item, values=tmp)

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
			msg = "Do you wish to install the game?"
			#if pwd is not None:
			#	msg += "\nPassword: {}".format(pwd)
			if messagebox.askyesno(title="Install game ?", message="Do you wish to install the game?", default='no'):
				ipath = INSTALLATION_PATH
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
		if DOWNLOAD_PATH=="/" or DOWNLOAD_PATH == "":
			download = os.getcwd()+'\\'
		else:
			download = DOWNLOAD_PATH
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
					self.thread = MegaDownloader(url, download, self.on_complete_callback)
					self.thread.daemon = True
					self.thread.start()
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
				self.thread = DownloadThread(r, CHUNKSIZE, size, download, name, self.on_complete_callback)
				self.thread.daemon = True
				self.thread.start()
		#self.downloaded_games[game_json["game"]] = version
		pass
	pass


if __name__ == "__main__":
	root = tk.Tk()
	root.title("NSFW Game Manager")
	#root.geometry(GEOMETRY)
	tk.Grid.rowconfigure(root, 0, weight=1)
	tk.Grid.columnconfigure(root, 0, weight=1)
	gui = GUI(root)
	for i in range(50):
		tk.Grid.rowconfigure(gui, i, weight=1)
		tk.Grid.columnconfigure(gui, i, weight=1)
	gui.grid(row=0,column=0, sticky="nsew")
	gui.mainloop()
