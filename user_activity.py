import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import os
import logging
from sql_db.sql_connector import AppDb, CredsDb
from configs import *

BG = '#171717'
FG = '#ffffff'
FNT = (FNTFAMILY, FNTSIZE+3, 'bold')
CUSTATTRS = ['Button', 'Label', 'Checkbutton', 'Entry']


class UserSignup(CustomFrame):
    
    # page = 1
    errorsLst = []

    def __init__(self, *args, **kwargs):
        if kwargs:
            self.makeAdmin = kwargs['admin']
            logging.debug('SIGNUP process for ADMIN')
        else:
            self.makeAdmin = False
        CustomFrame.__init__(self)
        for i in range(1, 2):
            self.grid_rowconfigure(i, weight=1)
        for i in range(1):
            self.grid_columnconfigure(i, weight=1)

        headerLblFrm = MyLabelFrame(self, text='', bd='2')
        headerLblFrm.grid(row=0, column=0, sticky='nsew')
        # for i in range(1):
        #     headerLblFrm.grid_columnconfigure(i, weight=1)
        # for i in range(1):
        #     headerLblFrm.grid_rowconfigure(i, weight=1)
        MyButton(headerLblFrm, text='Back', command=lambda: self.lower()) \
                .grid(padx=10, pady=20)


        bodyLblFrm = MyLabelFrame(self, text='', bd='2')
        bodyLblFrm.grid(row=1, column=0, sticky='nsew')
        for i in range(9):
            bodyLblFrm.grid_rowconfigure(i, weight=1)
        for i in range(3):
            bodyLblFrm.grid_columnconfigure(i, weight=1)

        # BACKGROUND IMAGE
        imgLbl = MyLabel(bodyLblFrm)
        # 1397x568 = 2.45 # final fullscreen
        tkImg = ImageTk.PhotoImage(image=Image.open(os.path.join(CURRDIR, 'perspectives', 'perspective1.jpg')))
        imgLbl.config(image=tkImg)
        imgLbl.image = tkImg
        imgLbl.place(x=0, y=0, relwidth=1, relheight=1, bordermode="outside")

        MyLabel(bodyLblFrm, text='Field marked with * are compulsory') \
                .grid(row=0, column=0, columnspan=3, sticky='ew', padx=2, pady=5)
        
        self.genderVar = tk.StringVar()
        vcmd = (self.register(self.onValidate), '%P')
        vcmdCnfrm = (self.register(self.onValidateCnfrm), '%P')

        # self.genList = ['Male', 'Female', 'Other']
        self.entries = ('Username*', 'First Name', 'Last Name', 'Email')
        self.entDict = {}

        for row, txt in enumerate(self.entries
                                + ('Password*', 'Confirm Password*', 'Gender'), start=1):
            MyLabel(bodyLblFrm, text=txt).grid(row=row, column=0, sticky='e', padx=2, pady=5)

        for row, entry in enumerate(self.entries, start=1):
            entry = entry.lower().replace(' ', '_')
            self.entDict[entry] = MyEntry(bodyLblFrm)
            self.entDict[entry].grid(row=row, column=1, sticky='ew', padx=8)
            lastrow = row

        self.pswdEnt = MyEntry(bodyLblFrm, show='*', validate="all", validatecommand=vcmd)
        self.showPswd = MyCheckButton(bodyLblFrm, text='Show',
                                        variable=self.pswdVar,
                                        command=self.showHidePswd)
        self.cnfrmPswdEnt = MyEntry(bodyLblFrm, show="*", validate="all", validatecommand=vcmdCnfrm)
        self.genBox = tk.OptionMenu(bodyLblFrm, self.genderVar, *['Male', 'Female', 'Other'])
        self.pswdVar = tk.IntVar()
        self.genBox.config(bg=BGCOLOR, fg=FGCOLOR, font=(FNTFAMILY, FNTSIZE),
                            activebackground=BGCOLOR, activeforeground=FGCOLOR,
                            width=6, relief='flat')
    
        self.pswdEnt.grid(row=lastrow+1, column=1, sticky='ew', padx=8)
        self.showPswd.grid(row=lastrow+1, column=2, sticky='w', padx=8)
        self.cnfrmPswdEnt.grid(row=lastrow+2, column=1, sticky='ew', padx=8)
        self.genBox.grid(row=lastrow+3, column=1, padx=8, sticky="w")
        self.errVar = tk.StringVar()
        self.errLbl = MyLabel(bodyLblFrm, fg='red', textvariable=self.errVar, wraplength=450)
        # self.errLbl.grid(row=lastrow+5, column=0, columnspan=3, padx=8, sticky="ew")

        bottomLblFrm = MyLabelFrame(self, text='', bd='2')
        bottomLblFrm.grid(row=2, column=0, sticky='nsew', pady=20)
        for i in range(2):
            bottomLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(1):
            bottomLblFrm.grid_rowconfigure(i, weight=1)

        MyButton(bottomLblFrm, text="Done", command=self.done) \
                .grid(row=0, column=0, sticky='e', padx=30)
        MyButton(bottomLblFrm, text="Clear", command=self.clearAllEnt) \
                .grid(row=0, column=1, sticky='w', padx=30)

        for frm in self.winfo_children():
            for widg in frm.winfo_children():
                if widg.winfo_class() in CUSTATTRS:
                    widg.config(bg=BG, fg=FG, font=FNT)

    def showErr(self, msg):
        if isinstance(msg, list):
            msg = '\n'.join(msg)
        self.errVar.set(msg)
        # print(self.errLbl.grid_info())
        self.errLbl.grid(columnspan=3, sticky='ew', padx=20)
        try:
            # if a timeout exists, cancel it/ restart it
            ROOT.after_cancel(self.intervalId)
        except AttributeError:
            pass
        # ungrid error label after 5000ms
        self.intervalId = ROOT.after(5000, lambda: self.errLbl.grid_forget())

        return True

    def onValidateCnfrm(self, currCnfrmEnt):
        return self.onValidate(currCnfrmEnt=currCnfrmEnt)

    def onValidate(self, currEnt=None, currCnfrmEnt=None):
        '''only %P can give current Password val. distinction between pass and
        confirm pass is required so that func need not be repeated. see matchPswd()
        for more.'''
        self.errorsLst = []
        self.isUsrnameEmpty()
        self.matchPswd(ps=currEnt, cnf=currCnfrmEnt)
        # always return True. no restriction while typing.
        if self.errorsLst:
            self.showErr(self.errorsLst)
            return True
        else:
            self.errLbl.grid_remove()
            return True

    def showHidePswd(self):
        if self.pswdVar.get():
            self.pswdEnt.config(show='')
            self.cnfrmPswdEnt.config(show='')
        else:
            self.pswdEnt.config(show='*')
            self.cnfrmPswdEnt.config(show='*')

    def isUsrnameEmpty(self):
        if self.entDict['username*'].get() != '':
            return False
        else:
            self.errorsLst.append('Username cannot be empty')
            return True

    def goHome(self):
        import start_win
        with AppDb(tblName=DBTABLE) as db:
            homePage = db.getPage(page=start_win.StartWin.page)
        ShowFrame(start_win.StartWin, thisPage=homePage)

    def matchPswd(self, ps=None, cnf=None):
        p = ps or self.pswdEnt.get()
        c = cnf or self.cnfrmPswdEnt.get()
        if len(p) < 8:
            self.errorsLst.append('Password must be greater than 8 characters long.')
            return False
        if p != c:
            self.errorsLst.append('Password do not match')
            return False
        return True

    def clearAllEnt(self, *args):
        for ent in self.entries:
            ent = self.entDict[ent.lower().replace(' ', '_')]
            ent.delete(0, tk.END)
        self.pswdEnt.delete(0, tk.END)
        self.cnfrmPswdEnt.delete(0, tk.END)
        self.genderVar.set('')
        self.pswdVar.set(0)

    def done(self, *args):
        self.onValidate()       # this sets the below variable
        if self.errorsLst: return
        with CredsDb(tblName=CREDSTABLE) as db:
            if db.user_exists(self.entDict['username*'].get()):
                self.showErr('You are already registered!')
                return
            db.signupPerson({
                    'isAdmin': 1 if self.makeAdmin else 0,
                    'username': self.entDict['username*'].get(),
                    'firstName': self.entDict['first_name'].get(),
                    'lastName': self.entDict['last_name'].get(),
                    'email': self.entDict['email'].get(),
                    'pswd': self.pswdEnt.get(),
                    'gender': self.genderVar.get(),
            })
            self.showErr('Registered Successfully!')
        

