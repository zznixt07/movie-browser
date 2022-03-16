import logging
import traceback
import json
import bcrypt
import mysql.connector
from mysql.connector import errorcode

FORMAT = '%(levelname)s, %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)


class AppDb:
    '''
    Used to store movie details especially IMDB movies in MYSQL DB
    '''
    haveList = ['country', 'cast', 'directors', 'writers', 'genres']
    keys = ['pos', 'imdbId', 'imgUrl', 'title', 'rating', 'totalRatedBy',
                'year', 'genres', 'isSeries', 'start', 'end', 'epNum', 'szNum', 
                'country', 'cast', 'plot', 'directors', 'writers',]

    def __enter__(self):
        # return self instead of self.conn or self.cur to allow methods to be called
        return self

    def __exit__(self, excType, excValue, excTraceback):
        if excType is not None:
            print(excType)
            print(excValue)
            print(excTraceback)
        self.conn.commit()
        self.cur.close()
        self.conn.close()
        # return True # supress exceptions

    def __init__(self, tblName: str, startPKFrom: int = 10):
        '''
        Initialize connection and create db and table
        '''
        logging.debug('connecting to mysql')
        self.dbName = 'movie_app_database'
        self._startPKFrom = startPKFrom
        self.tblName = tblName
        self.conn = mysql.connector.connect(**CONFIG)
        self.cur = self.conn.cursor()
        self._createDatabase()
        self._createTable()

    @property
    def getCursor(self):
        return self.cur

    @property
    def getLastPos(self):
        return self.cur.lastrowid

    # @property
    # def startingRowVal(self):
    #     return self._startPkFrom
    
    # @startingRowVal.setter
    # def startingRowVal(self, startFrom):
    #     self._startPKFrom = start

    def _createDatabase(self):
        logging.debug('creating database %s if it doesnt exists', self.dbName)
        self.cur.execute('CREATE DATABASE IF NOT EXISTS `{}`'.format(self.dbName))
        self.conn.database = self.dbName
        return True
        
    def _createTable(self):
        logging.debug('creating table %s', self.tblName)
        # inject here...
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS `{tbl}` (
                pos INT UNSIGNED NOT NULL AUTO_INCREMENT,
                imdb_id VARCHAR(15),
                img_url VARCHAR(500),
                title VARCHAR(100) NOT NULL UNIQUE,
                rating FLOAT(3, 1) CHECK (rating >= 0 AND rating <= 10),
                total_rated_by BIGINT UNSIGNED,
                year SMALLINT(4),
                genres JSON,
                is_series BOOL,
                start_year SMALLINT(4),
                end_year SMALLINT(4),
                num_ep SMALLINT UNSIGNED,
                num_szn TINYINT UNSIGNED,
                country JSON,
                cast JSON,
                plot varchar(6000),
                directors JSON,
                writers JSON,
                PRIMARY KEY (pos)
            ) AUTO_INCREMENT = {st}
            '''.format(tbl=self.tblName, st=self._startPKFrom))
        # img_path OUGHT TO NOT BE IN DB. CAUSE TOO MANY COMMIT TO DB.
        
        return True

    # heres the problem. it involves too much request if we try to get the full
    # details of all the 250 movies at once. 
    # hence we should fetch only small core info of all 250 movies. cardsDictToSql()
    # then update the info later as the cards are clicked.        detailedDictToSql()
    
    def cardsDictToSql(self, cards: list):
        '''put basic movies details to SQL DB'''
        logging.debug('inserting partial imdb details')
        lOfNewDict = []
        titles = self.getTitles()
        for dicts in cards:
            if dicts['title'] in titles:
                continue
            lOfNewDict.append(dicts)

        values = [
            (card['imdbId'], card['title'], card['rating'], card['imgUrl']) for card in lOfNewDict
        ]
        if not values:
            logging.debug('all titles already exists')
            return
        try:
            self.cur.executemany('''INSERT INTO {}
                                        (imdb_id, title, rating, img_url)
                                    VALUES
                                        (%s, %s, %s, %s)
                                '''.format(self.tblName), values)
            return True
        except mysql.connector.Error as e:
            logging.error('%s\n%s', e, traceback.format_exc())
            return False

    def detailedDictToSql(self, dtls):
        '''put full movie details to SQL DB. movieId should already exists'''
        logging.debug('inserting full remaining imdb details')
        for js in self.haveList:
            val = dtls[js]
            if isinstance(val, list):
                dtls[js] = json.dumps(val)
        titles = self.getTitles()
        if dtls['title'] in titles: return False
        # if not self.idExists(dtls['imdbId']): return False
        self.cur.execute('''
            UPDATE {}
            SET
                total_rated_by = %s,
                year = %s,
                genres = %s,
                is_series = %s,
                start_year = %s,
                end_year = %s,
                num_ep = %s,
                num_szn = %s,
                country = %s,
                cast = %s,
                plot = %s,
                directors = %s,
                writers = %s
            WHERE
                pos = %s
        '''.format(self.tblName), (
                    dtls['totalRatedBy'],
                    dtls['year'],
                    dtls['genres'],
                    dtls['isSeries'],
                    dtls['start'],
                    dtls['end'],
                    dtls['epNum'],
                    dtls['szNum'],
                    dtls['country'],
                    dtls['cast'],
                    dtls['plot'],
                    dtls['directors'],
                    dtls['writers'],
                    dtls['pos'],
        ))
        return True

    def insertAllCols(self, lstOfDicts: list, updateInstead=None):
        lOfNewDict = []
        # titles = self.getTitles()
        for dicts in lstOfDicts:
            # check if title already exists. if it does. skip for-loop.
            # if dicts['title'] in titles:
            #     continue

            tempDict = {**dicts}
            for elem in self.haveList:
                val = dicts[elem]
                if isinstance(val, list):
                    tempDict[elem] = json.dumps(val)
            lOfNewDict.append(tempDict)

        values = []
        for movDict in lOfNewDict:
            values.append(
                (movDict['imdbId'], movDict['imgUrl'], movDict['title'],
                movDict['rating'], movDict['totalRatedBy'], movDict['year'],
                movDict['genres'], movDict['isSeries'], movDict['start'],
                movDict['end'], movDict['epNum'], movDict['szNum'],
                movDict['country'], movDict['cast'], movDict['plot'],
                movDict['directors'], movDict['writers'])
            )
        if not values:
            logging.debug('all titles already exists')
            return
        # print(values)
        # REMEMBER INSERT IS SUPPOSED TO EXECUTEMANY so that it can insert
        # multiple values at once, with update it seems to be complex
        if updateInstead:
            self.cur.execute('''
                UPDATE {}
                SET
                    imdb_id = %s,
                    img_url = %s,
                    title = %s,
                    rating = %s,
                    total_rated_by = %s,
                    year = %s,
                    genres = %s,
                    is_series = %s,
                    start_year = %s,
                    end_year = %s,
                    num_ep = %s,
                    num_szn = %s,
                    country = %s,
                    cast = %s,
                    plot = %s,
                    directors = %s,
                    writers = %s
                WHERE
                    title = %s
            '''.format(self.tblName), values[0] + (movDict['title'], ))
            logging.debug('updating user movie instead of inserting')
        else:  
            self.cur.executemany('''
                INSERT INTO {}
                    (imdb_id, img_url, title, rating, total_rated_by, year, genres,
                        is_series, start_year, end_year, num_ep, num_szn, country,
                        cast, plot, directors, writers)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''.format(self.tblName), values)
            logging.debug('inserting user movie')

    def get(self, qry, values=None):
        logging.debug('fetching data from SQL..')
        self.cur.execute(qry, values)
        return self.cur.fetchall()

    def getPage(self, page: int, interval=10) -> list:
        if (page - 1) < 0: return []
        starting = int(page - 1) * interval
        if self.numOfRows() < 1: return []
        # keys = ['pos', 'imdbId', 'imgUrl', 'title', 'rating', 'totalRatedBy',
        #         'year', 'genres', 'isSeries', 'start', 'end', 'epNum', 'szNum', 
        #         'country', 'cast', 'plot', 'directors', 'writers',]
        rows = self.get('''
                    SELECT
                        pos, img_url, title, rating
                    FROM
                        {tbl}
                    ORDER BY
                        pos ASC
                    LIMIT %s OFFSET %s
            '''.format(tbl=self.tblName), values=(interval, starting))

        lst = []
        for row in rows:
            data = {}
            for i, elem in enumerate(('pos', 'imgUrl', 'title', 'rating')):
                data[elem] = row[i]
            lst.append(data)

        return lst
    
    """
    def getPage(self, page: int, interval=10) -> list:
        if (page - 1) < 0: return []
        starting = int(page - 1) * interval
        if self.numOfRows() < 1: return []
        rows = self.get('''
                    SELECT
                        *
                    FROM
                        {tbl}
                    ORDER BY
                        pos ASC
                    LIMIT %s OFFSET %s
            '''.format(tbl=self.tblName), values=(interval, starting))

        lst = []
        for row in rows:
            data = {}
            for i, elem in enumerate(self.keys):
                val = row[i]
                # these column contain JSON type. hence have to be converted.
                if elem in self.haveList:
                    if val is not None: # json can have just null (aka None)
                        val = json.loads(val)
                data[elem] = val
            lst.append(data)

        return lst
    """
    
    def dictFromId(self, movId):
        d = self._dictFrom(movId=movId)
        if d:
            return d[0]
        return None

    def dictFromTitle(self, title):
        d = self._dictFrom(movTitle=title)
        if d:
            return d[0]
        return None

    def _dictFrom(self, movId=None, movTitle=None):
        '''returns list of dict from sql'''
        if movId:
            colName = 'pos'
            colVal = movId
        if movTitle:
            colName = 'title'
            colVal = movTitle
        rows = self.get('''
                SELECT
                    *
                FROM
                    {tbl}
                WHERE
                    {col} = %s
            '''.format(tbl=self.tblName, col=colName), tuple([colVal]))

        lst = []
        for row in rows:
            data = {}
            for i, elem in enumerate(self.keys):
                val = row[i]
                # these column contain JSON type. hence have to be converted.
                if elem in self.haveList:
                    if val is not None: # json can have just null (aka None)
                        val = json.loads(val)
                data[elem] = val
            lst.append(data)

        return lst

    def idExists(self, movId):
        rows = self.get('''
                SELECT
                    pos
                FROM
                    {}
                WHERE
                    pos = %s
            '''.format(self.tblName), tuple([movId]))
        return bool(rows)

    def titleExists(self, title):
        rows = self.get('''
                SELECT
                    title
                FROM
                    {}
                WHERE
                    title = %s
            '''.format(self.tblName), tuple([title]))
        return bool(rows)

    def getTitles(self) -> list:
        '''returns list of (titles only) from the sql db table'''
        rows = self.get('''
                SELECT
                    title
                FROM
                    {}
                ORDER BY
                    pos DESC
            '''.format(self.tblName), values=None)
        titles = []
        for row in rows:
            titles.append(row[0])
        return titles

    def containing(self, colName, searchExpr, useRegex=False):
        if useRegex:
            rows = self.get('''
                    SELECT
                        title, rating
                    FROM
                        {}
                    WHERE
                        REGEXP_LIKE({}, '{}')
                '''.format(self.tblName, colName, searchExpr), values=None)
        else:
            rows = self.get('''
                    SELECT
                        title, rating
                    FROM
                        {}
                    WHERE
                        {} LIKE %s
                '''.format(self.tblName, colName), values=(searchExpr, ))

        return rows

    def getBasicInfo(self, limit=50):
        rows = self.get('''
                    SELECT
                        title, rating
                    FROM
                        {}
                    ORDER BY
                        pos DESC
                    LIMIT %s OFFSET 0
        '''.format(self.tblName), values=(limit, ))
        return rows

    def fullMovInfoRegex(self, colName, searchExpr, page=1, limit=10, useRegex=True):
        interval = 10
        if (page - 1) < 0: return []
        starting = int(page - 1) * interval
        rows = self.get('''
                    SELECT
                        *
                    FROM
                        {}
                    WHERE
                        REGEXP_LIKE({}, '{}')
                    LIMIT %s OFFSET %s
        '''.format(self.tblName, colName, searchExpr), values=(limit, starting))

        lst = []
        for row in rows:
            data = {}
            for i, elem in enumerate(self.keys):
                val = row[i]
                # these column contain JSON type. hence have to be converted.
                if elem in self.haveList:
                    if val is not None: # json can have just null (aka None)
                        val = json.loads(val)
                data[elem] = val
            lst.append(data)

        return lst

    def numOfRows(self):
        rows = self.get('''
                SELECT
                    count(pos)
                FROM
                    {}
            '''.format(self.tblName), values=None)
        if rows: return rows[0][0]
        else: return 0

    def removeMovie(self, title):
        # if not self.titleExists(title):
        #     return None
        rows = self.cur.execute('''
                DELETE FROM
                    {}
                WHERE
                    title = %s
            '''.format(self.tblName), (title, ))

        logging.debug('deleted rows are %s', rows)

    @staticmethod
    def changeToStr(lstOfDicts):
        lst = []
        for d in lstOfDicts:
            strsDict = {}
            for k, v in d.items():
                if v is None:
                    strsDict[k] = ''
                    continue
                strsDict[k] = v
            lst.append(strsDict)

        return lst



