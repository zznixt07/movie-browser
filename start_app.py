import tkinter as tk
import os
import logging
from sql_db.sql_connector import AppDb
import platform
from imdb_functions import *
import json
# import Neutron
import configs

logging.disable(logging.INFO)

FORMAT = '%(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)


class RootWin(tk.Tk):
        
    def __init__(self):
        tk.Tk.__init__(self)
        # top level(root) window should also be configured to allow scaling
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


def randColor():
    import random
    global CLRS
    CLRS = '0123456789abcdef'
    # return CLRS.pop(0)
    c = ''
    for _ in range(6):
        c += random.choice(CLRS)
    return '#' + c
    # return configs.BGCOLOR

def removeInvalidCharInPath(p):
    splitted = p.split(os.path.sep)
    if 'windows' in platform.system().lower():
        invalids = '\\/:?*<>|"'
        for i in range(len(splitted)):
            for invalid in invalids:
                splitted[i] = splitted[i].replace(invalid, '')

    return (os.path.sep).join(splitted)

def updateSqlUsingPredefinedInfo():
    with AppDb(tblName=configs.DBTABLE) as db:
        with open('20mov.json') as f:
            db.insertAllCols(json.loads(f.read()))

def fetchFromSQL(page, minRow=1):
    with AppDb(tblName=configs.DBTABLE) as db:
        # try every session to download all top movie info
        if db.numOfRows() < minRow: return None
        return db.getPage(page=page)

def getImdb250():
    try:
        moviesLst = CustomImdb().get_top_rated()
    except Exception:
        return None

    with AppDb(tblName=configs.DBTABLE) as db:
        db.cardsDictToSql(moviesLst)
    return True


if __name__ == '__main__':
    # threading.Thread(target=paginateMovies).start()
    # cannot thread cuz gui may access PAGE1 before it consists anything
    # maybe if anything else is passed in first ShowFrame then can be threaded.

    # db should have at least 200 rows. if not try getting top250 movie from imdb
    PAGE1 = fetchFromSQL(page=1, minRow=200)
    if not PAGE1:
        # try_downloading_from_imdb
        if not getImdb250():
            # if dwnld failed update_SQLDB_with_predefined_cmd_using_offline_files
            updateSqlUsingPredefinedInfo()
        PAGE1 = fetchFromSQL(page=1)

    configs.ROOT = RootWin()
    # SCRNWDTH = configs.ROOT.winfo_screenwidth()
    # SCRNHGHT = configs.ROOT.winfo_screenheight()
    # geometry=f'{SCRNWDTH}x{SCRNHGHT-50}+0+0'

    import start_win
    configs.ShowFrame(start_win.StartWin, thisPage=PAGE1, geometry=f'{900}x{700}+500+0')
    configs.ROOT.mainloop()
    configs.SESS.close()

