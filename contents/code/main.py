from PyKDE4 import plasmascript
from PyKDE4.plasma import Plasma
from PyKDE4.kdeui import KIcon, KMessageBox
import fnmatch
import os
from subprocess import call
from subprocess import check_output

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
        for root, dirnames, filenames in os.walk('/home/michael/.password-store/'):
            for filename in fnmatch.filter(filenames,'*.gpg'):
                matches.append(os.path.join(root,filename))

        keys = [ s for s in matches if str(q) in s ]

        limit = 0
        for i in keys:
            limit += 1
            if limit > 16:
                break
            pw=str(i).replace('/home/michael/.password-store/','').replace('.gpg','')
            m.setData(pw)
            m.setText("Copy password from: '%s'" % pw )
            context.addMatch(i,m)
        

    def run(self, context, match):
        # called by KRunner when the user selects our action,        
        # so lets keep our promise

        #KMessageBox.messageBox(None, KMessageBox.Information, match.data().toString())
        msg=check_output(["pass","-c","%s" % str(match.data().toString())])


def CreateRunner(parent):
    # called by krunner, must simply return an instance of the runner object
    return MsgBoxRunner(parent)
