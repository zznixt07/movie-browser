# import tkinter as tk
# from tkinter import ttk
from PIL import ImageTk, Image
# from tkinter import filedialog
# from tkinter import messagebox
import os
import configs
from sql_db.sql_connector import CredsDb, AppDb


class Info(configs.CustomFrame):

    def __init__(self, movieName, dbTable=None):
        self.dbTable = dbTable
        configs.CustomFrame.__init__(self)
        for i in range(1, 2):
            self.grid_rowconfigure(i, weight=1)
        for i in range(1):
            self.grid_columnconfigure(i, weight=1)

        headerLblFrm = configs.MyLabelFrame(self)
        headerLblFrm.grid(row=0, column=0, sticky='nsew')
        for i in range(1):
            headerLblFrm.grid_columnconfigure(i, weight=1)
        headerLblFrm.grid_rowconfigure(0, weight=1)
        configs.MyButton(headerLblFrm, text='Back',
                            command=lambda: self.lower()).grid(columnspan=3)

        # --------------------------- BODY -----------------------------------
        bodyLblFrm = configs.MyLabelFrame(self, text='body')
        bodyLblFrm.grid(row=1, column=0, sticky='nsew')
        for i in range(1, 3):
            bodyLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(1):
            bodyLblFrm.grid_rowconfigure(i, weight=1)

        info = configs.changeToStr(self.getFullDetails(movieName))
        # print(info)
        if not info: return
        posterPath = os.path.join(configs.CURRDIR, 'posters',
                                    str(info['pos']) + '--original.jpg')
        if not os.path.exists(posterPath):
            posterPath = os.path.join(configs.CURRDIR, 'jpgs', 'no-poster.jpg')
        imgLbl = configs.MyLabel(bodyLblFrm)
        imgLbl.grid(row=0, column=0, sticky='nsew')
        imgObj = Image.open(posterPath)
        w, h = imgObj.size[0], imgObj.size[1]
        imgObj = imgObj.resize((480, int((480/w) * h)))
        tkImg = ImageTk.PhotoImage(image=imgObj)
        imgLbl.config(image=tkImg)
        imgLbl.image = tkImg

        infoLblFrm = configs.MyLabelFrame(bodyLblFrm, text='info')
        infoLblFrm.grid(row=0, column=1, columnspan=2, sticky='nsew')
        for i in range(1):
            infoLblFrm.grid_columnconfigure(i, weight=1)
        for i in range(15):
            infoLblFrm.grid_rowconfigure(i, weight=1)

        # do I have a plot?
        plotArea = configs.MyLabelFrame(infoLblFrm)
        plotArea.config(text='plot', labelanchor='nw', bd=1)
        plotArea.grid(padx=50, sticky='nsew')
        configs.MyLabel(plotArea, text=info['plot'], wraplength=700).grid(padx=20)

        configs.MyLabel(infoLblFrm, text=f"Year Released: {info['year']}") \
                    .grid(padx=50, sticky='w')
        configs.MyLabel(infoLblFrm, text=f"Rating: {info['rating']}") \
                    .grid(padx=50, sticky='w')
        configs.MyLabel(infoLblFrm, text=f"Total rated by: {info['totalRatedBy']}") \
                    .grid(padx=50, sticky='w')
        configs.MyLabel(infoLblFrm, text='Genres: '+info['genres']) \
                    .grid(padx=50, sticky='w')
        configs.MyLabel(infoLblFrm, text='Directors: '+info['directors']) \
                    .grid(padx=50, sticky='w')
        configs.MyLabel(infoLblFrm, text='Writers: '+info['writers']) \
                    .grid(padx=50, sticky='w')
        configs.MyLabel(infoLblFrm, text='Country: '+info['country']) \
                    .grid(padx=50, sticky='w')
        configs.MyLabel(infoLblFrm,
                        text='Type: ' + ('Tv- Series' if info['isSeries'] else 'Movie')) \
                    .grid(padx=50, sticky='w')
        if info['isSeries']:
            configs.MyLabel(infoLblFrm, text=f"Year Finished: {info['end']}") \
                        .grid(padx=50, sticky='w')
            configs.MyLabel(infoLblFrm, text=f"Number of Seasons: {info['szNum']}") \
                        .grid(padx=50, sticky='w')
            configs.MyLabel(infoLblFrm, text=f"Number of Episodes: {info['epNum']}") \
                        .grid(padx=50, sticky='w')

        for widg in infoLblFrm.winfo_children():
            widg.config(font=('Consolas', 14, 'bold'))

        # plotArea = configs.MyLabelFrame(infoLblFrm)
        # plotArea.config(text='plot', labelanchor='nw', bd=1)
        # plotArea.grid(row=0, column=1, sticky='nsew')
        # configs.MyLabel(plotArea, text='hi'*100).grid()

        # plotArea = configs.MyLabelFrame(infoLblFrm)
        # plotArea.config(text='plot', labelanchor='nw', bd=1)
        # plotArea.grid(row=0, column=1, sticky='nsew')
        # configs.MyLabel(plotArea, text='hi'*100).grid()

        # plotArea = configs.MyLabelFrame(infoLblFrm)
        # plotArea.config(text='plot', labelanchor='nw', bd=1)
        # plotArea.grid(row=0, column=1, sticky='nsew')
        # configs.MyLabel(plotArea, text='hi'*100).grid()

        # plotArea = configs.MyLabelFrame(infoLblFrm)
        # plotArea.config(text='plot', labelanchor='nw', bd=1)
        # plotArea.grid(row=0, column=1, sticky='nsew')
        # configs.MyLabel(plotArea, text='hi'*100).grid()

        # plotArea = configs.MyLabelFrame(infoLblFrm)
        # plotArea.config(text='plot', labelanchor='nw', bd=1)
        # plotArea.grid(row=0, column=1, sticky='nsew')
        # configs.MyLabel(plotArea, text='hi'*100).grid()

        # plotArea = configs.MyLabelFrame(infoLblFrm)
        # plotArea.config(text='plot', labelanchor='nw', bd=1)
        # plotArea.grid(row=0, column=1, sticky='nsew')
        # configs.MyLabel(plotArea, text='hi'*100).grid()

        # plotArea = configs.MyLabelFrame(infoLblFrm)
        # plotArea.config(text='plot', labelanchor='nw', bd=1)
        # plotArea.grid(row=0, column=1, sticky='nsew')
        # configs.MyLabel(plotArea, text='hi'*100).grid()

        # plotArea = configs.MyLabelFrame(infoLblFrm)
        # plotArea.config(text='plot', labelanchor='nw', bd=1)
        # plotArea.grid(row=0, column=1, sticky='nsew')
        # configs.MyLabel(plotArea, text='hi'*100).grid()

        # plotArea = configs.MyLabelFrame(infoLblFrm)
        # plotArea.config(text='plot', labelanchor='nw', bd=1)
        # plotArea.grid(row=0, column=1, sticky='nsew')
        # configs.MyLabel(plotArea, text='hi'*100).grid()

        # plotArea = configs.MyLabelFrame(infoLblFrm)
        # plotArea.config(text='plot', labelanchor='nw', bd=1)
        # plotArea.grid(row=0, column=1, sticky='nsew')
        # configs.MyLabel(plotArea, text='hi'*100).grid()

        # plotArea = configs.MyLabelFrame(infoLblFrm)
        # plotArea.config(text='plot', labelanchor='nw', bd=1)
        # plotArea.grid(row=0, column=1, sticky='nsew')
        # configs.MyLabel(plotArea, text='hi'*100).grid()
        
    def getFullDetails(self, movieName):
        print(f'{movieName=!r}')
        with AppDb(tblName=self.dbTable) as db:
            return db.dictFromTitle(movieName)


