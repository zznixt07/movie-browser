import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import configs
from sql_db.sql_connector import CredsDb, AppDb


class Changer(configs.CustomFrame):
    errorsLst = []

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
        configs.MyButton(headerLblFrm, text='Back', command=self.goBack) \
                        .grid()

        bodyLblFrm = configs.MyLabelFrame(self)
        bodyLblFrm.grid(row=1, column=0, sticky='nsew')
        for i in range(2):
            bodyLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(4):
            bodyLblFrm.grid_rowconfigure(i, weight=1)

        self.entDict = {}
        self.entries = ('Old Password', 'New Password', 'Confirm New Password')
        for row, lbl in enumerate(self.entries):
            configs.MyLabel(bodyLblFrm, text=lbl).grid(row=row, column=0, sticky='e')

        for row, ent in enumerate(self.entries):
            if row == 0:
                self.entDict[ent] = configs.MyEntry(bodyLblFrm)
            else:
                self.entDict[ent] = configs.MyEntry(bodyLblFrm, show='*')
            self.entDict[ent].grid(row=row, column=1, sticky='w', padx=10)

        self.pswdVar = tk.IntVar()
        configs.MyCheckButton(bodyLblFrm, text='Show', variable=self.pswdVar,
                                command=self.showHidePswd).grid(row=1, column=2, sticky='w')
        self.errVar = tk.StringVar()
        self.errLbl = configs.MyLabel(bodyLblFrm, fg='red', textvariable=self.errVar, wraplength=450)

        bottomLblFrm = configs.MyLabelFrame(self, text='', bd='2')
        bottomLblFrm.grid(row=2, column=0, sticky='nsew', pady=20)
        for i in range(2):
            bottomLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(1):
            bottomLblFrm.grid_rowconfigure(i, weight=1)

        configs.MyButton(bottomLblFrm, text="Done", command=self.done) \
                .grid(row=0, column=0, sticky='e', padx=30)
        configs.MyButton(bottomLblFrm, text="Clear", command=self.clearAllEnt) \
                .grid(row=0, column=1, sticky='w', padx=30)

    def goBack(self):
        import admin_control
        configs.ShowFrame(admin_control.Control)

    def done(self):
        self.errorsLst = []
        if not self.matchPswd():
            self.showErr('\n'.join(self.errorsLst))
            return

        messagebox.showinfo(message='Password changed successful!')

        with CredsDb(tblName=configs.CREDSTABLE) as db:
            db.changePswd(username=configs.CURRLOGGEDIN,
                            oldPswd=self.entDict['Old Password'].get(),
                            newPswd=self.entDict['New Password'].get())
        configs.ISADMIN = False
        configs.CURRLOGGEDIN = ''
        self.goHome()

    def goHome(self):
        import start_win
        with AppDb(tblName=configs.DBTABLE) as db:
            homePage = db.getPage(page=start_win.StartWin.page)
        configs.ShowFrame(start_win.StartWin, thisPage=homePage)

    def matchPswd(self, ps=None, cnf=None):
        o = self.entDict['Old Password'].get()
        with CredsDb(tblName=configs.CREDSTABLE) as db:
            userInfo = db.returnPersonInfo(configs.CURRLOGGEDIN, o)
            if not userInfo:
                self.errorsLst.append('Old Password does not match.')
                return False
        p = self.entDict['New Password'].get()
        if len(p) < 8:
            self.errorsLst.append('Password must be greater than 8 characters long.')
            return False
        c = self.entDict['Confirm New Password'].get()
        if p != c:
            self.errorsLst.append('Password do not match')
            return False
        if p == o:
            self.errorsLst.append('New password cannot be same as old password')
            return False

        return True

    def showHidePswd(self):
        if self.pswdVar.get():
            self.entDict['New Password'].config(show='')
            self.entDict['Confirm New Password'].config(show='')
        else:
            self.entDict['New Password'].config(show='*')
            self.entDict['Confirm New Password'].config(show='*')

    def clearAllEnt(self, *args):
        for ent in self.entries:
            self.entDict[ent].delete(0, tk.END)
        self.pswdVar.set(0)

    def showErr(self, msg):
        if isinstance(msg, list):
            msg = '\n'.join(msg)
        self.errVar.set(msg)
        # print(self.errLbl.grid_info())
        self.errLbl.grid(columnspan=3, sticky='ew', padx=20)
        try:
            # if a timeout exists, cancel it/ restart it
            configs.ROOT.after_cancel(self.intervalId)
        except AttributeError:
            pass
        # ungrid error label after 5000ms
        self.intervalId = configs.ROOT.after(5000, lambda: self.errLbl.grid_forget())

        return True