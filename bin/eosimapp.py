import tkinter as tk
from eosim.gui.mainapplication import MainApplication
import argparse
import logging

def main(loglevel): 
    root = tk.Tk()
    root.resizable(False, False)
    MainApplication(root, loglevel)
    root.mainloop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Earth Observation Simulator (EOSim)'
    )
    parser.add_argument(
        '-loglevel',
        default="INFO",
        type=str,
        help="Logging level: Specifiy CRITICAL or ERROR or WARNING or INFO or DEBUG."
    )   

    args = parser.parse_args()
    if(args.loglevel=='CRITICAL'):
        loglevel = logging.CRITICAL
    elif(args.loglevel=='ERROR'):
        loglevel = logging.ERROR
    elif(args.loglevel=='WARNING'):
        loglevel = logging.WARNING
    elif(args.loglevel=='INFO'):
        loglevel = logging.INFO
    elif(args.loglevel=='DEBUG'):
        loglevel = logging.DEBUG

    main(loglevel)
