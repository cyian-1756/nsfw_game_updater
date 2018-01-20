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


from constants import *
from functions import *
from options import OptionGUI
from download_thread import *
from add_new import AddNewGUI
from get_from_reddit import GetFromRedditGUI

####FOR SOME REASON self.winfo_width() returns 1 even after self.update_idletasks() FIXME
#For now, set the geometry manually
GEOMETRY = "1920x1080"

class GUI(tk.Frame): #TODO: lua mem usage filter to display in a separate widget to not clutter the text widget, add scroll bar, try to auto reload if the lua file is deleted & add a about/options menu
	def __init__(self, master=None):
		tk.Frame.__init__(self,master)
		self.master = master

		self._jsonfile = open('games.json', 'r')
		self.json_data = json.loads(self._jsonfile.read())
		self._jsonfile.close()
		self.downloaded_games = {} if DOWNLOADED_GAMES is None else DOWNLOADED_GAMES
		self.platformToDownload = tk.StringVar()
		self.thread = None
		self.options_gui = None
		self.add_game_gui = None
		self.reddit_gui = None

		#Other initialization methodsa
		self.init_binds()
		self.init_layout()
		pass

	def init_binds(self):
		self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.master.bind('<Control-c>', self.onCtrlC)
		self.master.bind('<Control-d>', self.onCtrlD)
		self.master.bind('<Control-w>', self.mark_as_downloaded)
		pass

	def init_layout(self):
		self.menubar = tk.Menu(self)
		filemenu = tk.Menu(self)
		filemenu.add_command(label='Copy Link to Clipboard', command=self.onCtrlD)
		filemenu.add_command(label='Copy Data to Clipboard', command=self.onCtrlC)
		filemenu.add_command(label='Mark as Downloaded', command=self.mark_as_downloaded)
		filemenu.add_separator()
		filemenu.add_command(label='Check for updates', command=self.check_update)
		editmenu = tk.Menu(self)
		editmenu.add_command(label="Add New Game", command=self.add_new_game)
		editmenu.add_command(label="Edit Selected Entry", command=self.edit_current_game)
		editmenu.add_command(label="Open Reddit Scraper", command=self.open_reddit_scraper)
		self.menubar.add_cascade(label="File", menu=filemenu)
		self.menubar.add_cascade(label="Edit", menu=editmenu)
		self.menubar.add_command(label="Options", command=self.open_options)
		self.menubar.add_command(label="About", command=self.about)
		self.menubar.add_command(label="Help", command=self.help)
		self.master.config(menu=self.menubar)

		self.init_treeview()

		self.download_button = tk.Button(self, text="Download/Update", command=self.download_selected_game)
		self.download_button.grid(row=1, column=0)
		self.platformCombo = ttk.Combobox(self, textvariable = self.platformToDownload, state='readonly', values=("Automatic", "Windows", "Linux", "MacOS", "Android"))
		self.platformCombo.grid(row=1, column=1)
		self.platformCombo.current(0)
		self.progress = 0
		self.progressbar = ttk.Progressbar(self, mode="determinate", maximum=1024, \
							length= int(GEOMETRY.split("x")[0])-self.download_button.winfo_width(), variable=self.progress)
		self.progressbar.grid(row=1, column=2, columnspan=2)

		self.custom_loop()
		pass

	def init_treeview(self):
		self.columns = ("Developer", "Game", "Setting", "Engine", "Genre", "Visual style", "Animation", "Public Build", "Graphtreon")
		columns = self.columns
		self.treeview = ttk.Treeview(self, columns = columns, show="headings", height=30)
		#self.scrollbar_y = ttk.Scrollbar(self, command=self.treeview.yview)
		#self.scrollbar_y.grid(row=0, column=1)
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
			self.treeview.column(column, width=int(GEOMETRY.split("x")[0])//len(columns), anchor = tk.CENTER)
			self.treeview.heading(column, text=column.capitalize(), command=lambda _col=column: \
									treeview_sort_column(self.treeview, _col, False))
		self.add_games_to_tree()
		self.treeview.grid(row=0, column=0, columnspan=3)
		self.treeview.tag_configure('has_update', background="red")

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

	def mark_as_downloaded(self):
		game_json = self.get_json_from_tree()
		if game_json is not None:
			self.downloaded_games[game_json["game"]] = game_json["version"]
		pass

	def add_games_to_tree(self, games=None):
		if games is None:
			for i, info in enumerate(self.json_data):
				if i != 0:
					formatted = (info["developer"], info["game"], info["setting"], info["engine"], info["genre"], \
					info["visual_style"], info["animation"], info["public_build"], info["graphtreon"])
					self.treeview.insert('', 'end', values = formatted)
		else:
			for i, info in enumerate(games):
				formatted = (info["developer"], info["game"], info["setting"], info["engine"], info["genre"], \
				info["visual_style"], info["animation"], info["public_build"], info["graphtreon"])
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

	def edit_current_game(self):
		if self.add_game_gui is None:
			data = self.get_json_from_tree()
			if data is not None:
				self.add_game_gui = AddNewGUI(master=self, editdata=data)
				self.add_game_gui.mainloop()
		pass

	def custom_loop(self):
		if self.thread is not None:
			if self.thread.is_alive:
				self.progress = self.thread.progress
		self.update_idletasks()
		self.update()
		self.after(5, self.custom_loop)
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

	def download_selected_game(self): #It would be simpler if each game had its own ID, as well as to version track later on.
		def can_download(link):
			return "mega.nz" not in link and "itch.io" not in link
		game_json = self.get_json_from_tree()
		if game_json is None:
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
		if not can_download(url):
			messagebox.showerror("Error", "NSFW Game Manager doesn't support downloading from mega or itch.io yet.")
		elif url == "-":
			messagebox.showerror("Error", "This game isn't supported by your platform yet.")
		elif url.lower() == "non-static link":
			messagebox.showerror("Error", "The link for this game is non-static.")
		elif url == "":
			messagebox.showerror("Error", "No link found in the database for this game.")
		else:
			if "has_update" in itemtags or game_json["game"] not in self.downloaded_games:
				if "has_update" in itemtags:
					self.treeview.item(item, tags=())
				if "mediafire" in url:
					api = mediafire.MediaFireApi()
					response = api.file_get_links(url.split("/")[url.split('/').index("file")+1])
					url = response['links'][0]['normal_download']
				r = requests.get(url, stream=True)
				if r.status_code == 200:
					try:
						d = r.headers['content-disposition']
						name = re.findall("filename=(.+)", d)[0]
						size = int(r.headers['content-length'])
					except KeyError:
						name = url.split("/")[-1:][0]
						size = 1024
					chunksize = size//1024
				self.thread = DownloadThread(r, chunksize, download, name)
				self.thread.daemon = True
				self.thread.start()
		self.downloaded_games[game_json["game"]] = version
		pass

	def add_new_game(self):
		if self.add_game_gui is None:
			self.add_game_gui = AddNewGUI(master=self)
			self.add_game_gui.mainloop()
		pass

	def onKeypressEvent(self, event):
		pass

	def onCtrlC(self, event):
		item = self.get_json_from_tree(True)
		if item is not None:
			pyperclip.copy("; ".join(item))
		pass

	def onCtrlD(self, event):
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

	def on_closing(self):
		config = configparser.ConfigParser()
		config["DOWNLOAD_PATH"] = {}
		config["DOWNLOAD_PATH"]["path"] = DOWNLOAD_PATH
		config["GEOMETRY"] = {}
		config["GEOMETRY"]["x"] = GEOMETRY.split("x")[0]
		config["GEOMETRY"]["y"] = GEOMETRY.split("x")[1]
		config["DOWNLOADED_GAMES"] = self.downloaded_games
		with open('config.cfg', 'w') as configfile:
			config.write(configfile)
		self.master.destroy()
	def about(self):
		message = """
		NSFW Game Manager by Dogeek
		For additional information, check out
		https://github.com/cyian-1756/nsfw_game_updater
		License : GPL-3.0
		"""
		messagebox.showinfo("About", message)
		pass
	pass


if __name__ == "__main__":
	root = tk.Tk()
	root.title("NSFW Game Manager")
	root.geometry(GEOMETRY)
	root.resizable(0,0)
	gui = GUI(root)
	gui.grid(row=0,column=0)
	gui.mainloop()