class CredsDb:
    
    def __enter__(self):
        # return self instead of self.conn or self.cur to allow methods to be called
        return self

    def __exit__(self, excType, excValue, excTraceback):
        self.conn.commit()
        self.cur.close()
        self.conn.close()
        # if excType is not None:
        #     print(excType)
        #     print(excValue)
        #     print(excTraceback)
        # return True # supress exceptions

    def __init__(self, tblName: str, startPKFrom: int = 0):
        '''
        Initialize connection and create db and table
        '''
        logging.debug('connecting to mysql')
        self.dbName = 'movie_app_database'
        self._startPKFrom = startPKFrom
        self.tblName = tblName
        self.conn = mysql.connector.connect(**CONFIG)
        self.cur = self.conn.cursor()
        self._createDatabase()
        self._createTable()

    def _createDatabase(self):
        logging.debug('creating database %s if it doesnt exists', self.dbName)
        self.cur.execute('CREATE DATABASE IF NOT EXISTS `{}`'.format(self.dbName))
        self.conn.database = self.dbName
        return True
        
    def _createTable(self):
        logging.debug('creating table %s', self.tblName)
        # inject here...
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS `{tbl}` (
                p_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                is_admin BOOL,
                username varchar(200) UNIQUE,
                first_name varchar(100),
                last_name varchar(100),
                email varchar(100),
                pswd char(128),
                gender varchar(50),
                PRIMARY KEY(p_id)
            ) AUTO_INCREMENT = {st}
            '''.format(tbl=self.tblName, st=self._startPKFrom))
        
        return True

    def get(self, qry, values=None):
        logging.debug('fetching data from SQL..')
        self.cur.execute(qry, values)
        return self.cur.fetchall()

    def user_exists(self, username):
        """used during user signup"""
        rows = self.get('''
                    SELECT
                        *
                    FROM
                        {}
                    WHERE
                        username = %s
                '''.format(self.tblName), (username, ))
        # fetch_all returns an empty list if no row.
        return True if rows else False

    def usernames(self):
        rows = self.get('''
                SELECT
                    username
                FROM
                    {}
                WHERE
                    is_admin != 1
            '''.format(self.tblName))
        return [user[0] for user in rows]

    def is_admin(self, username):
        """used to perform deletion from database"""
        # if not self.user_exists(username): return False
        rows = self.get('''
                    SELECT
                        p_id
                    FROM
                        {}
                    WHERE
                        username = %s and is_admin = 1
                '''.format(self.tblName), values=(username, ))
        
        return True if rows else False

    def removeUser(self, username):
        if username not in self.usernames(): return
        self.cur.execute('''
                DELETE FROM
                    {}
                WHERE
                    username = %s and is_admin != 1
            '''.format(self.tblName), (username, ))
        return True

    def changePswd(self, username, oldPswd, newPswd):
        if not self.returnPersonInfo(username, oldPswd): return None
        saltedHash = bcrypt.hashpw(newPswd.encode('utf-8'), bcrypt.gensalt(rounds=12))
        return self.cur.execute('''
                UPDATE
                    {}
                SET
                    pswd = %s
                WHERE
                    username = %s
            '''.format(self.tblName), (saltedHash, username))


    def changeUserStatus(self, username):
        return self.cur.execute('''
                UPDATE
                    {}
                SET
                    is_admin = 1
                WHERE
                    username = %s
            '''.format(self.tblName), (username, ))

    def returnPersonInfo(self, username, unHashedPswd):
        rows = self.get('''
                    SELECT
                        p_id, is_admin, username, first_name, last_name, email, pswd, gender
                    FROM
                        {}
                    WHERE
                        username = %s
                '''.format(self.tblName), (username, ))
        if rows:
            row = rows[0]
            if not bcrypt.checkpw(unHashedPswd.encode('utf-8'), row[6].encode('utf-8')):
                return None
            return {
                'pId': row[0],
                'isAdmin': row[1],
                'username': row[2],
                'firstName': row[3],
                'lastName': row[4],
                'email': row[5],
                'gender': row[7],
            }
        return None

    def signupPerson(self, info: dict):
        saltedHash = bcrypt.hashpw(info['pswd'].encode('utf-8'), bcrypt.gensalt(rounds=12))
        self.cur.execute('''
            INSERT INTO {}
                (is_admin, username, first_name, last_name, email, pswd, gender)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s)
        '''.format(self.tblName), (
                    info['isAdmin'],
                    info['username'],
                    info['firstName'],
                    info['lastName'],
                    info['email'],
                    saltedHash,
                    info['gender'],
        ))
        return True


CONFIG = {
            'host': 'localhost',
            'user': 'root',
            'password': 'toor',
            'port': 3306
        }

if __name__ == '__main__':
    # from pprint import pprint
    # with CredsDb('creds_user_and_admin') as db:
    #     # print(db.is_admin('zz7'))
    #     # print(db.user_exists('zz'))
    #     print(db.returnPersonInfo('wrongusername', 'wrongpassword'))
    #     print(db.returnPersonInfo('myusername', 'wrongpassword'))
    #     print(db.returnPersonInfo('wrongusername', 'mypassword'))
    #     print(db.returnPersonInfo('myusername', 'mypassword'))
        # print(db.usernames())
        # print(db.removeUser('admin1'))
        # print(db.removeUser('user1'))
        # print(db.removeUser('user333'))
        # print(db.changeUserStatus('user222'))
        # print(db.changePswd('admin2', 'nisanthapa02@gmail.com', 'haha'))
        # print('admin2 password matches: ', db.returnPersonInfo('admin2', 'haha'))
        # print(db.changePswd('kells', 'qwertyuiop[]\\', 'haha'))
        # print(db.changePswd('kells', 'haha', 'qwertyuiop[]\\'))
        # print('kells password matches: ', db.returnPersonInfo('kells', 'haha'))
        # print('kells password matches: ', db.returnPersonInfo('kells', 'qwertyuiop[]\\'))
    
    # with AppDb(tblName='user_added_movs', startPKFrom=100000000) as db:
        # r = db.containing(colName='title', searchExpr='ffffff'+'%')
        # r = db.containing(colName='title', searchExpr='f'+'.*', useRegex=True)
        # print(r)

    with AppDb(tblName='imdb250') as db:
        print(db.dictFromTitle('the shawshank redemption'))

    '''
    db = AppDb('testing`; USE `testing`; SELECT * FROM table_1;--')
    with AppDb(tblName='imdb250') as db:
        imid = 'tt012345640'
        pos = 10
        db.cardsDictToSql([{
            'imdbId': imid,
            'title': 'Pee-pee-poo-poo',
            'rating': 9.9,
            'imgUrl': 'https://goo-goo-gaa-gaa.com'}])
        y=db.detailedDictToSql({
            'imdbId': imid,
            'totalRatedBy': 42069,
            'year': 2010,
            'genres': json.dumps([]),
            'isSeries': 1,
            'start': 2011,
            'end': 2012,
            'epNum': 55,
            'szNum': 21,
            'country': 'JP',
            'cast': json.dumps(['jackie chan', 'terry crew']),
            'plot': 'brrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr',
            'directors': json.dumps(['chris nolan']),
            'writers': json.dumps([]),
            'pos': pos
        })
        # print(y)
        # print(db.get('SELECT * FROM imdb250'))
        # print(db.dictFromId(pos))
        # print(db.idExists(pos))
        # print(db.numOfRows())
    '''
    # with AppDb(tblName='imdb250') as db:
    #     pprint(db.getPage(page=2, interval=9), sort_dicts=False)
    # with AppDb(tblName='imdb250') as db:
    #     with open('20mov.json') as f:
    #         db.insertAllCols(json.loads(f.read()))








