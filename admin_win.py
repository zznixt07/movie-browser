import tkinter as tk
from PIL import ImageTk, Image
# import os
# import threading
# import requests
import logging
# import queue
from sql_db.sql_connector import AppDb
import configs


class AdminWin(configs.CustomFrame):
    
    # page = 1

    def __init__(self, *args, **kwargs):
        configs.CustomFrame.__init__(self)
        # not scaling headerLblFrm cuz need max space for posters
        for i in range(1,2):
            self.grid_rowconfigure(i, weight=1)
        for i in range(1):
            self.grid_columnconfigure(i, weight=1)
        
        headerLblFrm = configs.MyLabelFrame(self)
        headerLblFrm.grid(row=0, column=0, sticky='nsew')
        
        for i in range(8):
            headerLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(1):
            headerLblFrm.grid_rowconfigure(i, weight=1)

        self.homeBtn = configs.MyButton(headerLblFrm, text='Home', command=self.goHome)
        self.profileLbl = configs.MyLabel(headerLblFrm, font=('Consolas', 14, 'bold'),
                                            fg='#000', bg='#fff', wraplength=100)
        
        self.homeBtn.grid(row=0, column=0)
        if configs.CURRLOGGEDIN:
            self.profileLbl.config(text=configs.CURRLOGGEDIN)
            self.profileLbl.grid(row=0, column=7, sticky='e')

        bodyLblFrm = configs.MyLabelFrame(self)
        bodyLblFrm.grid(row=1, column=0, sticky='nsew')
        for i in range(3):
            bodyLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(1):
            bodyLblFrm.grid_rowconfigure(i, weight=1)

        configs.MyButton(bodyLblFrm, text='Login', command=self.adminLogin) \
                        .grid(row=0, column=0)
        if configs.ISADMIN:
            configs.MyButton(bodyLblFrm, text='Admin Panel', command=self.adminPanel) \
                            .grid(row=0, column=1)
        configs.MyButton(bodyLblFrm, text='Sign Up', command=self.adminSignUp) \
                        .grid(row=0, column=2)


    def clearSearch(self, *args):
        logging.debug('clked on Search', self.searchBar.get())
        # seems no way to select the current contents
        self.searchBar.delete(0, tk.END)

    def displaySearchResults(self, *args):
        pass

    def goHome(self):
        logging.debug('Home Btn pressed')
        # using class varaible, the page numbers are remembered and can be resumed
        import start_win
        with AppDb(tblName=configs.DBTABLE) as db:
            homePage = db.getPage(page=start_win.StartWin.page)
        configs.ShowFrame(start_win.StartWin, thisPage=homePage)

    def adminLogin(self):
        import admin_activity
        configs.ShowFrame(admin_activity.AdminLogin)

    def adminSignUp(self):
        import user_activity
        configs.ShowFrame(user_activity.UserSignup, admin=True)

    def adminPanel(self):
        import admin_control
        configs.ShowFrame(admin_control.Control)

