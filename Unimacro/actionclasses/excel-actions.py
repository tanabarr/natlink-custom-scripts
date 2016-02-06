import win32com.client
import time, os, os.path
from pythoncom import com_error
from actionbases import AllActions
import natlinkutilsqh as natqh


class ExcelActions(AllActions):
    """attach to excel and perform necessary actions
    """
    appList = [] # here goes, for all instances, the excel application object
    positions = {} # dict with book/sheet/(col, row) (tuple)
    rows = {} # dict with book/sheet/row  (str)
    columns = {} # dict with book/sheet/col (str)
    def __init__(self, progInfo):
        AllActions.__init__(self, progInfo)
        self.app = self.connect()
        if not self.app:
            return
        self.prevBook = self.prevSheet = self.prevPosition = None
        self.update(progInfo)

    def update(self, progInfo):
        if self.app:
            self.checkForChanges(progInfo)
        else:
            print 'no valid excel instance available'
        
    def isInForeground(self, app=None, title=None, progInfo=None):
        """return True if app is in foreground
        """
        thisApp = app or self.app
        title = title or self.topTitle
        if not thisApp:
            return
        name = thisApp.ActiveWorkbook.Name
        #print 'activeworkbook: %s'% name
        if not name:
            print 'excel-actions, cannot find activeworkbook'
            return
        if title == 'microsoft excel':
            print 'cannot check the foreground state, but assume it is ok; please maximise your activeworkbook...'
            return True
        if title.find(name.lower()) >= 0:
            return True
        print 'excel, isInForeground: cannot find name %s in title: %s, probably you have more excel instances open. Unimacro only can connect to one of the instances.'% (name, title)
        
        
    def checkForChanges(self, progInfo=None):
        """return 1 if book, sheet or position has changed since previous call
        """
        progInfo = progInfo or natqh.getProgInfo()
        changed = 0
        if not self.app:
            self.prevBook = self.prevSheet = self.prevPosition = None
            self.progInfo = progInfo
            self.connect()
            if not self.app:
                self.progInfo = progInfo 
                return
        
        title = self.topTitle = progInfo[1]

        if not self.isInForeground(app=self.app, title=title, progInfo=progInfo):
            if self.prevBook:
                changed = 8 # from foreground into background
                self.prevBook = self.prevSheet = self.prevPosition = None
            self.book = self.sheet = self.Position = None
            self.currentRow = self.currentLine = None
            self.currentColumn = None
            self.progInfo = progInfo
            return


        self.book = self.app.ActiveWorkbook
        
        if self.book is None:
            print 'ExcelAction, no active workbook'
            self.bookName = ''
            self.sheetName = ''
            self.sheet = None
        else:
            self.bookName = str(self.book.Name)
            self.sheet = self.app.ActiveSheet
            self.sheetName = str(self.sheet.Name)
        if self.prevBook != self.bookName:
            self.prevBook = self.bookName
            changed += 4
        if self.prevSheet != self.sheetName:
            self.prevSheet = self.sheetName
            changed += 2
        if changed:
            print 'excel-actions: update book and/or sheet variables'
            self.positions.setdefault(self.bookName,{})
            self.positions[self.bookName].setdefault(self.sheetName, [])
            self.columns.setdefault(self.bookName,{})
            self.columns[self.bookName].setdefault(self.sheetName, [])
            self.rows.setdefault(self.bookName,{})
            self.rows[self.bookName].setdefault(self.sheetName, [])
            self.currentPositions = self.positions[self.bookName][self.sheetName]
            self.currentColumns = self.columns[self.bookName][self.sheetName]
            self.currentRows = self.rows[self.bookName][self.sheetName]
        if self.sheet:
            #print 'excel-actions: %s, update current position'% self.sheet

            cr = self.savePosition()
            self.currentPosition = cr
            self.currentRow = self.currentLine = cr[1]
            self.currentColumn = cr[0]
            #print 'currentColumn: %s, currentRow: %s, currentLine: %s'% (self.currentColumn, self.currentRow, self.currentLine)
            if cr != self.prevPosition:
                self.prevPosition = cr
                changed += 1
            #else:
            #    print 'same position: %s'% repr(cr)
        else:
            print 'excel-actions, no self.sheet.'
        #print 'return code checkForChanges: %s'% changed
        return changed
    
    #connect to programs:
    def connect(self):
        """connect to excel and leave app"""
        print 'Connecting to to excel...'
        if self.prog != 'excel':
            print "excel-actions, should only be called when excel is the foreground window, not: %s"% self.prog
            return
        title = self.topTitle
        if self.appList:
            if len(self.appList):
                print 'ExcelAction, more excel apps active: %s, take first instance'% len(self.appList)
            for app in self.appList:
                if self.isInForeground(app):
                    return app
            else:
                print 'cannot find excel instance for this foreground window'
                return
                print 'did not have the active excel instances in the foreground, try by filename'
        # if here, get foreground process:
        app = win32com.client.GetActiveObject(Class="Excel.Application")
        self.appList.append(app)
        if self.isInForeground(app):
            return app
        else:
            print 'cannot attach to Excel, app not in foreground, trick with recentFiles does not work (yet??)'
            return
            booksInApp = self.getBooksList(app=app)
            print 'not in foreground? Currentbooks: %s'% booksInApp
            recentList = app.RecentFiles
            for recent in recentList:
                recentPath = str(recent.Path)
                print 'recent: %s'% recentPath
                if self.recentMatchesTitle(recentPath, self.topTitle):
                    print 'recentPath: %s (type: %s typename: %s)'% (recentPath, type(recentPath), type(recent.Name))
                    app = win32com.client.GetActiveObject(recentPath)
                    print 'app from file: %s'% app
                    self.appList.append(app)
                    return app
            else:
                print 'cannot get access to Excel instance which owns the foreground window...'
                return

