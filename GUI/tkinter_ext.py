import tkinter as tk

class EntryWithPlaceholder(tk.Entry):
	def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', **kwargs):
		super().__init__(master, **kwargs)

		self.placeholder = placeholder
		self.placeholder_color = color
		self.default_fg_color = self['fg']

		self.bind("<FocusIn>", self.foc_in)
		self.bind("<FocusOut>", self.foc_out)

		self.put_placeholder()

	def put_placeholder(self):
		self.insert(0, self.placeholder)
		self['fg'] = self.placeholder_color

	def foc_in(self, *args):
		if self['fg'] == self.placeholder_color:
			self.delete('0', 'end')
			self['fg'] = self.default_fg_color

	def foc_out(self, *args):
		if not self.get():
			self.put_placeholder()

try:
	from Tkinter import PhotoImage, Frame, Label, Widget
	from Tkconstants import *
except ImportError:
	from tkinter import PhotoImage, Frame, Label, Widget
	from tkinter.constants import *

class CollapsibleFrame(Frame):
	def __init__(self, master, text=None, borderwidth=2, width=0, height=16, interior_padx=0, interior_pady=8, background=None, caption_separation=4, caption_font=None, caption_builder=None, icon_x=5):
		Frame.__init__(self, master)
		if background is None:
			background = self.cget("background")

		self.configure(background=background)

		self._is_opened = False

		self._interior_padx = interior_padx
		self._interior_pady = interior_pady

		self._iconOpen = PhotoImage(data="R0lGODlhEAAQAKIAAP///9TQyICAgEBAQAAAAAAAAAAAAAAAACwAAAAAEAAQAAADNhi63BMgyinFAy0HC3Xj2EJoIEOM32WeaSeeqFK+say+2azUi+5ttx/QJeQIjshkcsBsOp/MBAA7")
		self._iconClose = PhotoImage(data="R0lGODlhEAAQAKIAAP///9TQyICAgEBAQAAAAAAAAAAAAAAAACwAAAAAEAAQAAADMxi63BMgyinFAy0HC3XjmLeA4ngpRKoSZoeuDLmo38mwtVvKu93rIo5gSCwWB8ikcolMAAA7")

		height_of_icon = max(self._iconOpen.height(), self._iconClose.height())
		width_of_icon = max(self._iconOpen.width(), self._iconClose.width())

		containerFrame_pady = (height_of_icon//2) +1

		self._height = height
		self._width = width

		self._containerFrame = Frame(self, borderwidth=borderwidth, width=width, height=height, relief=RIDGE, background=background)
		self._containerFrame.pack(expand=True, fill=X, pady=(containerFrame_pady,0))

		self.interior = Frame(self._containerFrame, background=background)

		self._collapseButton = Label(self, borderwidth=0, image=self._iconOpen, relief=RAISED)
		self._collapseButton.place(in_= self._containerFrame, x=icon_x, y=-(height_of_icon//2), anchor=N+W, bordermode="ignore")
		self._collapseButton.bind("<Button-1>", lambda event: self.toggle())

		if caption_builder is None:
			self._captionLabel = Label(self, anchor=W, borderwidth=1, text=text)
			if caption_font is not None:
				self._captionLabel.configure(font=caption_font)
		else:
			self._captionLabel = caption_builder(self)

			if not isinstance(self._captionLabel, Widget):
				raise Exception("'caption_builder' doesn't return a tkinter widget")

		self.after(0, lambda: self._place_caption(caption_separation, icon_x, width_of_icon))

	def update_width(self, width=None):
		# Update could be devil
		# http://wiki.tcl.tk/1255
		self.after(0, lambda width=width:self._update_width(width))

	def _place_caption(self, caption_separation, icon_x, width_of_icon):
		self.update()
		x = caption_separation + icon_x + width_of_icon
		y = -(self._captionLabel.winfo_reqheight()//2)

		self._captionLabel.place(in_= self._containerFrame, x=x, y=y, anchor=N+W, bordermode="ignore")

	def _update_width(self, width):
		self.update()
		if width is None:
			width=self.interior.winfo_reqwidth()

		if isinstance(self._interior_pady, (list, tuple)):
			width += self._interior_pady[0] + self._interior_pady[1]
		else:
			width += 2*self._interior_pady

		width = max(self._width, width)

		self._containerFrame.configure(width=width)

	def open(self):
		self._collapseButton.configure(image=self._iconClose)

		self._containerFrame.configure(height=self.interior.winfo_reqheight())
		self.interior.pack(expand=True, fill=X, padx=self._interior_padx, pady =self._interior_pady)

		self._is_opened = True

	def close(self):
		self.interior.pack_forget()
		self._containerFrame.configure(height=self._height)
		self._collapseButton.configure(image=self._iconOpen)

		self._is_opened = False

	def toggle(self):
		if self._is_opened:
			self.close()
		else:
			self.open()

if __name__ == "__main__":
	try:
		from Tkinter import Tk, Button
	except ImportError:
		from tkinter import Tk, Button

	root = Tk()
	root.wm_geometry("400x300+0+0")

	cf1 = CollapsibleFrame(root, text ="Frame1", interior_padx=6)
	cf1.pack()

	for i in range(3):
		Button(cf1.interior, text="button %s"%i).grid(row=i, column=0)

	cf1.update_width()
	root.mainloop()
