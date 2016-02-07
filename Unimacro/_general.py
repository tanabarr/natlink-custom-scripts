__version__ = "$Rev: 538 $ on $Date: 2014-07-22 20:42:39 +0200 (di, 22 jul 2014) $ by $Author: quintijn $"
# This file is part of a SourceForge project called "unimacro" see
# http://unimacro.SourceForge.net and http://qh.antenna.nl/unimacro
# (c) copyright 2003 see http://qh.antenna.nl/unimacro/aboutunimacro.html
#    or the file COPYRIGHT.txt in the natlink\natlink directory 
#
#  _general.PY
#
# written by Quintijn Hoogenboom (QH softwaretraining & advies),
# developed during the past few years.
#


#
"""do a set of general commands, with language versions possible, version 7

a lot of commands from the previous version removed, inserted a search and dictate
mode, that only works when spell mode or command mode is on.


"""
#
#

Counts = range(1,20) + range(20,51,5)

# for taskswitch:
Handles = {}
#systray:
systrayHndle = 0

import string, types, copy, time, pydoc, os, utilsqh, sys, pickle, glob, pprint
import datetime
import natlink
import natlinkmain
import win32api, win32gui
import win32clipboard
import namelist # for name phrases
import nsformat

natut = __import__('natlinkutils')
natqh = __import__('natlinkutilsqh')
natbj = __import__('natlinkutilsbj')
from actions import doAction as action
from actions import doKeystroke as keystroke
import actions
# taskswitching moved to _tasks.py (july 2006)

language = natqh.getLanguage()
FORMATS = {
    # for letters (do nothing):
    'no spacing': (natqh.wf_NoSpaceFollowingThisWord | natqh.wf_NoSpacePreceedingThisWord |
                   natqh.wf_TurnOffSpacingBetweenWords |
                      natqh.wf_DoNotApplyFormattingToThisWord
          ),
    # normal words:
    'normal words': ( natqh.wf_RestoreNormalCapitalization |
            natqh.wf_RestoreNormalSpacing
          ),
    # extra space(do one space):
    'extra space':  ( natqh.wf_RestoreNormalCapitalization |
            natqh.wf_RestoreNormalSpacing |
            natqh.wf_AddAnExtraSpaceFollowingThisWord
          ), 
    }
version = natqh.getDNSVersion()
user = natlink.getCurrentUser()[0]
wordsFolder = os.path.split(
            sys.modules[__name__].__dict__['__file__'])[0] + \
            '\\' + language  + "_words" + \
            '\\' + user
utilsqh.createFolderIfNotExistent(wordsFolder)
files = [os.path.splitext(f)[0] for f in os.listdir(wordsFolder)]
## print '_general, files in wordsFolder %s: %s'% (wordsFolder, files)

if language == 'enx':
    nameList = {'Q. H.': 'QH',
                 'R. A.': 'RA',
                'underscore': '',
                 }
elif language == 'nld':
    nameList = {'QH': 'QH',
                 'er aa': 'RA',
                'underscore': '',
                 }
else:
    nameList = {}
        

switchDirection = {
      "{Up}":      "{Down}",
      "{Down}":    "{Up}",
      "{Left}":    "{Right}",
      "{Right}":   "{Left}"}

modes = ['spell', 'command', 'numbers', 'normal', 'dictation', 'dictate']
normalSet = ['test', 'reload', 'info', 'undo', 'redo', 'namephrase', 'batch',
             'comment', 'mousefix', 'documentation', 'modes', 'variable', 'search',
             'highlight',         # for Shane, enable, because Vocola did not fix _anything yet
             'browsewith', 'hyphenatephrase', 'openuser']
#normalSet = ['hyphenatephrase']


commandSet = normalSet[:] + ['dictate']


