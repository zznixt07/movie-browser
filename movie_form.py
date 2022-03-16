import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
# from PIL import ImageTk, Image
import os
import logging
from sql_db.sql_connector import AppDb
from configs import *
import configs

class MovieFormWin(CustomFrame):
    errorLst = []
    # thisDb = 'user_added_movs'

    def __init__(self, *args, **kwargs):
        CustomFrame.__init__(self)
        for i in range(1,2):
            self.grid_rowconfigure(i, weight=1)
        for i in range(1):
            self.grid_columnconfigure(i, weight=1)

        headerLblFrm = MyLabelFrame(self, text='')
        headerLblFrm.grid(row=0, column=0, sticky='nsew')
        for i in range(4):
            headerLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(1):
            headerLblFrm.grid_rowconfigure(i, weight=1)
        self.homeBtn = MyButton(headerLblFrm, text='Home', command=self.goHome)
        self.profileLbl = MyLabel(headerLblFrm, text=configs.CURRLOGGEDIN,
                                            font=('Consolas', 14, 'bold'),
                                            fg='#000', bg='#fff', wraplength=100)

        self.homeBtn.grid(row=0, column=0)
        self.profileLbl.grid(row=0, column=4, sticky='e')

        vcmd = (self.register(self.onValidate), '%s', '%S', '%d')
        bodyLblFrm = MyLabelFrame(self, text='body')
        bodyLblFrm.grid(row=1, column=0, sticky='nsew')
        bodyLblFrm.grid_columnconfigure(1, weight=1)
        bodyLblFrm.grid_columnconfigure(4, weight=1)
        for i in range(13):
            bodyLblFrm.grid_rowconfigure(i, weight=1)

        MyLabel(bodyLblFrm, text=('Labels with * are compulsory. More than one'
                                    + ' answers should be seperated with commas.')) \
                .grid(row=0, column=0, columnspan=6, sticky='', padx=10)
        self.entries = ('Title*', 'Rating', 'Total Rated By', 'Year Released', 'Genres',
                    'Country', 'Cast', 'Plot', 'Directors', 'Writers',
                    'Imdb Id', 'Poster Url/Path')
        self.seriesEntries = ('Start Year', 'End Year', 'Total Seasons', 'Total Episodes')
        self.entDict = {}
        self.imagePath = ''

        for row, lbl in enumerate(self.entries, start=1):
            MyLabel(bodyLblFrm, text=lbl, justify=tk.RIGHT,
                        font=(FNTFAMILY, FNTSIZE+2, 'bold')) \
                    .grid(row=row, column=0, sticky='E', padx=10)
        
        for row, entry in enumerate(self.entries, start=1):
            entry = entry.lower().replace(' ', '_')
            if entry == 'year_released':
                self.entDict[entry] = MyEntry(bodyLblFrm, width=50, bd=4,
                                            validate="all", validatecommand=vcmd)
            else:
                self.entDict[entry] = MyEntry(bodyLblFrm, width=50, bd=4)
            self.entDict[entry].grid(row=row, column=1, columnspan=2, sticky='w', padx=10)
            lastMaxRow = row
        
        MyButton(bodyLblFrm, text="Insert Poster", width=BTNWIDTH-2,
                        command=self.imageSelect).grid(row=lastMaxRow, column=3,
                                                        sticky='w', padx=30)

        for row, lbl in enumerate(self.seriesEntries, start=1):
            MyLabel(bodyLblFrm, text=lbl, justify=tk.RIGHT,
                        font=(FNTFAMILY, FNTSIZE+2, 'bold')) \
                    .grid(row=row, column=3, sticky='E', padx=10)
        
        for row, entry in enumerate(self.seriesEntries, start=1):
            entry = entry.lower().replace(' ', '_')
            self.entDict[entry] = MyEntry(bodyLblFrm, width=50, bd=4, state=tk.DISABLED,
                                            disabledbackground='#272727',
                                            validate="all", validatecommand=vcmd)
            self.entDict[entry].grid(row=row, column=4, columnspan=2, sticky='w', padx=10)

        self.isSeries = tk.IntVar()
        tk.Checkbutton(bodyLblFrm, text='TV-Show?', bg=BGCOLOR, fg=FGCOLOR,
                        font=(FNTFAMILY, FNTSIZE+2, 'bold'), selectcolor='#272727',
                        activebackground=BGCOLOR, activeforeground=FGCOLOR,
                        variable=self.isSeries, command=self.chkBtnClked) \
                        .grid(row=5, column=3, columnspan=2)
        # -------------- < Search widgets > -------------------------------
        searchLblFrm = MyLabelFrame(bodyLblFrm, text='searcher')
        searchLblFrm.grid(row=6, column=3, columnspan=2, sticky='ew')
        searchLblFrm.grid_columnconfigure(2, weight=1)
        searchLblFrm.grid_columnconfigure(3, weight=1)

        MyLabel(searchLblFrm, text='Search By:').grid(row=0, column=0)
        self.searchVar = tk.StringVar()
        MyOptionMenu(searchLblFrm, self.searchVar, *SEARCHBY).grid(row=0, column=1)
        self.searchVar.set(SEARCHBY[0])
        self.searchBar = MyEntry(searchLblFrm, bg=SEARCHBGCOLOR, bd=4, justify=tk.CENTER)
        searchBtn = MyButton(searchLblFrm, text='Search', command=self.displaySearchResults)
        self.searchBar.insert(0, 'Search Here...')
        self.searchBar.bind('<1>', self.clearSearch)
        self.searchBar.bind('<Return>', self.displaySearchResults)
        self.searchBar.grid(row=0, column=2, columnspan=2, sticky='ew')
        searchBtn.grid(row=0, column=4)
        # -------------- < /Search widgets > -------------------------------

        self.errVar = tk.StringVar()
        self.errLbl = MyLabel(bodyLblFrm, textvariable=self.errVar,
                                fg='red', font=(FNTFAMILY, FNTSIZE+2, 'bold'),
                                justify=tk.LEFT, wraplength=600)

        treeLblFrm = MyLabelFrame(bodyLblFrm, text='tree')
        treeLblFrm.grid(row=7, column=3, rowspan=5, columnspan=2, sticky='nsew', padx=50)
        for i in range(1):
            treeLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(1):
            treeLblFrm.grid_rowconfigure(i, weight=1)

        self.tree = ttk.Treeview(treeLblFrm, columns=('num', 'title', 'rating'), show='headings')
        self.tree.column('num', width=100)
        self.tree.column('title', width=200)
        self.tree.column('rating', width=130)
        self.tree.heading('num', text='No.', anchor='w')
        self.tree.heading('title', text='Title', anchor='w')
        self.tree.heading('rating', text='rating', anchor='w')
        # self.tree.grid(row=7, column=3, rowspan=5, columnspan=2, sticky='w', padx=100)
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.insertRowsInTree()
        
        self.scrollY = ttk.Scrollbar(treeLblFrm, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollY.grid(row=0, column=1, sticky='ns')
        self.tree.config(yscrollcommand=self.scrollY.set)

        # self.scrollY.grid(row=7, column=5, rowspan=3, sticky='ns')
        # self.scrollX = ttk.Scrollbar(bodyLblFrm, orient=tk.HORIZONTAL)
        # self.scrollX.grid(row=12, column=3, columnspan=2, sticky='ew')


        bottomLblFrm = MyLabelFrame(self, text='bottom')
        bottomLblFrm.grid(row=2, column=0, sticky='nsew')
        for i in range(3):
            bottomLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(1):
            bottomLblFrm.grid_rowconfigure(i, weight=1)

        MyButton(bottomLblFrm, text="Add/Update Movie", command=self.done) \
                .grid(row=0, column=0, sticky='e', padx=30)
        if configs.ISADMIN:
            MyButton(bottomLblFrm, text='Remove Movie', command=self.removeMovie) \
                    .grid(row=0, column=1, sticky='', padx=30)
        MyButton(bottomLblFrm, text="Clear", command=self.clearAllEnt) \
                .grid(row=0, column=2, sticky='w', padx=30)

    def insertRowsInTree(self, rows=None):
        self.tree.delete(*self.tree.get_children())
        if rows is None:
            with AppDb(tblName=USERDBTABLE, startPKFrom=USERMOVPK) as db:
                titles = db.getBasicInfo()
                for i, title in enumerate(titles, start=1):
                    rating = title[1] if title[1] is not None else 'N/A'
                    self.tree.insert(parent='', index='end',
                                        values=(i, title[0], rating))
        else:
            for i, title in enumerate(rows, start=1):
                rating = title[1] if title[1] is not None else 'N/A'
                self.tree.insert(parent='', index='end',
                                    values=(i, title[0], rating))

        # do not change to single click, cuz focus will happen slower
        # than single click
        self.tree.bind("<Double-1>", self.rowSelected)

    def rowSelected(self, *args):
        selectedTitle = self.tree.item(self.tree.focus())['values'][1]
        if selectedTitle:
            with AppDb(tblName=USERDBTABLE, startPKFrom=USERMOVPK) as db:
                movInfo = db.dictFromTitle(selectedTitle)

            for k, v in {**movInfo}.items():
                # entry doesnt allow inserting None. hence convert None to ''
                if v is None:
                    movInfo[k] = ''
                    continue
                # chnage list to string with comma between elements
                if isinstance(v, list):
                    movInfo[k] = ', '.join(v)

            # clear all fields
            self.clearAllEnt()

            self.entDict['title*'].insert(0, movInfo['title'])
            self.entDict['genres'].insert(0, movInfo['genres'])
            self.entDict['country'].insert(0, movInfo['country'])
            self.entDict['cast'].insert(0, movInfo['cast'])
            self.entDict['directors'].insert(0, movInfo['directors'])
            self.entDict['writers'].insert(0, movInfo['writers'])

            self.entDict['rating'].insert(0, movInfo['rating'])
            self.entDict['total_rated_by'].insert(0, movInfo['totalRatedBy'])
            self.entDict['year_released'].insert(0, movInfo['year'])
            self.entDict['plot'].insert(0, movInfo['plot'])
            self.entDict['imdb_id'].insert(0, movInfo['imdbId'])
            self.entDict['poster_url/path'].insert(0, movInfo['imgUrl'])
            self.isSeries.set(movInfo['isSeries'])
            if self.isSeries.get():
                logging.debug('checked')
                for ent in self.seriesEntries:
                    ent = ent.lower().replace(' ', '_')
                    self.entDict[ent].config(state=tk.NORMAL)

                self.entDict['start_year'].insert(0, movInfo['start'])
                self.entDict['end_year'].insert(0, movInfo['end'])
                self.entDict['total_episodes'].insert(0, movInfo['epNum'])
                self.entDict['total_seasons'].insert(0, movInfo['szNum'])
            else:
                for ent in self.seriesEntries:
                    ent = ent.lower().replace(' ', '_')
                    self.entDict[ent].config(state=tk.DISABLED)

    def clearSearch(self, *args):
        print('clked on Search', self.searchBar.get())
        # seems no way to select the current contents
        self.searchBar.delete(0, tk.END)
        self.searchBar.bind('<1>', lambda x: None)

    def displaySearchResults(self, *args):
        searchTerm = self.searchBar.get()
        colName = self.searchVar.get()
        if searchTerm != '':
            with AppDb(tblName=USERDBTABLE, startPKFrom=USERMOVPK) as db:
                matchingTitles = db.containing(colName=colName,
                                                searchExpr=searchTerm+'.*',
                                                useRegex=True)
            self.insertRowsInTree(rows=matchingTitles)


    def goHome(self):
        logging.debug('Home Btn pressed')
        # using class varaible, the page numbers are remembered and can be resumed
        import start_win
        with AppDb(tblName=DBTABLE) as db:
            homePage = db.getPage(page=start_win.StartWin.page)
        ShowFrame(start_win.StartWin, thisPage=homePage)

    def imageSelect(self, *args):
        self.imagePath = filedialog.askopenfilename(
                        filetypes=[('JPG', '*.jpg'), ('JPEG', '*.jpeg'), ('PNG', '*.png')],
                        title='Select image file to use as poster..')
        if self.imagePath != '':
            p = self.entDict['poster_url/path']
            p.config(state=tk.NORMAL)
            p.delete(0, tk.END)
            p.insert(0, self.imagePath)
            p.config(state='disabled')

    def onValidate(self, prevStr, currChar, opType):
        print(f'{opType=!r}')
        if opType == '1':     # insert
            if len(prevStr + currChar) < 5:
                if currChar.isdecimal():
                    # if starts with 0 then wont be a problem due to it being str
                    # since int('001') doesnt throw error
                    return True
        else:     # delete or focus
            return True
        return False

    def chkBtnClked(self, *args):
        logging.debug('clked on check btn')
        if self.isSeries.get():
            logging.debug('checked')
            for ent in self.seriesEntries:
                ent = ent.lower().replace(' ', '_')
                self.entDict[ent].config(state=tk.NORMAL)
        else:
            logging.debug('unchecked')
            for ent in self.seriesEntries:
                ent = ent.lower().replace(' ', '_')
                self.entDict[ent].config(state=tk.DISABLED)

    def clearAllEnt(self, *args):
        for ent in self.entries + self.seriesEntries:
            ent = self.entDict[ent.lower().replace(' ', '_')]
            if ent['state'].lower() == 'disabled':
                # if state is disabled cannot delete hence enable, delete and disable
                ent.config(state=tk.NORMAL)
                ent.delete(0, tk.END)
                ent.config(state=tk.DISABLED)
            else:
                ent.delete(0, tk.END)
        self.isSeries.set(0)

    def showErr(self, msg):
        self.errVar.set(msg)
        # print(self.errLbl.grid_info())
        self.errLbl.grid(row=6, column=3, rowspan=2, columnspan=2, sticky='nw', padx=20)
        try:
            # if a timeout exists, cancel it/ restart it
            ROOT.after_cancel(self.intervalId)
        except AttributeError:
            pass
        # ungrid error label after 5000ms
        self.intervalId = ROOT.after(5000, lambda: self.errLbl.grid_forget())

        return True

    def emptyTitle(self):
        if not self.entDict['title*'].get():
            # self.showErr('Title cannot be empty!')
            MovieFormWin.errorLst.append('Title cannot be empty!')
            return True
        return False

    def noTypeMatch(self):
        rating = None
        # float will throw error on empty string. and rating is opt.
        if self.entDict['rating'].get():
            try:
                rating = float(self.entDict['rating'].get())
                if rating > 10:
                    MovieFormWin.errorLst.append(
                        'Rating cannot be greater than 10!')
            except ValueError:
                # return self.showErr('Rating only accepts numbers(can contain decimals)!')
                MovieFormWin.errorLst.append(
                    'Rating only accepts numbers(can contain decimals)!')
                # dont return here to check for below problems

        d = {}
        for string in ('total_rated_by', 'year_released'):
            d[string] = None
            # int will throw error on empty string. and these are opt.
            if string == 'year_released':
                d['year_released'] = self.entDict[string].get()[:4]
            if self.entDict[string].get():
                try:
                    # float not allowed
                    d[string] = int(self.entDict[string].get())
                except ValueError:
                    # return self.showErr(f"{string.replace('_', ' ').title()} only accepts numbers!")
                    MovieFormWin.errorLst.append(
                        f"{string.replace('_', ' ').title()} only accepts numbers!")

        return {**{'rating': rating}, **d}

    def pathExists(self):
        pass
        # print('path is:', self.imagePath)
        # if self.imagePath:
        #     # its a non-empty path. check if it exists
        #     if not os.path.exists(self.imagePath):
        #         MovieFormWin.errorLst.append('Image Path is incorrect')
        #         return
        # don't try to check if url works.
        # if self.entDict['poster_url/path']:

    def convertToJson(self):
        import json
        d = {}
        haveList = ['country', 'cast', 'directors', 'writers', 'genres']
        for k in haveList:
            # if empty string replace with None. .split() messes up empty string.
            if self.entDict[k].get() == '':
                # add as what it is so that it can be handled uniformly at last.
                d[k] = ''
                continue
            lst = [name.strip() for name in self.entDict[k].get().split(',')]
            # we could leave it in list cuz sql class can handle lists.
            d[k] = json.dumps(lst)
        return d

    def checkSeries(self):
        if not self.isSeries.get():
            return {'start': '', 'end': '', 'szNum': '', 'epNum': ''}

        start = end = szNum = epNum = ''
        if self.entDict['start_year'].get() != '':
            start = int(self.entDict['start_year'].get())
        if self.entDict['end_year'].get() != '':
            end = int(self.entDict['end_year'].get())
        if self.entDict['total_seasons'].get() != '':
            szNum = int(self.entDict['total_seasons'].get())
            szNum = szNum if szNum < 255 else 254
        if self.entDict['total_episodes'].get() != '':
            epNum = int(self.entDict['total_episodes'].get())

        return {'start': start, 'end': end, 'szNum': szNum, 'epNum': epNum}

    def done(self, *args):
        # remove all previous errors appended to list.
        MovieFormWin.errorLst = []
        logging.debug('btn done clked')
        self.emptyTitle()
        i = self.noTypeMatch()
        self.pathExists()
        if MovieFormWin.errorLst:
            # self.showErr('\n'.join(MovieFormWin.errorLst))
            messagebox.showerror(message='\n'.join(MovieFormWin.errorLst))
            return

        logging.debug('all checked. no problem')
        s = self.checkSeries()
        j = self.convertToJson()
        from sql_db.sql_connector import AppDb
        with AppDb(tblName=USERDBTABLE, startPKFrom=USERMOVPK) as db:
            updateInstead = False
            if db.titleExists(self.entDict['title*'].get()):
                msg = ('This movie already exists in the database.'
                        + 'Press Yes to update info or No to cancel.')
                if not messagebox.askyesno(message=msg):
                    return
                # update instead of insert
                updateInstead = True
            db.insertAllCols([{
                'title': self.entDict['title*'].get(),
                'plot': self.entDict['plot'].get() or None,
                'imdbId': self.entDict['imdb_id'].get() or None,
                'imgUrl': self.entDict['poster_url/path'].get() or None,
                'isSeries': int(self.isSeries.get()),
                'rating': i['rating'] or None,
                'totalRatedBy': i['total_rated_by'] or None,
                'year': i['year_released'] or None,
                'start': s['start'] or None,
                'end': s['end'] or None,
                'epNum': s['epNum'] or None,
                'szNum': s['szNum'] or None,
                'genres': j['genres'] or None,
                'country': j['country'] or None,
                'cast': j['cast'] or None,
                'directors': j['directors'] or None,
                'writers': j['writers'] or None,
            }], updateInstead=updateInstead)
            pos = db.getLastPos

        if self.imagePath:
            # filename can only be possible after knowing `pos`
            filename = os.path.join(
                            CURRDIR,
                            'posters',
                            pos + '--original' + os.path.splitext(self.imagePath)[1])
            try:
                shutil.copy(self.imagePath, filename)
            except Exception as e:
                logging.error('%s', e)
        messagebox.showinfo(message='Operation completed successfully!')
        self.insertRowsInTree()

    def removeMovie(self):
        selectedTitle = self.tree.item(self.tree.focus())['values'][1]
        if not selectedTitle:
            messagebox.showerror(message='No movie selected yet. Double click to select.')
            return
        if configs.ISADMIN:
            with AppDb(tblName=USERDBTABLE, startPKFrom=USERMOVPK) as db:
                db.removeMovie(selectedTitle)
            messagebox.showinfo(message='Movie successfully removed.')
            self.insertRowsInTree()
        else:
            messagebox.showerror(message='You do not have enough previlage to remove movie.')


if __name__ == '__main__':
    pass

