import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import configs
from sql_db.sql_connector import CredsDb, AppDb


class Control(configs.CustomFrame):

    def __init__(self, *args, **kwargs):
        configs.CustomFrame.__init__(self)
        for i in range(1, 2):
            self.grid_rowconfigure(i, weight=1)
        for i in range(1):
            self.grid_columnconfigure(i, weight=1)

        headerLblFrm = configs.MyLabelFrame(self)
        headerLblFrm.grid(row=0, column=0, sticky='nsew')
        for i in range(1):
            headerLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(1):
            headerLblFrm.grid_rowconfigure(i, weight=1)
        configs.MyButton(headerLblFrm, text='Back', command=goBack).grid()

        # --------------------------- BODY ------------------------------------
        bodyLblFrm = configs.MyLabelFrame(self)
        bodyLblFrm.grid(row=1, column=0, sticky='nsew')
        for i in range(1):
            bodyLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(4):
            bodyLblFrm.grid_rowconfigure(i, weight=1)

        configs.MyButton(bodyLblFrm, text='Change Your Password', command=self.changePswd) \
                .grid(row=0, column=0, padx=20)
        configs.MyButton(bodyLblFrm, text='Remove User', command=self.rmvUsr) \
                .grid(row=1, column=0, padx=20)
        configs.MyButton(bodyLblFrm, text='Change Users Status', command=self.chngStatus) \
                .grid(row=2, column=0, padx=20)
        configs.MyButton(bodyLblFrm, text='View movies', command=self.goToMovies) \
                .grid(row=3, column=0, padx=20)

        for frm in self.winfo_children():
            for widg in frm.winfo_children():
                if widg.winfo_class() == 'Button':
                    widg.config(width=configs.BTNWIDTH+7)

    def changePswd(self):
        import password_changer
        configs.ShowFrame(password_changer.Changer)

    def rmvUsr(self):
        configs.ShowFrame(UserRemover)

    def chngStatus(self):
        configs.ShowFrame(StatusChanger)

    def goToMovies(self):
        import movie_form
        configs.ShowFrame(movie_form.MovieFormWin)


class UserRemover(configs.CustomFrame):

    def __init__(self, *args, **kwargs):
        configs.CustomFrame.__init__(self)
        for i in range(1, 2):
            self.grid_rowconfigure(i, weight=1)
        for i in range(1):
            self.grid_columnconfigure(i, weight=1)

        headerLblFrm = configs.MyLabelFrame(self)
        headerLblFrm.grid(row=0, column=0, sticky='nsew')
        for i in range(1):
            headerLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(1):
            headerLblFrm.grid_rowconfigure(i, weight=1)
        configs.MyButton(headerLblFrm, text='Back', command=goBack).grid()

        # --------------------------- BODY ------------------------------------
        bodyLblFrm = configs.MyLabelFrame(self)
        bodyLblFrm.grid(row=1, column=0, sticky='nsew')
        for i in range(1):
            bodyLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(4):
            bodyLblFrm.grid_rowconfigure(i, weight=1)

        configs.MyLabel(bodyLblFrm, text='Type username of user to remove.').grid(sticky='nsew')
        self.user = configs.MyEntry(bodyLblFrm)
        self.user.grid(sticky='ew')
        configs.MyButton(bodyLblFrm, text='Remove', command=self.removeUserFn).grid()

    def removeUserFn(self):
        with CredsDb(tblName=configs.CREDSTABLE) as db:
            if self.user.get() == configs.CURRLOGGEDIN:
                messagebox.showinfo(message='Cannot remove current user.')
            elif db.removeUser(self.user.get()):
                messagebox.showinfo(message='User Succssfully removed.')
            else:
                messagebox.showerror(message='User doesn\'t exists.')


class StatusChanger(configs.CustomFrame):

    def __init__(self, *args, **kwargs):
        configs.CustomFrame.__init__(self)
        for i in range(1, 2):
            self.grid_rowconfigure(i, weight=1)
        for i in range(1):
            self.grid_columnconfigure(i, weight=1)

        headerLblFrm = configs.MyLabelFrame(self)
        headerLblFrm.grid(row=0, column=0, sticky='nsew')
        for i in range(1):
            headerLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(1):
            headerLblFrm.grid_rowconfigure(i, weight=1)
        configs.MyButton(headerLblFrm, text='Back', command=goBack) \
                        .grid()

        # --------------------------- BODY ------------------------------------
        bodyLblFrm = configs.MyLabelFrame(self)
        bodyLblFrm.grid(row=1, column=0, sticky='nsew')
        for i in range(1):
            bodyLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(4):
            bodyLblFrm.grid_rowconfigure(i, weight=1)

        configs.MyLabel(bodyLblFrm, text='Type username of user to change to admin.').grid(sticky='nsew')
        self.user = configs.MyEntry(bodyLblFrm)
        self.user.grid(sticky='ew')
        configs.MyButton(bodyLblFrm, text='Remove', command=self.changeStatus).grid()

    def changeStatus(self):
        with CredsDb(tblName=configs.CREDSTABLE) as db:
            db.changeUserStatus(self.user.get())
            messagebox.showinfo(message='If User Exists then, Operation was successfull.')


def goBack(*args):
    # import admin_win
    # configs.ShowFrame(admin_win.AdminWin)
    configs.ShowFrame(Control)