ancestor=natbj.IniGrammar
class ThisGrammar(ancestor):

    iniIgnoreGrammarLists = ['modes','count', 'namelist']

    number_rules = natbj.numberGrammar[language] #  including millions

    language = natqh.getLanguage()        
    name = "general"
    gramSpec = ["""
<before> = Command | Here;
<dgnletters> imported;
<dgndictation> imported;
<documentation> exported = Make documentation;
<batch> exported = do batch words;
<test> exported = test (pleestring| even testen | abeecee); 
<reload> exported = reload Natlink;
<info> exported = give (user | window |unimacro| path) (info|information) ;
<undo> exported = Undo [That] [{count} [times]];
<redo> exported = Redo [That] [{count} [times]];
<namephrase> exported = Make That [Name] phrase;
<hyphenatephrase> exported = Hyphenate (phrase| last word | last ({n2-5}) words);
<comment> exported = Comment {namelist};
<mousefix> exported = Mouse (Down|Up|Release);
<variable> exported = (Variable| Method) Back [{n1-5}];
<modes> exported = {modes} mode;
<highlight> exported = highlight <dgndictation>;         # for Shane,
<search> exported = search ('go back'|new|
                            ((for|before|after|extend|insert)(<dgndictation>))|
                            ({searchwords}[<dgndictation>])|
                            ((forward|back|up|down) [{count} [times]]));
<browsewith> exported = ('browse with') {browsers};
<openuser> exported = 'open user' {users};

"""]

      

    def initialize(self):
        if self.language:
            self.load(self.gramSpec)
            self.switchOnOrOff() # initialises lists from inifile, and switches on
                             # if all goes well (and variable onOrOff == 1)

            self.setNumbersList('count', Counts)
            self.setList('modes', modes)
##            self.testlist = ['11\\Canon fiftyfive two fifty',
##                    '12\\Canon',
##                    '15\\C. Z. J.',
##                    '19\\Helios fourtyfour M.',
##                    '38\\Vivitar seventy one fifty',
##                    '32\\Contax twentyeight millimeter',
##                    '33\\C. Z. J. one thirtyfive number one',
##                    'Canon 2870',
##                    '09\\Canon 1022',
##                    '31\\Tamron 2875']
##            #self.setList('testlist', self.testlist)
##            self.emptyList('testlist')
            self.activateSet(normalSet)
            self.title = 'Unimacro grammar "'+__name__+'" (language: '+self.language+')'
            self.specialSearchWord = None
            self.specialSearchWords = ['test']
        else:
            print "no valid language in grammar "+__name__+" grammar not initialized"

    def gotBegin(self,moduleInfo):
        if self.checkForChanges:
            self.checkInifile() # refills grammar lists and instance variables
                                # if something changed.
    def gotResults_wrongrule(self,words,fullResults):
        natut.playString("%s\n"% fullResults)

    def gotResultsInit(self,words,fullResults):
        self.fullText = string.join(words)
        self.progName = natqh.getProgName()

        # for Shane
        self.search = self.dictate = self.highlight = 0
        self.text = ''
        self.minimalapp=None
        self.specialSearchWords = None

        if words[0] in ['Hier', 'Here']:
            print 'Here from _general...'
            natut.buttonClick()
            natqh.Wait()
                

        
        
        
    def gotResults_batch(self,words,fullResults):
        
        files = [f[:-4] for f in os.listdir(wordsFolder)]
        if files:
            print 'in folder: %s, files: %s'% (wordsFolder, files)
        else:
            print 'in folder: %s, no files found'% wordsFolder
            return
        
        for f in files:
            F = f + '.txt'
            if f == 'deleted words':
                print 'delete words!'
                for l in open(os.path.join(wordsFolder, F)):
                    w = l.strip()
                    if w.find('\\\\') > 0:
                        w, p = w.split('\\\\')
                    print f, ', word to delete :', w
                    natqh.deleteWordIfNecessary(w)
                continue

            if f in FORMATS:
                formatting = FORMATS[f]
                print 'to formatting for file: %s: %x'% (f, formatting)
            else:
                print 'no formatting information for file: %s'% f
                formatting = 0

            for l in open(os.path.join(wordsFolder, F)):
                p = 0 # possibly user defined properties
                w = l.strip()
                print f, ', word:', w
                if w.find('\\\\') > 0:
                    w, p = w.split('\\\\')
                    exec("p = %s"%p)
##                    pList = natqh.ListOfProperties(p)
##                    for pp in pList:
##                        print pp
                newFormat = p or formatting
                natqh.addWordIfNecessary(w)
                formatOld = natlink.getWordInfo(w)
                if formatOld == newFormat:
                    print 'format already okay: %s (%x)'% (w, newFormat)
                else:
                    natlink.setWordInfo(w, newFormat)
                    print 'format set for %s: %x'% (w, newFormat)

