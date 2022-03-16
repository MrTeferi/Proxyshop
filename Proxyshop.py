"""
PROXYSHOP - GUI LAUNCHER
"""
import os
import sys
from tkinter import *
from tkinter import ttk
import proxyshop.launcher as gui
from proxyshop.settings import cfg
import proxyshop.settings as conf
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
cwd = os.getcwd()

def render_all(selections):
	"""
	Renders all images in the art folder
	"""
	my_temps = gui.get_my_templates(selections)
	update_config()
	gui.render_all(my_temps)

def render_target(selections):
	"""
	User selects a target image to render
	"""
	my_temps = gui.get_my_templates(selections)
	update_config()
	gui.render_target(my_temps)

# Setup Kinter
root = Tk()
root.title("Proxyshop v1.0.4")
root.geometry("800x600")
root.minsize(520, 455)
root.maxsize(520, 455)

# Root frame top
f_root_t = Frame(root)
f_root_t.pack(fill=X)

# Root frame top
f_root_b = LabelFrame(root)
f_root_b.pack(fill=X, padx=6, pady=5)

# Settings frame
f_settings = LabelFrame(f_root_t, text="Settings", padx=5, pady=5)
f_settings.pack(fill=X, padx=10)

# Tabs frame
n_tabs = ttk.Notebook(f_root_b)
n_tabs.pack(fill=BOTH, expand=True)

#Settings Variables
AutoSetSymbol = BooleanVar()
AutoSymbolSize = BooleanVar()
NoReminder = BooleanVar()
NoFlavor = BooleanVar()
SaveUncompressed = BooleanVar()
ManualEdit = BooleanVar()

# Settings elements
cb_AutoSetSymbol = Checkbutton(f_settings, text="Auto Set Symbol", variable=AutoSetSymbol)
if conf.auto_symbol: cb_AutoSetSymbol.select()
cb_AutoSymbolSize = Checkbutton(f_settings, text="Auto Symbol Size", variable=AutoSymbolSize)
if conf.auto_symbol_size: cb_AutoSymbolSize.select()
cb_NoReminder = Checkbutton(f_settings, text="No Reminder Text", variable=NoReminder)
if conf.remove_reminder: cb_NoReminder.select()
cb_NoFlavor = Checkbutton(f_settings, text="No Flavor Text", variable=NoFlavor)
if conf.remove_flavor: cb_NoFlavor.select()
cb_SaveUncompressed = Checkbutton(f_settings, text="Save Uncompressed", variable=SaveUncompressed)
if conf.fast_save: cb_SaveUncompressed.select()
cb_ManualEdit = Checkbutton(f_settings, text="Manual Edit Step", variable=ManualEdit)
if conf.exit_early: cb_ManualEdit.select()

# Add settings to grid
cb_AutoSetSymbol.grid(row=0, column=0, sticky="w")
cb_AutoSymbolSize.grid(row=0, column=1, sticky="w")
cb_ManualEdit.grid(row=0, column=2, sticky="w")
cb_NoReminder.grid(row=1, column=0, sticky="w", pady=(0,5))
cb_NoFlavor.grid(row=1, column=1, sticky="w", pady=(0,5))
cb_SaveUncompressed.grid(row=1, column=2, sticky="w", pady=(0,5))

# Add tabs to grid
tabs = gui.get_tabs(n_tabs)
lb = {}
scrollbar = {}
for key, tab in tabs.items():

	# Based on tab key create list
	lb[key] = gui.get_listbox(key, tab)

	# Adding Scrollbar to the right
	scrollbar[key] = Scrollbar(tab)
	scrollbar[key].pack(side = RIGHT, fill = BOTH)

	# Add scroll cmd
	lb[key].config(yscrollcommand = scrollbar[key].set)
	scrollbar[key].config(command = lb[key].yview)
	lb[key].pack(fill=X, expand=True, padx=5, pady=5)
	lb[key].select_set(0)
	lb[key].event_generate("<<ListboxSelect>>")

# Buttons
b_RenderAll = Button(f_settings, text="Render All", width=12, command=lambda: render_all(lb))
b_RenderTarget = Button(f_settings, text="Render Target", width=12, command=lambda: render_target(lb))
b_RenderTarget.grid(row=0, column=3, sticky="nsew", padx=(6,0))
b_RenderAll.grid(row=1, column=3, sticky="nsew", pady=(0,5), padx=(6,0))

def update_config():
	"""
	Update config with chosen settings
	"""
	cfg.set("CONF", "Auto.Set.Symbol", str(AutoSetSymbol.get()))
	cfg.set("CONF", "Auto.Symbol.Size", str(AutoSymbolSize.get()))
	cfg.set("CONF", "No.Flavor.Text", str(NoFlavor.get()))
	cfg.set("CONF", "No.Reminder.Text", str(NoReminder.get()))
	cfg.set("CONF", "Fast.Saving", str(SaveUncompressed.get()))
	cfg.set("CONF", "Manual.Edit", str(ManualEdit.get()))
	with open("config.ini", "w", encoding="utf-8") as config_file:
		cfg.write(config_file)
		config_file.close()

root.mainloop()
