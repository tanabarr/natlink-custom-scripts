# actions classes for specific programs, base classes first:
import messagefunctions as mf

class AllActions(object):
    def __init__(self, progInfo):
        self.prog, self.topTitle, self.topOrChild, self.topHandle = progInfo
        self.progInfo = None # for update purposes
        
    def update(self, newProgInfo):
        if newProgInfo == self.progInfo:
            return
        print 'allactions: new prog info, overload for your specific program: %s'% self.prog
        self.progInfo = newProgInfo
        
    def getCurrentLineNumber(self):
        pass
    
# base actions for applications that are connected through Windows Messages Functions
class MessageActions(AllActions):
    def __init__(self, progInfo):
        AllActions.__init__(self, progInfo)
        self.classname = None   #  Scintilla can be handled quite generically with setting this variable
        self.prevTabName = None
        self.update(progInfo)

    def update(self, progInfo):
        """if prog info changes, then probably only title changes so notice and do nothing
        """
        if progInfo == self.progInfo:
            return 1 # OK
        self.handle = self.getInnerHandle(self.topHandle)
        if not self.handle:
            if progInfo and progInfo[2] == 'top':
                print 'no handle found for (top) edit control for program: %s'% self.prog
            return
        self.progInfo = progInfo
        print 'updated program info: %s, edit control handle: %s'% (repr(self.progInfo), self.handle) 
        return self.handle  # None if no valid handle        

    def getCurrentLineNumber(self, handle=None):
        handle = handle or self.handle
        if not handle: return
        linenumber = mf.getLineNumber(handle, classname=self.classname)  # charpos = -1
        return linenumber

    def getNumberOfLines(self, handle=None):
        handle = handle or self.handle
        if not handle: return
        nl = mf.getNumberOfLines(handle, classname=self.classname)  
        return nl
    
    def isVisible(self, handle=None):
        handle = handle or self.handle
        if not handle: return
        return mf.isVisible(handle, classname=self.classname)