##    def gotResults_datetime(self,words,fullResults):
##        """print copy or playback date, time or date and time
##        """
##        Print = self.hasCommon(words, 'print')
##        Speak = self.hasCommon(words, 'give')
##        Date  = self.hasCommon(words, 'date')
##        Time  = self.hasCommon(words, 'time')
##        if Date and Time:
##            DateTime  = 1
##        result = []
##        if Date:
##            dateformat = "%m/%d/%Y"
##            cdate = datetime.date.today()
##            fdate = cdate.strftime(dateformat)
##            result.append(fdate)
##        if Time:
##            timeformat = "%H:%M"
##            ctime = datetime.datetime.now().time()
##            ftime = ctime.strftime(timeformat)
##            result.append(ftime)
##        if result:
##            result = ' '.join(result)
##        else:
##            print 'no date or time in result'
##            return
##        if Print:
##            keystroke(result)
##        elif Speak:
##            natlink.execScript('TTSPlayString "%s"'% result)

    def gotResults_highlight(self,words,fullResults):
        # for Shane
        self.highlight = 1

    def gotResults_search(self,words,fullResults):
        self.search = 1
        if self.specialSearchWords == None:
            self.specialSearchWords = self.Lists['searchwords']
            print 'specialSearchWords: %s'% self.specialSearchWords

        counts = self.getNumbersFromSpoken(words, Counts)
        if counts:
            self.count = counts[0]
        else:
            self.count = None
        if self.hasCommon(words, ['new', 'nieuw']):
            self.search = 'new'
        elif self.hasCommon(words, ['back', 'up', 'omhoog', 'terug', 'achteruit']):
            self.search = 'back'
        elif self.hasCommon(words, ['forward', 'down', 'vooruit', 'omlaag', 'verder']):
            self.search = 'forward'
        elif self.hasCommon(words, ['go back', 'ga terug']):
            self.search = 'go back'
        elif self.hasCommon(words, ['for', 'naar']):
            self.search = 'for'
        elif self.hasCommon(words, ['before', 'voor']):
            self.search = 'before'
        elif self.hasCommon(words, ['after', 'na']):
            self.search = 'after'
        elif self.hasCommon(words, ['insert', 'invoegen']):
            self.search = 'insert'
        elif self.hasCommon(words, ['extend', 'uitbreiden']):
            self.search = 'extend'

        # provisions for extra special keywords (in front of spelled characters)            
        self.specialSearchWord = self.hasCommon(words, self.specialSearchWords)


    def gotResults_dictate(self,words,fullResults):
        self.dictate = 1

    def gotResults_dgnletters(self,words,fullResults):
        self.text = ''.join(map(natqh.stripSpokenForm, words))
        if self.search:
            # catch some common misrecognitions:
            if self.text == '4':
                print 'caught dgnletters %s, switch to forward search'% self.text
                self.text = ''
                self.search = 2 # forward search
            elif self.text in ['43', '403']:
                print 'caught dgnletters %s, switch to forward search 3'% self.text
                self.text = ''
                self.count = 3
                self.search = 2 # forward search
        
    def gotResults_dgndictation(self,words,fullResults):
        #self.text = ' '.join(map(natqh.stripSpokenForm, words))
        # try with the improved nsformat function 
        self.text = nsformat.formatWords(words, (8,))[0]
        
        if self.search and self.text in ['on', 'verder']:
            self.search = 2
        elif self.search and self.text in ['new', 'nieuw']:
            self.search = 3
        elif self.search and self.text in ['terug', 'back']:
            self.search = 4
        print 'dgndictation: %s'% self.text

    def gotResults_dgnwords(self,words,fullResults):
        print 'dgnwords heard: %s'% words
        return
        t = words[0]
        # catch the special search words first:
        if not self.specialSearchWord:
            self.specialSearchWord = self.hasCommon(t, self.specialSearchWords)
            if self.specialSearchWord:
                print 'caugth special word: %s'% self.specialSearchWord
                return
        if self.search and self.text in ['on', 'verder']:
            self.search = 2
        elif self.search and self.text in ['new', 'nieuw']:
            self.search = 3
        elif self.search and self.text in ['terug', 'back']:
            self.search = 4
        else:
            self.text = t.split('\\')[0]

    def gotResults_browsewith(self,words,fullResults):
        """show page in another browser"""
        m = natlink.getCurrentModule()
        prog, title, topchild = natqh.getProgInfo(modInfo=m)
        Iam2x = prog == '2xexplorer'
        IamExplorer = prog == 'explorer'
        browser = prog in ['iexplore', 'firefox','opera', 'netscp', 'chrome']
        if not browser:
            self.DisplayMessage ('command only for browsers')
            return
        print 'words:', words
        natqh.saveClipboard()
        action('<<addressfield>>; {extend}{shift+exthome}{ctrl+c};<<addressfieldclose>>')
        askedBrowser = self.getFromInifile(words, 'browsers')
        if askedBrowser == prog:
            self.DisplayMessage('command only for another browser')
            return
        print 'try to bring up browser: |%s|'% askedBrowser
        action('RW')
        action('AppBringUp "%s"'% askedBrowser)
        action('WTC')
        action('<<addressfield>>; {ctrl+v}{enter}')
        
        natqh.restoreClipboard()
 
    def gotResults_documentation(self,words,fullResults):
        oldPath = os.getcwd()
        uniGrammars = self.ini.getList('documentation', 'unimacro grammars')
        uniModules = self.ini.getList('documentation', 'unimacro modules')
        otherGrammars = self.ini.getList('documentation', 'other grammars')
        otherModules = self.ini.getList('documentation', 'other modules')
        base = natqh.getUnimacroUserDirectory()
        docPath = os.path.join(base, 'doc')
        pickleFile = os.path.join(docPath, '@unimacro.pickle')
        try:
            psock = open(pickleFile, 'r')
            memory = pickle.load(psock)
            psock.close()
            print '--------------------memory from pickle: %s'% pickleFile
        except:
            memory = {}
            print '--------------------no or invalid pickle file: %s'% pickleFile
            
        utilsqh.createFolderIfNotExistent(docPath)
        os.chdir(docPath)
        self.DisplayMessage('writing documentation to: %s'% docPath)
        pydoc.writedocs(base)
        self.DisplayMessage('checking unimacro grammars, modules and other grammars, modules')
        loadedGrammars = natlinkmain.loadedFiles.keys()
        if 'unimacro grammars' not in memory:
            memory['unimacro grammars'] = {}
        mem = memory['unimacro grammars']
        for m in uniGrammars:
            if m in loadedGrammars:
                mem[m] = sys.modules[m].__doc__
            else:
                if not m in mem:
                    mem[m] = ''

        if 'unimacro modules' not in memory:
            memory['unimacro modules'] = {}
        mem = memory['unimacro modules']
        for m in uniModules:
            if m in sys.modules:
                mem[m] = sys.modules[m].__doc__
            else:
                try:
                    M = __import__(m)
                except ImportError:
                    print 'cannot import module: %s'% m
                    continue
                mem[m] = M.__doc__
                mem[m] = M.__doc__
                del M

        print 'writing to pickle file: %s'% pickleFile
        psock = open(pickleFile, 'w')
        pickle.dump(memory, psock)
        psock.close()
        L = []
        htmlFiles = filter(isHtmlFile, os.listdir(docPath))
        
        
        categories = self.ini.get('documentation')
        if not categories:
            self.DisplayMessage('please fill in documentation categories')

        for c in categories:
            if not c in memory:
                continue
            L.append("<H1>%s</H1>"% c)
            mem = memory[c]
            for m in mem:
                file = m+'.html'
                if os.path.isfile(os.path.join(docPath, m+'.html')):
                    link = "<a href=%s.html>%s</a>"% (m, m)
                    htmlFiles.remove(file)
                else:
                    link = "???%s"% m
                if mem[m] == None:
                    text = 'no doc string for this module'
                elif mem[m] == '':
                    text = 'module could not be loaded, possibly start program and do "Make documentation" again'
                else:
                    text = mem[m]

                if text.find('\n\n'):
                    T = text.split('\n\n')
                    text = T[0]
                L.append("<p>%s: %s</p>"% (link, text))
        if htmlFiles:
            M = []
            L.append("<H1>%s</H1>"% "other files")
            for f in htmlFiles:
                if f == 'index.html':
                    continue
                name = f.split('.')[0]
                link = "<a href=%s>%s</a>"% (f, name)
                M.append(link)
            L.append("<p>%s</p>"% ', '.join(M))
        HTMLpage = '''<!doctype html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html><head><title>Natlink grammars and modules documentations</title>
<style type="text/css"><!--
TT { font-family: lucidatypewriter, lucida console, courier }
--></style></head><body bgcolor="#f0f0f8">
%s
</body></html>''' % '\n'.join(L)
        fsock = open(os.path.join(docPath, 'index.html'), 'w')
        fsock.write(HTMLpage)
        fsock.close()
                    
        os.chdir(oldPath)
        
        self.DisplayMessage('okay')
        

    def gotResults_stopwatch(self,words,fullResults):
        """ stopwatch"""
        if self.hasCommon(words, 'start'):
        	  self.startTime = time.time()
        else:
        	  t = time.time()
        	  elapsed = t - self.startTime
        	  action('MSG %.2f seconds'% elapsed)
        	  self.startTime = t


