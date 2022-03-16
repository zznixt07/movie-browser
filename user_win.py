import tkinter as tk
from PIL import ImageTk, Image
import os
import threading
import requests
import logging
import queue
from sql_db.sql_connector import AppDb
import configs


class UserWin(configs.CustomFrame):
    
    page = 1
    searchPage = 1

    def __init__(self, *args, **kwargs):
        configs.CustomFrame.__init__(self)
        # not scaling headerLblFrm cuz need max space for posters
        for i in range(1,2):
            self.grid_rowconfigure(i, weight=1)
        for i in range(1):
            self.grid_columnconfigure(i, weight=1)

        print('initializing User Page')
        self.thisPage = kwargs['thisPage']
        # used to grid images later after fetching image and knowing when all
        # images have been grided. Each image grided -> coressponding labelframe
        # poped. Here, Label frames are used to group widgets.
        self.labelFrames = []
        print('PAGE IS', UserWin.page)
        
        headerLblFrm = configs.MyLabelFrame(self)
        headerLblFrm.grid(row=0, column=0, sticky='nsew')
        
        for i in range(8):
            headerLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(1):
            headerLblFrm.grid_rowconfigure(i, weight=1)

        self.homeBtn = configs.MyButton(headerLblFrm, text='Home', command=self.goHome)
        # -------------- < Search widgets > -------------------------------
        self.searchLblFrm = configs.MyLabelFrame(headerLblFrm, text='searcher')
        self.searchLblFrm.grid_columnconfigure(2, weight=1)
        self.searchLblFrm.grid_columnconfigure(3, weight=1)

        configs.MyLabel(self.searchLblFrm, text='Search By:').grid(row=0, column=0)
        self.searchVar = tk.StringVar()
        configs.MyOptionMenu(self.searchLblFrm, self.searchVar, *configs.SEARCHBY) \
                            .grid(row=0, column=1)
        self.searchVar.set(configs.SEARCHBY[0])
        self.searchBar = configs.MyEntry(self.searchLblFrm, bg=configs.SEARCHBGCOLOR,
                                            bd=4, justify=tk.CENTER)
        searchBtn = configs.MyButton(self.searchLblFrm, text='Search', width=7,
                                command=self.displaySearchResults)
        self.searchBar.insert(0, 'Search Here.....')
        self.searchBar.bind('<1>', self.clearSearch)
        self.searchBar.bind('<Return>', self.displaySearchResults)
        self.searchBar.grid(row=0, column=2, columnspan=2, sticky='ew')
        searchBtn.grid(row=0, column=4)
        # --------------- < /Search widgets > -------------------------

        self.userLoginBtn = configs.MyButton(headerLblFrm, text='Login', command=self.userLogin)
        self.userSignUpBtn = configs.MyButton(headerLblFrm, text='Sign Up', command=self.userSignUp)
        self.addMovBtn = configs.MyButton(headerLblFrm, text='Add new movies',
                                            command=self.addMovie)
        self.profileLbl = configs.MyLabel(headerLblFrm, font=('Consolas', 14, 'bold'),
                                            fg='#000', bg='#fff', wraplength=100)

        self.threadedGrid()

    def threadedGrid(self, searching=False):
        self.bodyLblFrm = configs.MyLabelFrame(self)
        self.bodyLblFrm.grid(row=1, column=0, sticky='nsew')

        for i in range(1, configs.NOFCOLS+1):
            self.bodyLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(0, configs.NOFROWS+1):
            self.bodyLblFrm.grid_rowconfigure(i, weight=1)
        if searching:
            self.prevBtn = configs.MyButton(self.bodyLblFrm, text='<', width=1, height=20,
                                        command=self.prevSearchPage)
            self.nextBtn = configs.MyButton(self.bodyLblFrm, text='>', width=1, height=20,
                                        command=self.nextSearchPage)
        else:
            self.prevBtn = configs.MyButton(self.bodyLblFrm, text='<', width=1, height=20,
                                        command=self.prevPage)
            self.nextBtn = configs.MyButton(self.bodyLblFrm, text='>', width=1, height=20,
                                        command=self.nextPage)


        for i in range(len(self.thisPage)):
            lblFrm = configs.MyLabelFrame(self.bodyLblFrm, text='')
            self.labelFrames.append(lblFrm)
            imgLbl = configs.MyLabel(lblFrm, wraplength=200, justify=tk.LEFT)
            movieInfoLbl = configs.MyLabel(lblFrm, fg='#f7f4e0', wraplength=200, justify=tk.LEFT)
            imgLbl.grid(row=0, column=0)
            movieInfoLbl.grid(row=1, column=0, sticky='w')

            l = configs.GRIDLAYOUT[i]
            lblFrm.grid(row=int(l[0]), column=int(l[1]))
            # when either the image or title is clicked. expand movie details.
            movieInfoLbl.bind('<1>', self.showFullInfo)
            imgLbl.bind('<1>', self.showFullInfo)

        for movie in self.thisPage:
            url = movie['imgUrl']
            # this means data should alwz have pos -> so it must come from SQL
            file = str(movie['pos'])
            text = f"{movie['title']}\nrating: {movie['rating']}"
            t0 = threading.Thread(target=self.downloadImg, args=[url, file, text])
            t0.start()
        
        # t1 = threading.Thread(target=self.imagesPathManager)
        # t1.start()
        self.periodicCall()
    
    def periodicCall(self):
        '''
        1. check the queue
        2. check if all images are grided
        > keep repeating above instructions
        '''
        self.imagesPathManager()
        if not self.labelFrames:
            # if all images in label frames are gridded, then display buttons
            # and stop checking queue
            logging.info('showing buttons')
            self.homeBtn.grid(row=0, column=0)
            self.searchLblFrm.grid(row=0, column=1, columnspan=3, sticky='ew')
            
            self.userLoginBtn.grid(row=0, column=4)
            self.userSignUpBtn.grid(row=0, column=5)
            self.addMovBtn.grid(row=0, column=6)
            # import configs
            if configs.CURRLOGGEDIN:
                self.profileLbl.config(text=configs.CURRLOGGEDIN)
                self.profileLbl.grid(row=0, column=7, sticky='e')

            self.prevBtn.grid(row=0, column=0, rowspan=2)
            self.nextBtn.grid(row=0, column=6, rowspan=2)
            return # see above

        configs.ROOT.after(300, self.periodicCall)

    def showFullInfo(self, e, *args):
        # e.widget gives the curr clicked widget/label.the title of movie is
        # present in the image label. the title gets covered by the image.
        # also if thier is no pic. both pic and text are not grided.
        # MYSQL Searching is CASE-INSENSITIVE. so all uppercase is ok.
        movieName = e.widget.master.winfo_children()[1]['text'].split('\n')[0]
        import full_movie
        configs.ShowFrame(full_movie.Info, movieName, dbTable=configs.USERDBTABLE)

    def clearSearch(self, *args):
        logging.debug('clked on Search', self.searchBar.get())
        # seems no way to select the current contents
        self.searchBar.delete(0, tk.END)

    def displaySearchResults(self, *args):
        searchTerm = self.searchBar.get()
        colName = self.searchVar.get()
        if searchTerm != '':
            with AppDb(tblName=configs.USERDBTABLE) as db:
                fullInfo = db.fullMovInfoRegex(page=self.searchPage,
                                                colName=colName,
                                                searchExpr=searchTerm+'.*',
                                                useRegex=True)
            self.thisPage = fullInfo
            if not self.thisPage: return None
            self.bodyLblFrm.grid_forget()
            self.threadedGrid(searching=True)
            return True

    def goHome(self):
        logging.debug('Home Btn pressed')
        # using class varaible, the page numbers are remembered and can be resumed
        import start_win
        with AppDb(tblName=configs.DBTABLE) as db:
            homePage = db.getPage(page=start_win.StartWin.page)
        configs.ShowFrame(start_win.StartWin, thisPage=homePage)

    def nextPage(self):
        logging.debug('next Btn pressed')
        UserWin.page += 1
        with AppDb(tblName=configs.USERDBTABLE, startPKFrom=configs.USERMOVPK) as db:
            nextPage = db.getPage(page=UserWin.page)
        if not nextPage:
            UserWin.page -= 1
            return
        else:
            self.destroy()
            configs.ShowFrame(UserWin, thisPage=nextPage)

    def prevPage(self):
        logging.debug('prev Btn pressed')
        UserWin.page -= 1
        with AppDb(tblName=configs.USERDBTABLE, startPKFrom=configs.USERMOVPK) as db:
            prevPage = db.getPage(page=UserWin.page)
        if not prevPage:
            UserWin.page += 1
            return
        else:
            self.destroy()
            configs.ShowFrame(UserWin, thisPage=prevPage)

    def nextSearchPage(self,):
        self.searchPage += 1
        if not self.displaySearchResults():
            self.searchPage -= 1

    def prevSearchPage(self,):
        self.searchPage -= 1
        if not self.displaySearchResults():
            self.searchPage += 1

    def userLogin(self):
        import user_activity
        configs.ShowFrame(user_activity.UserLogin)

    def userSignUp(self):
        import user_activity
        configs.ShowFrame(user_activity.UserSignup)

    def addMovie(self):
        if not configs.CURRLOGGEDIN:        # username will always be string
            from tkinter import messagebox
            msg = ('To add new movies, you must log in first!\n'
                    + 'New users ought to sign up.')
            messagebox.showerror(message=msg)
            return

        import movie_form
        configs.ShowFrame(movie_form.MovieFormWin)

    def resizeImage(self, imgPath, name, ext):
        imgObj = Image.open(imgPath)
        w, h = imgObj.size[0], imgObj.size[1]
        sizes = {'large': 268/h}
        for size in sizes.keys():
            file = f'{name}--{size}{ext}'
            if os.path.exists(file): continue
            logging.debug('resizing %s', name)
            newImg = imgObj.resize((int(w * sizes[size]), int(h * sizes[size])))
            newImg.save(file)

    def imagesPathManager(self):
        while configs.IMAGESQUEUE.qsize():
        # while self.labelFrames:
            try:
                # if self.labelFrames: return
                imgPath, text = configs.IMAGESQUEUE.get(0)

                logging.info('popping 1st labelFrame from %s', self.labelFrames)
                frm = self.labelFrames.pop(0)
                if imgPath is not None:
                    # download error
                    name, ext = os.path.splitext(imgPath)
                    name = name.split('--')[0]
                    # imgPath = name.split('--')[0] + '--medium' + ext
                    # images are grided as they are downloaded hence they will be 
                    # placed randomly first time. However after they are in db. they
                    # are placed in the order they were in. (descending ratings)
                    logging.debug('gridding image %s', name)
                    self.resizeImage(imgPath, name, ext)

                    tkImg = ImageTk.PhotoImage(image=Image.open(name + '--large' + ext))
                    frm.winfo_children()[0].config(image=tkImg, text=text)
                    frm.winfo_children()[0].image = tkImg
                frm.winfo_children()[1].config(text=text.upper())
                configs.IMAGESQUEUE.task_done()
                logging.debug('gridding done ---')
            except queue.Empty:
                pass

    def downloadImg(self, url, name, text, pathOnly=None):
        if url is None:
            configs.IMAGESQUEUE.put([None, text])
            return

        if not pathOnly: pathOnly = os.path.join(configs.CURRDIR, 'posters')
        os.makedirs(pathOnly, exist_ok=True)
        # WILL IMAGE ALWAYZ BE IN .jpg?? This will be used as download path.
        fullPath = os.path.join(pathOnly, name + '--original.jpg')

        for ext in ['.jpg', '.jpeg', '.png']:
            if os.path.exists(os.path.splitext(fullPath)[0] + ext):
                # return fullPath, name
                logging.info('already dwnloaded. putting %s to image queue', name)
                configs.IMAGESQUEUE.put([os.path.splitext(fullPath)[0] + ext, text])
                return

        logging.info('dwnlding and putting %s to image queue', name)
        # dwnldPath = Neutron.get(url, customName=name+'--original.jpg', customPath=pathOnly)
        try:
            r = configs.SESS.get(url, stream=True, verify=False)
        except requests.exceptions.ConnectionError:
            logging.warning('dwnlding %s failed!! ', name)
            configs.IMAGESQUEUE.put([None, text])
            return
        if r.status_code != 200: return
        # not required cuz imdbid is used for filename
        # dwnldPath = removeInvalidCharInPath(fullPath)
        with open(fullPath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                f.write(chunk)

        configs.IMAGESQUEUE.put([fullPath, text])
        return


if __name__ == '__main__':
    pass

