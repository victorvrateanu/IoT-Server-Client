import tkinter as tk

def buton_inactiv(button):
    button.config(state=tk.DISABLED)

def buton_activ(button):
    button.config(state=tk.NORMAL)