#  sstarting message
    def gotResults_test(self,words,fullResults):

        print "got words: %s"% words
        ## delete to end:
        #iconDir = r'D:\natlink\unimacro\icons'
        #for name in ['repeat', 'repeat2', 'waiting', 'waiting2']:
        #    iconPath = os.path.join(iconDir, name+'.ico')
        #    print 'iconPath', iconPath
        #    natlink.setTrayIcon(iconPath)
        #    time.sleep(0.5)
        #
        #natlink.setTrayIcon()

        #allUsers = natlink.getAllUsers()
        #print 'allUsers: %s'% allUsers

        ## try displayText:#
        #for i in range(10):
        #    natlink.displayText('test %s\n'% i, i)
        #reload(actions)
        #print 'calling script'
        #actions.doAction("AHK showmessageswindow.ahk")
        ##t = 'xyz'
        #keydown = natut.wm_keydown  # or wm_syskeydown
        #keyup = natut.wm_keyup      # or wm_syskeyup
        #
        #ctrl_down = (keydown, natut.vk_control, 1)
        #ctrl_up = (keyup, natut.vk_control, 1)
        #v_key = ord('V')
        #v_down = (keydown, v_key, 1)
        #v_up = (keyup, v_key, 1)
        #          
        #natlink.playEvents([ctrl_down, v_down, v_up, ctrl_up])
        #natut.playString("{ctrl}{ctrl}{ctrl}{ctrl}{ctrl}{ctrl}{ctrl}" + t, 0x200)natlink
