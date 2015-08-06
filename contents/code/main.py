from PyKDE4 import plasmascript
from PyKDE4.plasma import Plasma
from PyKDE4.kdeui import KIcon, KMessageBox
import fnmatch
import os
import dbus
from subprocess import call

PASSWORD_STORE=os.path.expanduser("~/.password-store/")

# notify function -> this is a python/dbus notify version
# maybe switch to a proper kde notify version, since
# this is for kde only anyway
def notify(summary, body='', app_name='', app_icon='', timeout=5000, actions=[], hints=[], replaces_id=0):
    _bus_name = 'org.freedesktop.Notifications'
    _object_path = '/org/freedesktop/Notifications'
    _interface_name = _bus_name

    session_bus = dbus.SessionBus()
    obj = session_bus.get_object(_bus_name, _object_path)
    interface = dbus.Interface(obj, _interface_name)
    interface.Notify(app_name, replaces_id, app_icon,
    summary, body, actions, hints, timeout)


class MsgBoxRunner(plasmascript.Runner):

    def init(self):
        # called upon creation to let us run any intialization
        # tell the user how to use this runner
        self.addSyntax(Plasma.RunnerSyntax("gp :q:", "get password from :q: and store it in clipboard"))

    def match(self, context):
        # called by krunner to let us add actions for the user
        if not context.isValid():
            return

        q = context.query()

        # look for our keyword 'msg'
        if not q.startsWith("gp "):
             return

        # ignore less than 1 characters (in addition to the keyword)
        if q.length() < 4:
            return

        # strip the keyword and leading space
        q = q[2:]
        q = q.trimmed()

        # now create an action for the user, and send it to krunner
        m = Plasma.QueryMatch(self.runner)
        m.setType(Plasma.QueryMatch.ExactMatch)
        m.setIcon(KIcon("security"))


        matches = []
        for root, dirnames, filenames in os.walk(PASSWORD_STORE):
            for filename in fnmatch.filter(filenames,'*.gpg'):
                matches.append(os.path.join(root,filename))

        keys = [ s for s in matches if str(q) in s ]

        limit = 0
        for i in keys:
            limit += 1
            # only show the first 15 matches
            if limit > 15:
                break
            pw=str(i).replace(PASSWORD_STORE,'').replace('.gpg','')
            m.setData(pw)
            m.setText("Copy password from: '%s'" % pw )
            context.addMatch(i,m)

    def run(self, context, match):
        # called by KRunner when the user selects our action,
        # so lets keep our promise

        # get return code of pass (somehow check_output with pass -c kills krunner)
        rc=call(["pass","-c","%s" % str(match.data().toString())])
        # 0 = means password was correct
        if rc == 0:
            # text is basically the same like what pass outputs
            notify(summary="pass", app_icon="dialog-information", body="Copied %s to clipboard. Will clear in 45 seconds." % str(match.data().toString()))
        else:
            notify(summary="pass", app_icon="dialog-warning",  body="gpg: decryption failed: No secret key")

def CreateRunner(parent):
    # called by krunner, must simply return an instance of the runner object
    return MsgBoxRunner(parent)
