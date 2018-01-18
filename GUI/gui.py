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

from constants import *
from options import OptionGUI
from download_thread import *
from add_new import AddNewGUI

####FOR SOME REASON self.winfo_width() returns 1 even after self.update_idletasks() FIXME
#For now, set the geometry manually
GEOMETRY = "1920x1080"

class GUI(tk.Frame): #TODO: lua mem usage filter to display in a separate widget to not clutter the text widget, add scroll bar, try to auto reload if the lua file is deleted & add a about/options menu
	def __init__(self, master=None):
		tk.Frame.__init__(self,master)
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
		self._jsonfile = open('games.json', 'r')
		self.json_data = json.loads(self._jsonfile.read())
		self.downloaded_games = DOWNLOADED_GAMES
		self.init_layout()
		pass

	def init_layout(self):
		self.menubar = tk.Menu(self)
		filemenu = tk.Menu(self)
		filemenu.add_command(label="Add New Game", command=self.add_new_game)
		self.menubar.add_cascade(label="File", menu=filemenu)
		self.menubar.add_command(label="Edit", command=self.edit_menu)
		self.menubar.add_command(label="Options", command=self.open_options)
		self.menubar.add_command(label="About", command=self.about)
		self.master.config(menu=self.menubar)

		self.init_treeview()

		self.download_button = tk.Button(self, text="Download/Update", command=self.download_selected_game)
		self.download_button.grid(row=1, column=0)
		self.progress = 0
		self.progressbar = ttk.Progressbar(self, mode="determinate", maximum=1024, \
							length= int(GEOMETRY.split("x")[0])-self.download_button.winfo_width(), variable=self.progress)
		self.progressbar.grid(row=1, column=1, columnspan=2)

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
			self.treeview.column(column, width=(int(GEOMETRY.split("x")[0])-0)//len(columns), anchor = tk.CENTER)
			self.treeview.heading(column, text=column.capitalize(), command=lambda _col=column: \
									treeview_sort_column(self.treeview, _col, False))
		self.add_games_to_tree()
		self.treeview.grid(row=0, column=0, columnspan=2)

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

	def custom_loop(self):
		global current_progress
		self.progress = current_progress
		self.update_idletasks()
		self.update()
		self.after(5, self.custom_loop)

	def download_selected_game(self): #It would be simpler if each game had its own ID, as well as to version track later on.
		def can_download(link):
			return "mediafire.com" not in link and "mega.nz" not in link and "itch.io" not in link
		item = self.treeview.item(self.treeview.focus())["values"]
		i = self.columns.index("Game")
		gamename = item[i]
		current_os = platform.system().lower()
		if current_os != '':
			for g in self.json_data:
				if g["game"] == gamename:
					url = g["download_link_{}".format(current_os)]
					version = g["latest_version"]
		if DOWNLOAD_PATH=="/" or DOWNLOAD_PATH == "":
			download = os.getcwd()+'\\'
		else:
			download = DOWNLOAD_PATH
		if not can_download(url):
			messagebox.showerror("Error", "NSFW Game Manager doesn't support downloading from mediafire, mega or itch.io yet.")
		elif url == "-":
			messagebox.showerror("Error", "This game isn't supported by your platform yet.")
		elif url.lower() == "non-static link":
			messagebox.showerror("Error", "The link for this game is non-static.")
		elif url == "":
			messagebox.showerror("Error", "No link found in the database for this game.")
		else:
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
			thread = DownloadThread(r, chunksize, download, name)
			thread.daemon = True
			thread.start()
			thread.join()
		self.downloaded_games[gamename] = version
		pass
	def add_new_game(self):
		global ADD_NEW_OPEN
		if not ADD_NEW_OPEN:
			ADD_NEW_OPEN = True
			window = AddNewGUI(master=self.master)
			window.mainloop()
		pass

	def edit_menu(self):
		pass

	def open_options(self):
		global OPTIONSOPEN
		if not OPTIONSOPEN:
			OPTIONSOPEN = True
			options = OptionGUI(master=self.master)
			options.mainloop()
		pass

	def on_closing(self):
		self._jsonfile.close()
		config = configparser.ConfigParser()
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