class UserLogin(CustomFrame):
    errorsLst = []

    def __init__(self, *args, **kwargs):

        CustomFrame.__init__(self)
        for i in range(1, 2):
            self.grid_rowconfigure(i, weight=1)
        for i in range(1):
            self.grid_columnconfigure(i, weight=1)

        headerLblFrm = MyLabelFrame(self, text='', bd='2')
        headerLblFrm.grid(row=0, column=0, sticky='nsew')
        # for i in range(1):
        #     headerLblFrm.grid_columnconfigure(i, weight=1)
        # for i in range(1):
        #     headerLblFrm.grid_rowconfigure(i, weight=1)
        MyButton(headerLblFrm, text='Back', command=self.goBack) \
                .grid(padx=10, pady=20)

        bodyLblFrm = MyLabelFrame(self, text='', bd=2)
        bodyLblFrm.grid(row=1, column=0, sticky='nsew')
        
        # BACKGROUND IMAGE
        imgLbl = MyLabel(bodyLblFrm)
        # 1397x568 = 2.45 # final on fullscreen
        tkImg = ImageTk.PhotoImage(image=Image.open(os.path.join(CURRDIR, 'perspectives', 'perspective0.jpg')))
        imgLbl.config(image=tkImg)
        imgLbl.image = tkImg
        imgLbl.place(x=0, y=0, relwidth=1, relheight=1, bordermode="outside")
        
        for i in range(4):
            bodyLblFrm.grid_rowconfigure(i, weight=1)
        for i in range(3):
            bodyLblFrm.grid_columnconfigure(i, weight=1)

        self.errVar = tk.StringVar()
        self.pswdVar = tk.IntVar()
        MyLabel(bodyLblFrm, text='Username').grid(row=0, column=0, sticky='e', padx=2, pady=5)
        MyLabel(bodyLblFrm, text='Password').grid(row=1, column=0, sticky='e', padx=2, pady=5)
        self.errLbl = MyLabel(bodyLblFrm, fg='red', textvariable=self.errVar, wraplength=450)
        self.username = MyEntry(bodyLblFrm)
        self.pswdEnt = MyEntry(bodyLblFrm, show='*')
        self.showPswd = tk.Checkbutton(bodyLblFrm, text='Show', bg=BGCOLOR, fg=FGCOLOR,
                                        selectcolor='#101010', activebackground=BGCOLOR,
                                        activeforeground=FGCOLOR, variable=self.pswdVar,
                                        command=self.showHidePswd)

        self.username.grid(row=0, column=1, sticky='ew', padx=8)
        self.pswdEnt.grid(row=1, column=1, sticky='ew', padx=8)
        self.showPswd.grid(row=1, column=2, sticky='w', padx=8)
        ttk.Separator(bodyLblFrm, orient="horizontal").grid(row=3, column=0, columnspan=3, sticky="ew")

        bottomLblFrm = MyLabelFrame(self, text='', bd='2')
        bottomLblFrm.grid(row=2, column=0, sticky='nsew', pady=20)
        for i in range(1):
            bottomLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(1):
            bottomLblFrm.grid_rowconfigure(i, weight=1)

        MyButton(bottomLblFrm, text="Login", command=self.done) \
                .grid(row=0, column=0, sticky='e', padx=30)
        # MyButton(bottomLblFrm, text="Clear", command=self.clearAllEnt) \
        #         .grid(row=0, column=1, sticky='w', padx=30)
        for frm in self.winfo_children():
            for widg in frm.winfo_children():
                if widg.winfo_class() in CUSTATTRS:
                    widg.config(bg=BG, fg=FG, font=FNT)

    def showErr(self, msg):
        if isinstance(msg, list):
            msg = '\n'.join(msg)
        self.errVar.set(msg)
        # print(self.errLbl.grid_info())
        self.errLbl.grid(columnspan=3, padx=20)
        try:
            # if a timeout exists, cancel it/ restart it
            ROOT.after_cancel(self.intervalId)
        except AttributeError:
            pass
        # ungrid error label after 5000ms
        self.intervalId = ROOT.after(5000, lambda: self.errLbl.grid_forget())

        return True

    def goBack(self):
        import user_win
        with AppDb(tblName=USERDBTABLE, startPKFrom=USERMOVPK) as db:
            userPage = db.getPage(page=user_win.UserWin.page)
        ShowFrame(user_win.UserWin, thisPage=userPage)

    def showHidePswd(self):
        if self.pswdVar.get():
            self.pswdEnt.config(show='')
        else:
            self.pswdEnt.config(show='*')

    def done(self):
        with CredsDb(tblName=CREDSTABLE) as db:            
            userInfo = db.returnPersonInfo(self.username.get(), self.pswdEnt.get())
            if not userInfo or userInfo['isAdmin']:
                self.showErr('Username or Password does not match')
                return
            
            # Storer.storeLoggedIn(userInfo['username'])
            import configs
            configs.CURRLOGGEDIN = userInfo['username']
            # to get new value of CURRLOGGEDIN import configs again.
            from tkinter import messagebox
            messagebox.showinfo(message='Successfully logged in.')

if __name__ == '__main__':
    pass   

