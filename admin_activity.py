import configs
import user_activity
from sql_db.sql_connector import CredsDb

class AdminLogin(user_activity.UserLogin):

    def __init__(self, *args, **kwargs):
        user_activity.UserLogin.__init__(self)
        

    def goBack(self):
        import admin_win
        configs.ShowFrame(admin_win.AdminWin)

    def done(self):
        with CredsDb(tblName=configs.CREDSTABLE) as db:
            userInfo = db.returnPersonInfo(self.username.get(), self.pswdEnt.get())
            if not userInfo:
                self.showErr('Username or Password does not match')
                return

            configs.CURRLOGGEDIN = userInfo['username']
            # to get new value of CURRLOGGEDIN import configs again.
            configs.ISADMIN = True
        import admin_control
        configs.ShowFrame(admin_control.Control)

