#-*- encoding:utf8 -*-
#!/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import time
import configparser
import json


class GUI(tk.Frame): #TODO: lua mem usage filter to display in a separate widget to not clutter the text widget, add scroll bar, try to auto reload if the lua file is deleted & add a about/options menu
	def __init__(self, master=None):
		tk.Frame.__init__(self,master)
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
		self._jsonfile = open('games.json', 'r')
		self.json_data = json.loads(self._jsonfile.read())
		self.init_layout()
		pass

	def init_layout(self):
		self.menubar = tk.Menu(self)
		self.menubar.add_command(label="File", command=self.file_menu)
		self.menubar.add_command(label="Edit", command=self.edit_menu)
		self.menubar.add_command(label="Options", command=self.open_options)
		self.menubar.add_command(label="About", command=self.about)
		self.master.config(menu=self.menubar)

		columns = ("Developer", "Game", "Setting", "Engine", "Genre", "Visual style", "Animation", "Public Build", "Graphtreon")
		self.treeview = ttk.Treeview(self.master, columns = columns)
		self.treeview["show"]="headings"
		for column in columns:
			self.treeview.column(column, width=1920//len(columns), anchor = tk.CENTER)
			self.treeview.heading(column, text=column.capitalize())
		self.treeview.pack()
		self.add_games_to_tree()

		self.custom_loop()
		pass

	def add_games_to_tree(self):
		for i, info in enumerate(self.json_data):
			if i != 0:
				formatted = (info["developer"], info["game"], info["setting"], info["engine"], info["genre"], \
				info["visual_style"], info["animation"], info["public_build"], info["graphtreon"])
				self.treeview.insert('', 'end', values = formatted)
		pass

	def custom_loop(self):
		print(self.winfo_width())
		columns = ("Developer", "Game", "Setting", "Engine", "Genre", "Visual style", "Animation", "Public Build", "Graphtreon")
		self.master.update_idletasks()
		self.after(5, self.custom_loop)

	def file_menu():
		pass

	def edit_menu():
		pass

	def on_closing(self):
		self._jsonfile.close()
		config = configparser.ConfigParser()
		config["GEOMETRY"] = {}
		config["GEOMETRY"]["x"] = str(self.winfo_height())
		config["GEOMETRY"]["y"] = str(self.winfo_width())
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
	root.geometry("1920x1080")#root.geometry(GEOMETRY)
	gui = GUI(root)
	gui.pack()
	root.update_idletasks()
	gui.mainloop()
