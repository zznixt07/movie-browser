from configs import *
import tkinter as tk
from PIL import ImageTk, Image
import os
import threading
import requests
import logging
from sql_db.sql_connector import AppDb


class StartWin(CustomFrame):
    page = 1
    searchPage = 1

    def __init__(self, *args, **kwargs):
        print('root window', ROOT)
        CustomFrame.__init__(self)
        # not scaling headerLblFrm cuz need max space for posters
        for i in range(1,2):
            self.grid_rowconfigure(i, weight=1)
        for i in range(1):
            self.grid_columnconfigure(i, weight=1)

        # movies must be prepended to sql table to display user movies as well
        # as imdb movies.
        self.thisPage = kwargs['thisPage']
        # used to grid images later after fetching image and knowing when all
        # images have been grided. Each image grided -> coressponding labelframe
        # poped. Here, Label frames are used to group widgets.
        self.labelFramesDict = {}
        self.labelFrames = []
        print('PAGE IS', StartWin.page)
        
        headerLblFrm = MyLabelFrame(self)
        headerLblFrm.grid(row=0, column=0, sticky='nsew')
        
        for i in range(7):
            headerLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(1):
            headerLblFrm.grid_rowconfigure(i, weight=1)

        self.homeBtn = MyButton(headerLblFrm, text='Home', command=self.goHome)
        # -------------- < Search widgets > -------------------------------
        self.searchLblFrm = MyLabelFrame(headerLblFrm, text='searcher')
        self.searchLblFrm.grid_columnconfigure(2, weight=1)
        self.searchLblFrm.grid_columnconfigure(3, weight=1)

        MyLabel(self.searchLblFrm, text='Search By:').grid(row=0, column=0)
        self.searchVar = tk.StringVar()
        MyOptionMenu(self.searchLblFrm, self.searchVar, *SEARCHBY).grid(row=0, column=1)
        self.searchVar.set(SEARCHBY[0])
        self.searchBar = MyEntry(self.searchLblFrm, bg=SEARCHBGCOLOR, bd=4, justify=tk.CENTER)
        searchBtn = MyButton(self.searchLblFrm, text='Search', width=7,
                                command=self.displaySearchResults)
        self.searchBar.insert(0, 'Search Here.....')
        self.searchBar.bind('<1>', self.clearSearch)
        self.searchBar.bind('<Return>', self.displaySearchResults)
        self.searchBar.grid(row=0, column=2, columnspan=2, sticky='ew')
        searchBtn.grid(row=0, column=4)
        # --------------- < /Search widgets > -------------------------
        self.adminBtn = MyButton(headerLblFrm, text='Admin', command=self.goAdmin)
        self.userBtn = MyButton(headerLblFrm, text='User', command=self.goUser)

        # ------------------- <body> ------------------------

        self.threadedGrid()

    def threadedGrid(self, searching=False):
        self.bodyLblFrm = MyLabelFrame(self)
        self.bodyLblFrm.grid(row=1, column=0, sticky='nsew')
        for i in range(1, NOFCOLS+1):
            self.bodyLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(0, NOFROWS+1):
            self.bodyLblFrm.grid_rowconfigure(i, weight=1)
        if searching:
            self.prevBtn = MyButton(self.bodyLblFrm, text='<', width=1, height=BTNHEIGHT+20,
                                    command=self.prevSearchPage)
            self.nextBtn = MyButton(self.bodyLblFrm, text='>', width=1, height=BTNHEIGHT+20,
                                    command=self.nextSearchPage)
        else:
            self.prevBtn = MyButton(self.bodyLblFrm, text='<', width=1, height=BTNHEIGHT+20,
                                    command=self.prevPage)
            self.nextBtn = MyButton(self.bodyLblFrm, text='>', width=1, height=BTNHEIGHT+20,
                                    command=self.nextPage)
            

        for i in range(len(self.thisPage)):
            lblFrm = MyLabelFrame(self.bodyLblFrm, text='body')
            
            self.labelFrames.append(lblFrm)
            imgLbl = MyLabel(lblFrm, wraplength=200, justify=tk.LEFT)
            movieInfoLbl = MyLabel(lblFrm, fg='#f7f4e0', wraplength=200, justify=tk.LEFT)
            imgLbl.grid(row=0, column=0)
            movieInfoLbl.grid(row=1, column=0, sticky='w')

            l = GRIDLAYOUT[i]
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
            self.searchLblFrm.grid(row=0, column=1, columnspan=4, sticky='ew')
            self.adminBtn.grid(row=0, column=5)
            self.userBtn.grid(row=0, column=6)

            self.prevBtn.grid(row=0, column=0, rowspan=2)
            self.nextBtn.grid(row=0, column=6, rowspan=2)
            # again fill labelFrames for searchfunc
            # self.labelFrames = self.labelFramesFixLen[:]
            return # see above
        ROOT.after(300, self.periodicCall)

    def showFullInfo(self, e, *args):
        # e.widget gives the curr clicked widget/label.the title of movie is
        # present in the image label. the title gets covered by the image.
        # also if thier is no pic. both pic and text are not grided.
        # MYSQL Searching is CASE-INSENSITIVE. so all uppercase is ok.
        movieName = e.widget.master.winfo_children()[1]['text'].split('\n')[0]
        import full_movie
        ShowFrame(full_movie.Info, movieName, dbTable=DBTABLE)

    def clearSearch(self, *args):
        logging.debug('clked on Search', self.searchBar.get())
        # seems no way to select the current contents
        self.searchBar.delete(0, tk.END)
        self.searchBar.bind('<1>', lambda x: None)

    def displaySearchResults(self, *args, **kwargs):
        searchTerm = self.searchBar.get()
        colName = self.searchVar.get()
        if searchTerm != '':
            with AppDb(tblName=DBTABLE) as db:
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
        StartWin.page = 1
        with AppDb(tblName=DBTABLE) as db:
            homePage = db.getPage(page=StartWin.page)
        ShowFrame(StartWin, thisPage=homePage)

    def nextPage(self,):
        logging.debug('next Btn pressed')
        StartWin.page += 1
        with AppDb(tblName=DBTABLE) as db:
            nextPage = db.getPage(page=StartWin.page)
        if not nextPage:
            StartWin.page -= 1
            return
        else:
            self.destroy()
            ShowFrame(StartWin, thisPage=nextPage)

    def prevPage(self, ):
        logging.debug('prev Btn pressed')
        StartWin.page -= 1
        with AppDb(tblName=DBTABLE) as db:
            prevPage = db.getPage(page=StartWin.page)
        if not prevPage:
            StartWin.page += 1
            return
        else:
            self.destroy()
            ShowFrame(StartWin, thisPage=prevPage)

    def nextSearchPage(self,):
        self.searchPage += 1
        if not self.displaySearchResults():
            self.searchPage -= 1

    def prevSearchPage(self,):
        self.searchPage -= 1
        if not self.displaySearchResults():
            self.searchPage += 1

    def goAdmin(self):
        import admin_win
        ShowFrame(admin_win.AdminWin)

    def goUser(self):
        import user_win
        with AppDb(tblName=USERDBTABLE, startPKFrom=USERMOVPK) as db:
            userPage = db.getPage(page=user_win.UserWin.page)
        ShowFrame(user_win.UserWin, thisPage=userPage)

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
        while IMAGESQUEUE.qsize():
        # while self.labelFrames:
            try:
                # if self.labelFrames: return
                imgPath, text = IMAGESQUEUE.get(0)
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
                    # also add text so that the label can be identified
                    frm.winfo_children()[0].config(image=tkImg, text=text)
                    frm.winfo_children()[0].image = tkImg
                frm.winfo_children()[1].config(text=text.upper())
                IMAGESQUEUE.task_done()
                logging.debug('gridding done ---')
            except queue.Empty:
                pass

    def downloadImg(self, url, name, text, pathOnly=None):
        if url is None:
            IMAGESQUEUE.put([None, text])
            return

        if not pathOnly: pathOnly = os.path.join(CURRDIR, 'posters')
        os.makedirs(pathOnly, exist_ok=True)
        # WILL IMAGE ALWAYZ BE IN .jpg?? This will be used as download path.
        fullPath = os.path.join(pathOnly, name + '--original.jpg')

        for ext in ['.jpg', '.jpeg', '.png']:
            if os.path.exists(os.path.splitext(fullPath)[0] + ext):
                # return fullPath, name
                logging.info('already dwnloaded. putting %s to image queue', name)
                IMAGESQUEUE.put([os.path.splitext(fullPath)[0] + ext, text])
                return

        logging.info('dwnlding and putting %s to image queue', name)
        # dwnldPath = Neutron.get(url, customName=name+'--original.jpg', customPath=pathOnly)
        try:
            r = SESS.get(url, stream=True, verify=False)
        except requests.exceptions.ConnectionError:
            logging.warning('dwnlding %s failed!! ', name)
            IMAGESQUEUE.put([None, text])
            return
        if r.status_code != 200: return
        # not required cuz imdbid is used for filename
        # dwnldPath = removeInvalidCharInPath(fullPath)
        with open(fullPath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                f.write(chunk)

        IMAGESQUEUE.put([fullPath, text])
        return

"""
class Poster:

    def __init__(self):
        self.imgPath = imgPath
        try:
            self.imgObj = Image.open(self.imgPath)
        except (FileNotFoundError, UnidentifiedImageError, ValueError, AttributeError):
            return
        self.name, self.ext = os.path.splitext(self.imgPath)
        self.name = self.name.split('--')[0]
        self.resizeImage()

        # mediumImg = Image.open(self.name + '--medium' + self.ext)
        ImageTk.PhotoImage.__init__(self, image=Image.open(f'{self.name}--{Poster.currSize}{self.ext}'))

        self.imgLbl = tk.Label(master=lblFrm, image=self)
        self.imgLbl.grid(row=0, column=0)
        Poster.imgLbls[Poster.indexes] = self.imgLbl
        Poster.indexes += 1
        self.aspectRatio = self.imgObj.size[0] / self.imgObj.size[1]

        # only bind to one labelFrame. cuz all have same height difference
        if not Poster.binded:
            Poster.binded = True
            lblFrm.bind('<Configure>', self.resizer)
            # SeaOfWindows.mainFrame.bind('<Configure>', self.resizer)


    def resizeImage(self):
        w, h = self.imgObj.size[0], self.imgObj.size[1]
        sizes = {'small': 80/h, 'medium': 160/h, 'large': 268/h}
        for size in sizes.keys():
            file = os.path.join(CURRDIR, f'{self.name}--{size}{self.ext}')
            if os.path.exists(file): continue
            logging.debug('resizing %s', self.name)
            newImg = self.imgObj.resize((int(w * sizes[size]), int(h * sizes[size])))
            newImg.save(file)

    def resizer(self, event):
        '''
        ratioH = 1
        h = int(float(self.imgLbl.winfo_height() / ratioH))
        w = int(float(h * self.aspectRatio))
        # print(w,h)
        # self.imgLbl.config(width=w)
        # self.imgLbl.config(height=h)

        img = ImageTk.PhotoImage(image=self.imgObj.resize((w, h)))
        self.imgLbl.configure(image=img)
        self.imgLbl.image = img
        '''
        imgHeight = event.height
        logging.debug('current height is %s', imgHeight)
        logging.debug()
        if imgHeight < SCRNHGHT * 0.4:
            # if the poster is already small, dont redraw it!!
            if Poster.currSize == 'small': return
            Poster.currSize = 'small'
        elif imgHeight < SCRNHGHT * 0.65:
            if Poster.currSize == 'medium': return
            Poster.currSize = 'medium'
        else:
            if Poster.currSize == 'large': return
            Poster.currSize = 'large'
        print('changing size to', Poster.currSize)

        i = 0
        for img in StartWin.imgLst:
            name, ext = os.path.splitext(img)
            imgPath = f'{name.split("--")[0]}--{Poster.currSize}{ext}'
            try:
                tkImg = ImageTk.PhotoImage(image=Image.open(imgPath))
            except (FileNotFoundError, UnidentifiedImageError, ValueError, AttributeError):
                continue
            Poster.imgLbls[i].configure(image=tkImg)
            Poster.imgLbls[i].image = tkImg
            i += 1
"""



if __name__ == '__main__':
    pass

