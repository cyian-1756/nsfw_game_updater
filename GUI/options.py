#-*- encoding:utf8 -*-
#!/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory
from constants import *

class OptionGUI(tk.Toplevel):
	def __init__(self, master = None):
		super(OptionGUI, self).__init__()
		self.master = master
		self.title = "Options"
		self.resolution_var = tk.StringVar()
		self.resolution_var.set(GEOMETRY)
		self.filepath_var = tk.StringVar()
		self.filepath_var.set(DOWNLOAD_PATH)
		self.advanced_view_var = tk.IntVar()
		self.advanced_view_var.set(int(ADVANCED_VIEW))
		self.config()
		pass

	def config(self):
		resolutions = ('800x600', '1024x768', '1280x960', '1280x720', '1600x900', '1920x1080', '1366x768')
		self.combo_resolution = ttk.Combobox(self, textvariable = self.resolution_var, state='readonly', values=resolutions)
		self.combo_resolution.grid(column=1, row=0, columnspan=2)
		tk.Label(self, text="Resolution :").grid(row=0, column=0)

		self.filepath_entry = tk.Entry(self, textvariable=self.filepath_var)
		self.filepath_entry.grid(column=1, row=1)
		folderimg = tk.BitmapImage(data=FOLDER_ICON.split('-')[0], maskdata=FOLDER_ICON.split('-')[1], background="white")
		self.filepath_button = tk.Button(self, command=self.onFilepathButton, image=folderimg, width=16, height=16)
		self.filepath_button.image = folderimg
		self.filepath_button.grid(row=1, column=2)
		tk.Label(self, text="Download Path :").grid(row=1, column=0)
		tk.Checkbutton(self, variable=self.advanced_view_var).grid(row=2, column=1, columnspan=2)
		tk.Label(self, text="Advanced View :").grid(row=2, column=0)
		self.ok_button = tk.Button(self, text="Save", command=self.onOkButton)
		self.cancel_button = tk.Button(self, text="Cancel", command=self.onCancelButton)
		self.ok_button.grid(column=0, row=6)
		self.cancel_button.grid(column=1, row=6)
		self.loopCheck()
		pass

	def onFilepathButton(self):
		directory = askdirectory()
		self.filepath_var.set(directory)
		pass

	def onOkButton(self):
		global GEOMETRY
		global DOWNLOAD_PATH
		global ADVANCED_VIEW
		GEOMETRY = self.resolution_var.get()
		DOWNLOAD_PATH = self.filepath_var.get()
		ADVANCED_VIEW = bool(self.advanced_view_var.get())

		self.master.treeview.destroy()
		self.master.init_treeview()
		self.master.master.geometry(self.resolution_var.get())
		for column in self.master.columns:
			self.master.treeview.column(column, width=int(GEOMETRY.split("x")[0])//len(self.master.columns), anchor = tk.CENTER)
		self.onCancelButton()
	def onCancelButton(self):
		self.master.options_gui = None
		self.destroy()

	def loopCheck(self):
		self.after(20, self.loopCheck)
		pass
	pass