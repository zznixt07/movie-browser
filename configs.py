import os
import queue
import requests
import tkinter as tk

# BGCOLOR = "#5A4D77" # purpleish
# FGCOLOR = "#DBDBDB"
BGCOLOR = "#101010"
FGCOLOR = "#FFFFFF"
ENTBGCOLOR = '#575757'
CARETFGCOLOR = '#ffffff'
SEARCHBGCOLOR = '#171717'
BTNBGCOLOR = "#373737"
BTNFGCOLOR = "white"
BTNWIDTH = 15
BTNHEIGHT = 1
# FNTFAMILY = 'Helvetica'
FNTFAMILY = 'Consolas'
# FNTFAMILY = 'Roboto'
FNTSIZE = 10

CURRDIR = os.path.dirname(__file__)
DBTABLE = 'imdb250'
USERDBTABLE = 'user_added_movs'
CREDSTABLE = 'creds_user_and_admin'
CURRLOGGEDIN = ''
ISADMIN = False
USERMOVPK = 100000000
IMAGESQUEUE = queue.Queue()
ROOT = None
SEARCHBY = ['title', 'rating', 'genres', 'year', 'cast', 'directors']
GRIDLAYOUT = []
NOFROWS, NOFCOLS = 2, 5
for row in range(0, NOFROWS):
    for col in range(1, NOFCOLS+1):
        GRIDLAYOUT.append(f'{row}{col}')

SESS = requests.Session()
# sizes = {'small': 80/h, 'medium': 160/h, 'large': 268/h}

class ShowFrame:

    def __init__(self, className, *args, title=None, geometry=None, **kwargs):
        if not ROOT:
            raise NotImplementedError
        # size of window remains same unless explicitly stated in each class
        if geometry:
            ROOT.geometry(geometry)
        if title:
            ROOT.title(title)
        thisFrame = className(*args, **kwargs)
        thisFrame.grid(row=0, column=0, sticky='nsew')
        thisFrame.lift()


class CustomFrame(tk.Frame):

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, master=ROOT, bg=BGCOLOR,
                            relief='sunken', padx=5, pady=0)
        # keep this seperate otherwise multiple kwargs error.
        self.configure(**kwargs)


class MyLabelFrame(tk.LabelFrame):

    def __init__(self, *args, **kwargs):
        tk.LabelFrame.__init__(self, *args, labelanchor='s', borderwidth=0,
                                bg=BGCOLOR, fg=FGCOLOR, pady=3, padx=10)
        self.config(**kwargs)
        self.config(text='')  # can control anchor-text during development
        self.config(borderwidth=4)  # can control border during development

'''with attrs in each class, the modules can overwrite these values.
But to return to default the module should set attrs to their starting value
    MyLabel.fnt = MyEntry.fnt = MyButton.fnt = FNT
    MyEntry.bg = '#515151'
    MyEntry.fg = '#ffffff'

    MyLabel.fnt = MyEntry.fnt = MyButton.fnt = MyEntry.bg = MyEntry.fg = None
'''


class MyButton(tk.Button):
    fnt = bg = fg = None

    def __init__(self, *args, **kwargs):
        tk.Button.__init__(self, *args, bg=self.bg or BTNBGCOLOR, fg=self.fg or BTNFGCOLOR,
                            relief='solid', width=BTNWIDTH, height=BTNHEIGHT,
                            font=self.fnt or (FNTFAMILY, FNTSIZE+1, 'bold'))
        self.config(**kwargs)


class MyEntry(tk.Entry):
    fnt = bg = fg = None

    def __init__(self, *args, **kwargs):
        tk.Entry.__init__(self, *args, bg=self.bg or ENTBGCOLOR, fg=self.fg or FGCOLOR,
                            relief='flat', insertbackground=CARETFGCOLOR,
                            font=self.fnt or (FNTFAMILY, FNTSIZE, 'bold'))
        self.config(**kwargs)


class MyLabel(tk.Label):
    fnt = bg = fg = None

    def __init__(self, *args, **kwargs):
        tk.Label.__init__(self, *args, bg=self.bg or BGCOLOR, fg=self.fg or FGCOLOR,
                            font=self.fnt or (FNTFAMILY, FNTSIZE, 'bold'),
                            justify=tk.LEFT)
        self.config(**kwargs)


class MyOptionMenu(tk.OptionMenu):
    
    def __init__(self, *args, **kwargs):
        tk.OptionMenu.__init__(self, *args)
        self.config(bg=BGCOLOR, fg=FGCOLOR, font=(FNTFAMILY, FNTSIZE), bd=0,
                    activebackground=BGCOLOR, activeforeground=FGCOLOR, width=6,
                    relief='flat')
        self.config(**kwargs)


class MyCheckButton(tk.Checkbutton):

    def __init__(self, *args, **kwargs):
        tk.Checkbutton.__init__(self, *args, bg=BGCOLOR, fg=FGCOLOR,
                                selectcolor='#101010', activebackground=BGCOLOR,
                                activeforeground=FGCOLOR)
        self.config(**kwargs)


class Rememberer:

    def __init__(self):
        import shelve

    def storeLoggedIn(self, username):
        with shelve.open('logged') as f:
            f['cred'] = username

    def getLoggedIn(self):
        with shelve.open('logged') as f:
            return f.get('cred')

def changeToStr(d, convFalsyTo=''):
    '''mainly used for tkinter labels. dosen't convert int and floats.'''
    strsDict = {}
    for k, v in d.items():
        if v is None:
            strsDict[k] = convFalsyTo
        elif isinstance(v, list):
            strsDict[k] = ', '.join(v) or convFalsyTo # if both falsy, OR chooses latter
        else:
            strsDict[k] = v

    return strsDict