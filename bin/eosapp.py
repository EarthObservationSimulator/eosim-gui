import tkinter as tk
from eos.gui.mainapplication import MainApplication
import os

def main(): 
    root = tk.Tk()
    root.resizable(False, False)
    MainApplication(root)
    root.mainloop()
    

if __name__ == '__main__':
    main()