##        
    def gotResults_reload(self,words,fullResults):
        print "reloading natlink...."
        natqh.switchToWindowWithTitle("Messages from Python Macros")
        natqh.Wait()
        natlink.setMicState("off")
        natqh.Wait()
        print "do it yourself..."
    
   # deze regel print de naam van de huidige module in het debug-venster
    def gotResults_info(self,words,fullResults):
        """display in a message box information about the window, user or unimacro

        """
        T = []
        extra = []
        if self.hasCommon(words,'window'):
            m = natlink.getCurrentModule()
            hwnd = m[2]
            p = natqh.getProgInfo(m)
            toporchild = p[2]
            T.append('---from natqh.getProgInfo:')
            T.append('0 program: %s'% p[0])
            T.append('1 window title: %s'% p[1])
            T.append('2 toporchild: %s'% p[2])
            T.append('3 window handle: %s'% p[3])
            if toporchild == 'top':
                overrule = actions.topWindowBehavesLikeChild(m)
                if overrule:
                    T.append('\t*** but should be treated as child window according to actions.topWindowBehavesLikeChild')
            else:
                overrule = actions.childWindowBehavesLikeTop(m)
                if overrule:
                    T.append('\t*** but should be treated as top window according to actions.childWindowBehavesLikeTop')
            T.append('')
            T.append('---from getCurrentModule:')
            T.append('0 program path: %s'% m[0])
            T.append('1 window title: %s'% m[1])
            T.append('2 window handle: %s'% m[2])
            T.append('')
            T.append('---from GetClassName:')
            T.append('class name: %s'% win32gui.GetClassName(hwnd))
        elif self.hasCommon(words,'user'):
            T.append('user:\t%s'% natqh.getUser())
            T.append('language:\t%s'% self.language)
            bm = natqh.getBaseModel()
            bt = natqh.getBaseTopic()
            T.append('BaseModel:\t%s'% bm)
            T.append('BaseTopic:\t%s'% bt)
            T.append('')
            T.append('see messages window for trainuser info')
            extra = ['lines for making a new user:']
            extra.append(r'cd d:\natlink\miscscripts   (or different folder)')
            extra.append(r'python trainuser.py d:\natlink\recordings\recordingcode "user name" "%s" "%s"'%\
                         (bm, bt))
            extra.append('change folders, recording code and user name of course')
            
        elif self.hasCommon(words,'unimacro'):
            T.append('DNSVersion:\t%s'% natqh.getDNSVersion())
            T.append('WindowsVersion:\t%s'% natqh.getWindowsVersion())
            T.append('Natlink/Unimacro userDirectory:\t%s'% natqh.getUserDirectory())
            T.append('(Unimacro) UserIniFilesDirectory:\t%s'% natqh.getUnimacroUserDirectory())
            T.append('DNSuserDirectory:\t%s'% natqh.getDNSuserDirectory())
        elif self.hasCommon(words,'path'):
        	  T.append('the python path:')
        	  T.append(pprint.pformat(sys.path))
        elif self.hasCommon(words, "class"):
            T.append()
        else:
            T.append('no valid keyword found')

        s = '\n'.join(T)
        self.DisplayMessage(s)
        print s
        print
        for e in extra:
            print e
            

    def gotResults_variable(self,words,fullResults):
        cmdVariable = self.hasCommon(words[0], 'Variable')
        cmdMethod = self.hasCommon(words[0], 'Method')
        
        c = self.getNumberFromSpoken(words[-1])
        
        if c:
            keystroke('{Shift+Ctrl+ExtLeft %s}' % c)
        else:
            action("HW select that")
            natqh.Wait(0.1)
        keystroke('{ctrl+x}')
        natqh.Wait(0.1)
        t = natlink.getClipboard()
        # put spaces if they were collected on the clipboard:
        while t and t[0] == " ":
            t = t[1:]
            keystroke(" ")
        t = t.strip()
        if not t:
            print 'no variable to compress!'
            return
        # split words into a list:
        w = t.split()
        if cmdVariable or cmdMethod:
            # uppercase each command word:
            w = map(self.capit, w)

        T = ''.join(w)
        if cmdVariable:
            T = T[0].lower() + T[1:]
        # add words to vocabulary!
        if natqh.getDNSVersion() >= 11:
            backslashes = '\\\\'
        else:
            backslashes = '\\'
        if len(w) > 1:
            natqh.addWordIfNecessary(T+backslashes+t)
        else:
            natqh.addWordIfNecessary(T)
            
        keystroke(T)


    def capit(self, s):
        """ capitalise, but leave upper case characters as they are

        (the builtin capitalise makes first letter upper case and the following
         letters lowercase)
        """
        return s[0].upper() + s[1:]

    def gotResults_undo(self,words,fullResults):
        counts = self.getNumbersFromSpoken(words)
        if counts:
            count = counts[0]
        else:
            count = 1
        #print 'count: %s'% count
        for i in range(count):
            action('<<undo>>')

    def gotResults_redo(self,words,fullResults):
        counts = self.getNumbersFromSpoken(words)
        if counts:
            count = counts[0]
        else:
            count = 1
        #print 'count: %s'% count
        for i in range(count):
            action('<<redo>>')

    def gotResults_mousefix(self,words,fullResults):
        fix = 0
        xPos,yPos = natlink.getCursorPos()
        if self.hasCommon(words, ['vast', 'omlaag', 'Down', 'Fix']):
            action('MDOWN')
        elif self.hasCommon(words, ['los', 'omhoog', 'Up', 'Release']):
            action('ENDMOUSE')
        else:
            print '_general, mousefix, invalid keywords: %s'% words


    def gotResults_comment(self,words,fullResults):
        name = nameList[words[-1]]
        if name:
            ts = time.strftime("%d%m%Y", time.localtime(time.time()))
        else:
            ts = time.strftime("%d%m%y_", time.localtime(time.time()))

        m = natlink.getCurrentModule()
        if natqh.matchModule('pythonwin', modInfo=m):
            com = "#" + name + ts
        elif natqh.matchModule('textpad', 'html', modInfo=m):
            com = "<!--" + name + ts + "-->"
        elif natqh.matchModule(m,'textpad', '.c', modInfo=m):
            com = "$$$$" + name + ts + "$$$$"
        elif natqh.matchModule(m,'textpad', '.py', modInfo=m):
            com = "#" + name + ts
        else:
            com = name + ts
        keystroke(com+"\n")
            
    def gotResults_modes(self,words,fullResults):
        """enable different modes

        When going to spell mode or command mode the special
        set which makes searching and dictating a single word
        or a few words possible are enabled.

        """
        mode = self.hasCommon(words, modes)
        if not mode:
            print 'modes, invalid mode: %s'% words
            return
        if mode in ['normal', 'normale']:
            M = 0
        elif mode in ['dictation', 'dicteer', 'dictate']:
            M = 1
        elif mode in ['command', 'commando']:
            M = 2
        elif mode in ['numbers', 'nummer']:
            M = 3
        elif mode in ['spell', 'spel']:
            M = 4
        else:
            print 'no valid mode: %s'% mode
            return

        self.setMode(M)

        if M > 1:
            self.DisplayMessage('<_general: setting command set>')
            self.activateSet(commandSet)
        else:
            self.DisplayMessage('<_general: setting normal set>')
            self.activateSet(normalSet)
            
        

    def gotResults_namephrase(self,words,fullResults):
        # list of words that can be combined in a double christian name
        #  eg Jan Jaap or Jan-Marie 
        voornamenList = ['Jan', 'Jaap', 'Peter', 'Louise', 'Anne'
                         ]
        modInfo = natlink.getCurrentModule()
        action("CLIPSAVE")
        keystroke("{Ctrl+c}")

        # do contents of clipboard:
        t = string.strip(natlink.getClipboard())
        if not t:
            modInfo = natlink.getCurrentModule()
            if natqh.matchModule('natspeak', 'spell', modInfo):
                keystroke("{ExtHome}{Shift+ExtEnd}{Ctrl+x}")
                natqh.Wait(0.5)
                t = string.strip(natlink.getClipboard())
                if not t:
                    action("CLIPRESTORE")
                    return
            else:
                if self.language == 'nld':
                    com = "Selecteer dat"
                else:
                    com  = "Select That"
                if natqh.getDNSVersion() >= 7:
                    com = com.lower()
                action("HW %s"%com)
                natqh.Wait(0.5)
                keystroke("{Ctrl+c}")
                
                t = string.strip(natlink.getClipboard())
                if not t:                    
                    self.DisplayMessage("select a text first")
                    action("CLIPRESTORE")
                    return
        if self.hasCommon(words, ['naam', 'Name']):
            result = namelist.namelistUnimacro(t, ini=self.ini)
            print 'result of namelistUnimacro function: %s'% result
            for r in result:
                print 'adding part: %s'% r
                natqh.addWordIfNecessary(t)
            keystroke(r)
        else: # zonder naam in words, a normal phrase:
            print 'adding phrase %s'% t
            natqh.addWordIfNecessary(t)
            keystroke(t)
        action("CLIPRESTORE")

            
    def gotResults_hyphenatephrase(self,words,fullResults):
        # selection or last utterance is spelled out with all caps and hyphens
        # Quintijn, August 15, 2009

        # save clipboard, release after the action:                                 
        action("CLIPSAVE")
        # hasCommon function for possibility of translations/synonyms without altering the code:
        if self.hasCommon(words[-1], "phrase"):
            keystroke("{Ctrl+c}")
            # do contents of clipboard:
            t = string.strip(natlink.getClipboard())
            if not t:
                if self.language == 'nld':
                    com = "Selecteer dat"
                else:
                    com  = "Select That"
                if natqh.getDNSVersion() >= 7:
                    com = com.lower()
                action("HW %s"%com)
                natqh.Wait(0.5)
                keystroke("{Ctrl+c}")
                t = string.strip(natlink.getClipboard())
            if not t:                    
                self.DisplayMessage("select a text first")
                action("CLIPRESTORE")
                return
        elif self.hasCommon(words, ('word', 'words')):
            counts = self.getNumbersFromSpoken(words)
            if counts:
                count = counts[0]
            else:
                count = 1
            keystroke("{shift+ctrl+left %s}"% count)
            keystroke("{Ctrl+c}")
            t = string.strip(natlink.getClipboard())
            if not t:                    
                self.DisplayMessage("could not select a valid text")
                action("CLIPRESTORE")
                return
        else:
            self.DisplayMessage("unexpected last word in command phrase: %s"% words[-1])
            action("CLIPRESTORE")
            return
            

        # first paste back the selected text, and add a space if needed:
        L = []
        # for each word in utterance join uppercased characters of word with a '-'
        tWords = t.split()
        for word in tWords:
            L.append('-'.join([t.upper() for t in word]))
            L.append(' ')
        keystroke(''.join(L))
        action("CLIPRESTORE")
        # 
    def gotResults_openuser(self,words,fullResults):
        user = self.getFromInifile(words[-1], 'users')
        print 'user: %s'% user
        try:
            natlink.openUser(user)
        except natlink.UnknownName:
            print 'cannot open user "%s", unknown name'% user
            
            


    def gotResults(self,words,fullResults):
        if self.highlight:
            # for Shane
            asterisksSpacing = 1   # to be perfected later as option of this grammar
            if asterisksSpacing:
                if self.text.find('*'):
                    self.text = self.text.replace('*', ' * ')
            if self.text:
                action("<<startsearch>>")
                keystroke(self.text)
                action("<<searchgo>>")    
            else:
                print 'no text to highlight'
            return
            #keystroke("{ctrl+f}")
            #t = self.text
            #t = t.replace(' . ', '.')
            #t = t.replace('( ', '(')
            #t = t.replace(' )', ')')
            ##print 'execute highlight with "%s"'% highlightText
            #keystroke(t)
            #keystroke("{enter}")
            #return

        if self.search:
            progInfo = natqh.getProgInfo()

            # make provisions for searchwords (function (def), class (class) etc)
            if self.specialSearchWord:
                self.text = self.ini.get('searchwords', self.specialSearchWord) + self.text
            if self.count:
                count = int(self.count)
            else:
                count = 1
            if self.search == 'forward':
                # forward
                self.direc = 'down'
                res = self.searchOn(count, progInfo=progInfo)
                return
            elif self.search == 'new':
                # new, just start the search dialog:
                self.searchMarkSpot(progInfo=progInfo)
                action('<<startsearch>>', progInfo=progInfo)
                return
            elif self.search == 'back':
                # back:
                self.direc = 'up'
                res = self.searchOn(count, progInfo=progInfo)
                return
            elif self.search ==  'go back':
            # go back, return to origin
                print "search go back"
                self.searchGoBack(progInfo=progInfo)
                return
            elif self.search in ('for', 'before','after'):
                # new search with text
                self.direc = 'down'
                print 'new leap to text: %s'% self.text
                self.searchMarkSpot(progInfo=progInfo)
                res = self.searchForText(self.direc, self.text, progInfo=progInfo, beforeafter=self.search)
            elif self.search == 'extend':
                res = self.searchForText(self.direc, self.text, progInfo=progInfo, extend=1)
            elif self.search == 'insert':
                res = self.searchForText(self.direc, self.text, progInfo=progInfo, insert=1)
            else:
                print 'invalid search code: %s'% self.search
                self.DisplayMessage('search, invalid search code: %s'% self.search)
                return
            if res == -2:
            # search failed, did cancel mode
                return 
            natqh.visibleWait()
            print 'calling stop search'
            self.stopSearch(progInfo=progInfo)

    def searchOn(self, count, progInfo=None):
        """search up or down possibly more times"""
        for i in range(count):
            res = self.searchForText(self.direc, progInfo=progInfo)
            self.direc = self.getLastSearchDirection() # in case back search changed it!
            if res == -2:
                # search failed, did cancel mode
                return 
        natqh.visibleWait()
        self.stopSearch(progInfo)


    def GetGrammarModuleName(self):
        return __name__    

    def GetDictionaries(self):
        Dicts={
        }
        return Dicts

    def Message(self,t):
        tt = t + "  (command: " + self.fullText + ")"
        natqh.Message(tt,self.title)
        

