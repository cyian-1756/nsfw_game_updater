#-*- encoding:utf8 -*-
#!/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import time
import configparser
import json
import wget
import platform

from constants import *

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
		print(self.master.winfo_width(), self.winfo_width())
		self.init_layout()
		pass

	def init_layout(self):
		self.menubar = tk.Menu(self)
		self.menubar.add_command(label="File", command=self.file_menu)
		self.menubar.add_command(label="Edit", command=self.edit_menu)
		self.menubar.add_command(label="Options", command=self.open_options)
		self.menubar.add_command(label="About", command=self.about)
		self.master.config(menu=self.menubar)

		self.frame_viewer = tk.Frame(self.master, height=550)
		self.frame_viewer.pack(side=tk.TOP)

		self.init_treeview()
		self.custom_loop()
		#self.custom_loop()
		self.frame_buttons = tk.Frame(self.master, height=50)
		self.frame_buttons.pack(side=tk.BOTTOM)

		self.download_button = tk.Button(self.frame_buttons, text="Download/Update", command=self.download_selected_game)
		self.download_button.pack(side=tk.LEFT)
		self.progress = 0
		self.progressbar = ttk.Progressbar(self.frame_buttons, mode="determinate", \
							length= int(GEOMETRY.split("x")[0])-self.download_button.winfo_width(), variable=self.progress)
		self.progressbar.pack()
		pass

	def init_treeview(self):
		self.columns = ("Developer", "Game", "Setting", "Engine", "Genre", "Visual style", "Animation", "Public Build", "Graphtreon")
		columns = self.columns
		self.treeview = ttk.Treeview(self.frame_viewer, columns = columns, show="headings")
		self.scrollbar_y = ttk.Scrollbar(self.frame_viewer, command=self.treeview.yview)
		self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
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
			self.treeview.column(column, width=(int(GEOMETRY.split("x")[0])-self.scrollbar_y.winfo_width())//len(columns), anchor = tk.CENTER)
			self.treeview.heading(column, text=column.capitalize(), command=lambda _col=column: \
									treeview_sort_column(self.treeview, _col, False))
		self.add_games_to_tree()
		self.treeview.pack(side=tk.LEFT, fill=tk.Y)

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
		self.update_idletasks()
		self.update()
		self.after(5, self.custom_loop)

	def download_selected_game(self): #It would be simpler if each game had its own ID, as well as to version track later on.
		item = self.treeview.item(self.treeview.focus())["values"]
		i = self.columns.index("Game")
		gamename = item[i]
		current_os = platform.system().lower()
		if current_os != '':
			for g in self.json_data:
				if g["game"] == gamename:
					url = g[f"download_link_{current_os}"]
		wget.download(url) #TODO : get progress to show in the progressbar, get folder selection to save file at the right place.
		pass
	def file_menu():
		pass

	def edit_menu():
		pass

	def on_closing(self):
		self._jsonfile.close()
		config = configparser.ConfigParser()
		config["GEOMETRY"] = {}
		config["GEOMETRY"]["x"] = GEOMETRY.split("x")[0]
		config["GEOMETRY"]["y"] = GEOMETRY.split("x")[1]
		with open('config.cfg', 'w') as configfile:
			config.write(configfile)
		self.master.destroy()
	def about(self):
		message = """
		NSFW Game Manager by Dogeek\n
		For additional information, check out\n
		https://github.com/cyian-1756/nsfw_game_updater\n
		License : GPL-3.0
		"""
		messagebox.showinfo("About", message)
		pass

	def open_options(self):
		pass
	pass


if __name__ == "__main__":
	root = tk.Tk()
	root.title("NSFW Game Manager")
	root.geometry(GEOMETRY)
	gui = GUI(root)
	gui.pack()
	gui.mainloop()