####oleAccDll = ctypes.oledll.oleacc
####AccessibleObjectFromWindow = oleAccDll.AccessibleObjectFromWindow
####IID_IAccessible = ctypes.c_int.in_dll(oleAccDll, "IID_IAccessible")
####OBJID_WINDOW = 0
####
##### you could also say: IID_IAccessible = ctypes.com.GUID( "{618736E0-3C3D-11CF-810C-00AA00389B71}" )
####
####
####def callback(hwnd, extra):
####  acc = ctypes.c_int()
####  hr = AccessibleObjectFromWindow(hwnd, OBJID_WINDOW, ctypes.byref(IID_IAccessible), ctypes.pointer(acc))
####  print("hr is %s, acc is %x" % (hr, acc))
####
####win32gui.EnumWindows(callback, None)

# you could also say: IID_IAccessible = ctypes.com.GUID( "{618736E0-3C3D-11CF-810C-00AA00389B71}" )
        
        if title:
            # connect to instance with book from window title:
            try:
                bookName = self.getBookNameFromTitle(title)
                app = win32com.client.GetObject(bookName).Application
            except com_error:
                print 'cannot get excel application with bookName: %s'% bookName
                return
        else:
            # connect to running instance:
            try:
                app = win32com.client.GetObject(Class="Excel.Application")
            except com_error:
                print 'no excel instance active on this computer...'
                return
        ##app = win32com.client.gencache.EnsureDispatch('Excel.Application')
        #print 'app: %s'% repr(app)
        #self.appList.append(app)
        #if title:
        #    bookName = self.getBookFromTitle(title, app=app)
        #    print 'title: %s, bookName: %s'% (title, bookName)
        #
        #if app.Workbooks.Count and not app.Visible:
        #    app.Visible = True
        return app

    def recentMatchesTitle(self, recentFile, windowTitle):
        """check the recent file with the current window title
        """
        p, name = os.path.split(recentFile)
        if windowTitle.find(name) >= 0:
            return True
        

    def disconnect(self):
        """disconnect from excel
        
        by removing the connecting 
        """
        # previous connection was not valid anymore, so remove old list and go for a new connection
        if self.app:
            if self.app.Workbooks.Count == 0:
                self.app.Quit()
            if len(self.appList) > 1:
                print 'ExcelAction, more excel apps active: %s'% len(self.appList)
            while self.appList:
                pop = self.appList.pop()
                del pop

    def savePosition(self):
        """save current position in positions dict
        
        returns the current (col, row) tuple
        """
        cr = self.getCurrentPosition()
        c, r = cr
        self.pushToListIfDifferent(self.currentPositions, cr)
        self.pushToListIfDifferent(self.currentRows, r)
        self.pushToListIfDifferent(self.currentColumns, c)
        
        return cr
    
    def getBookFromTitle(self, title, app=None):
        """return the book name corresponding with title (being the window title)
        """
        bookList = self.getBooksList(app=app)
        if bookList:
            for b in bookList:
                if title.find(b) >= 0:
                    print 'found book in instance: %s'% b
                    return b
        print 'not found title in instance, bookList: %s'% bookList

    def getBookNameFromTitle(self, title):
        """return the book name corresponding with title (being the window title)
        """
        excelTexts = ['Microsoft Excel -', '- Microsoft Excel']
        print 'getBookNameFromTitle: %s'% title
        if title.find('['):
            title = title.split('[')[0].strip()
        for e in excelTexts:
            if title.find(e) >= 0:
                title = title.replace(e, '').strip()
        print 'result: %s'% title
        return title
            
        
    
    def getBooksList(self,app=None):
        """get list of strings, the names of the open workbooks
        """
        app = app or self.app
        if app:
            books = []
            for i in range(app.Workbooks.Count):
                b = app.Workbooks(i+1)
                books.append(str(b.Name))
            return books
        return []

    def getCurrentLineNumber(self, handle=None):
        if not self.app: return
        lineStr = self.getCurrentPosition()[1]
        return int(lineStr)
    
    
    def getSheetsList(self, book=None):
        """get list of strings, the names of the open workbooks
        """
        if book is None:
            book = self.book
        elif isinstance(book, basestring):
            book = self.app.Workbooks[book]
        
        if book:
            sheets = []
            for i in range(book.Sheets.Count):
                s = self.app.Worksheets(i+1)
                sheets.append(str(s.Name))
            return sheets

    
    def selectSheet(self, sheet):
        """select the sheet by name of number
        """
        self.app.Sheets(sheet).Activate()
    
    def getCurrentPosition(self):
        """return row and col of activecell
        
        as a side effect remember the (changed position)
        """
        if not (self.app and self.book and self.sheet):
            return None, None
        ac = self.app.ActiveCell
        comingFrom = ac.Address
        #print 'activecell: %s'% comingFrom
        cr = [str(value).lower() for value in comingFrom.split("$") if value]
        if len(cr) == 2:
            #print 'currentposition, lencr: %s, cr: %s'% (len(cr), cr)
            return tuple(cr)
        else:
            print 'excel-actions, no currentposition, lencr: %s, cr: %s'% (len(cr), cr)
            return None, None

    def pushToListIfDifferent(self, List, value):
        """add to list (in place) of value differs from last value in list
        
        for positions, value is (c,r) tuple
        """
        if not value:
            return
        if List and List[-1] == value:
            return
        List.append(value)
    
    def getPreviousRow(self):
        """return the previous row number
        """
        cr = self.getCurrentPosition()
        c, r = cr
        while 1:
            newr = self.popFromList(self.currentRows)
            if newr is None:
                return
            if r != newr:
                return newr

    def getPreviousColumn(self):
        """return the previous col letter
        """
        cr = self.getCurrentPosition()
        c, r = cr
        while 1:
            newc = self.popFromList(self.currentColumns)
            if newc is None:
                return
            if c != newc:
                return newc
    
    def popFromList(self, List):
        """pop from list a different value than currentValue
        
        and return None if List is exhausted
        """
        if List:
            value = List.pop()
            return value


    # functions that do an action from the action.py module, in case of excel:
    # one parameter should be given    
    def metaaction_gotoline(self, rowNum):
        """overrule for gotoline meta-action
        
        goto line in the current column
        """
        rowNum = str(rowNum)
        if not self.app:  return
        cPrev, rPrev = self.getCurrentPosition()
        if rowNum == rPrev:
            print 'row already selected'
            return 1
        try:
            range = cPrev + rowNum
            #print 'current range: %s, %s'% (rPrev, cPrev)
            sheet = self.app.ActiveSheet
            #print 'app: %s, sheet: %s (%s), range: %s'% (app, sheet, sheet.Name, range)
            sheet.Range(range).Select()
            return 1
        except:
            print 'something wrong in excel-actions, metaaction_gotoline.'
            return
            
    def metaaction_selectline(self, dummy=None):
        """select the current line
        """
        if not self.app: return
        self.app.ActiveCell.EntireRow.Select()
        return 1

    def metaaction_remove(self, dummy=None):
        """remove the selection, assume rows or columns are selecte
        """
        if not self.app: return
        self.app.Selection.Delete()

        return 1
        
    def metaaction_insert(self, dummy=None):
        """insert the number of lines that are selected
        """
        if not self.app: return
        self.app.Selection.Insert()

        return 1

    metaaction_lineinsert = metaaction_insert

    def metaaction_pasteinsert(self, dummy=None):
        """insert the number of lines that are selected
        """
        if not self.app: return
        self.app.Selection.Insert()
        self.app.CutCopyMode = False

        return 1

    def metaaction_selectpreviousline(self, dummy=None):
        """select the previous line with respect to the activecell
        """
        if not self.app: return
        wantedLine = int(self.currentRow) - 1
        self.metaaction_gotoline(wantedLine)
        self.app.ActiveCell.EntireRow.Select()
        return 1

    def metaaction_movetotopofselection(self, dummy=None):
        """select first line of a selected range
        """
        if not self.app: return
        self.app.Selection.Rows(1).Select()
        return 1

    def metaaction_movetobottomofselection(self, dummy=None):
        """select first line of a selected range
        """
        if not self.app: return
        nRows = self.app.Selection.Rows.Count
        self.app.Selection.Rows(nRows).Select()
        return 1
    def metaaction_movecopypaste(self, dummy=None):
        """insert the clipboard after a movecopy action.
        """
        if not self.app: return
        self.app.ActiveCell.EntireRow.Insert()
        self.app.CutCopyMode = False
        return 1
        
    def metaaction_lineback(self, dummy=None):
        """goes back to the previous row
        """
        if not self.app: return
        #self.app.ActiveCell.EntireRow.Select()
        prevRow = self.getPreviousRow()
        print 'prevRow: %s'% prevRow
        if prevRow:                
            self.gotoRow(prevRow)
        return 1
        
if __name__ == '__main__':
    progInfo = ('excel', 'Microsoft Excel - footprintdata_2010_qh.xls', 'top', 396140)
    excel = ExcelActions(progInfo)
    if excel.app:
        #excel.app.Visible = True
        print 'activeCell: %s'% excel.app.ActiveCell
        print 'books: %s'% excel.app.Workbooks.Count
        print 'foreground: %s'%excel.isInForeground()
        print 'now click on excel please'
        excel.metaaction_gotoline(345)
        time.sleep(5)