def isPythonFile(f):
    return f[-3:] == '.py'

def isHtmlFile(f):
    return f[-5:].lower() == '.html'


Classes = ('TkTopLevel')
def getIdleTitles():
    """get all titles of top windows with class name in tuple below

    This class name belongs, as far as I know, to the window explorer window

    """
    TitlesHandles = []

    ##print 'Classes:', Classes
##    Classes = None
    win32gui.EnumWindows(getIdleWindowsWithText, (TitlesHandles, Classes))
    return TitlesHandles

def getIdleWindowsWithText(hwnd, th):
    TH, Classes = th
##    if wTitle.find('d:') == 0:
##        print 'class:', win32gui.GetClassName(hwnd)
    if win32gui.GetClassName(hwnd) in Classes:
        wTitle = win32gui.GetWindowText(hwnd).strip().lower()
        TH.append((wTitle, hwnd))


# standard stuff Joel (adapted for possible empty gramSpec, QH, unimacro)
thisGrammar = ThisGrammar()
if thisGrammar.gramSpec:
    thisGrammar.initialize()
else:
    thisGrammar = None

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None

# forgot about this, possibly delete (QH 2010):
#def processLine(line):
#    """proces a line"""
#    if line.find("Bind") == -1:
#        return line
#    obj, options = line.split('.Bind')
#    lenstart = len(obj) - len(obj.lstrip())
#    obj = obj.strip()
#    options = options[1:-1]
#    pars = tuple(map(string.strip, options.split(',')))
#    if len(pars) == 2:
#        oldMethod, method = pars
#        return '%s%s(%s, %s)'% (' '*lenstart, oldMethod, obj, method)
#    elif len(pars) == 3:
#        oldMethod, method, id = pars
#        return '%s%s(%s, %s, %s)'% (' '*lenstart, oldMethod, obj, id, method)
#    else:
#        return 'invalid pars: %s %s'% (len(pars), line)
#




