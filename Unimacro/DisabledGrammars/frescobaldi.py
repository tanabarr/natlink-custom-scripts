__version__ = "$Revision: 417 $, $Date: 2011-03-13 17:14:04 +0100 (zo, 13 mrt 2011) $, $Author: quintijn $"
#
# frescobaldi.py
#
# Written by: Quintijn Hoogenboom (QH softwaretraining &
# advies),2002, revised October 2003
# march 2011: change sol to frescobaldi
"""grammar rules for frescobaldi (lilypond) music typesetting

"""

natqh = __import__('natlinkutilsqh')
natut = __import__('natlinkutils')
natbj = __import__('natlinkutilsbj')
from actions import doAction as action
from actions import doKeystroke as keystroke
import re, copy
from lynote import LyNote   

reSplitInWords = re.compile(r'(\s+)')  # split on whitespace
reIsWhiteSpace = re.compile(r'\s')

ancestor = natbj.DocstringGrammar
class ThisGrammar(ancestor):
    name = 'frescobaldi'

    def initialize(self):
        global language
        if self.load(self.gramSpec):
            print 'grammar frescobaldi (%s) active'% self.name
            self.prevHandle = -1
        else:
            language = ""
        self.isActive = 0
                        
    def gotBegin(self,moduleInfo):
        winHandle = moduleInfo[2]
        if self.prevHandle == winHandle: return
        self.prevHandle = winHandle
        if moduleInfo[0].lower().find('frescobaldi.exe') > 0 and natqh.isTopWindow(moduleInfo[2]):
            if self.checkForChanges:
                #print 'grammar frescobaldi (%s) checking the inifile'% self.name
                self.checkInifile()
            self.switchOnOrOff()
            self.isActive = 1
        elif self.isActive:
            self.deactivateAll()
            self.isActive = 0

    def gotResultsInit(self,words,fullResults):
        """initialize values
        """
        self.note = ""
        self.rythm = ""
        self.point = "" # for rythms, halving a note or rest
        self.noteaddition = "" # up, down, slur
        self.separator = "" # bar
        self.pitch = "" # up or down octave(s)
        self.wordsList, self.noteIndexes = [], [] # for notesnavigate
        self.notesWanted = 0 # also for notesnavigate...
        self.newNotes = []
        self.hadFigure = 0
        
    def rule_sequence(self, words):
        "(<note>|<pitch>|<rythm>|<separator>|<noteaddition>)+"
        pass
    
    def subrule_note(self, words):
        "{notes}"
        for w in words:
            note = self.getFromInifile(w, 'notes')
            if note:
                if self.note:
                    self.finishNote()
                self.note = note
                continue

    def subrule_pitch(self, words):
        "{pitchs}"
        for w in words:
            pitch = self.getFromInifile(w, 'pitchs')
            if pitch:
                self.pitch += pitch
                continue                                

    def subrule_noteaddition(self, words):
        "{noteadditions}"
        for w in words:
            self.noteaddition = self.getFromInifile(w, 'noteadditions')
        
    def subrule_rythm(self, words):
        "{rythms}|{rythms} point"
        for w in words:
            if self.hasCommon(w, "point"):
                self.point += "."
            else:
                rythm = self.getFromInifile(w, 'rythms')
                if self.rythm and self.note:
                    self.finishNote()
                self.rythm = rythm

    def subrule_separator(self, words):
        "{separators}"
        self.finishNote()
        s = []
        for w in words:
            separator = self.getFromInifile(w, 'separators')
            self.newNotes.append(separator)
            
    def rule_figure(self, words):
        """<notesnavigate> figure {figures}+"""
        # start with the pointer in the music pane
        self.hadFigure = 1
        selection = self.getFigurePart()
        if not selection:
            print 'rule_figure, no selection found, stop macro'
            return 
        L = []
        previous = None
        for w in words:
            figure = self.getFromInifile(w, 'figures')
            print 'figure: %s, result: %s'% (w, figure)
            if figure:
                if previous and self.isFigure(previous) and not self.isFigure(figure):
                    if figure.startswith("_"):
                        figure = figure.lstrip("_")
                    L[-1] = L[-1] + figure
                else:
                    L.append(figure)
                previous = figure
        self.keystroke(' '.join(L))  # allow for { , not being a control character!
        
    def isFigure(self, figure):
        """return True if figure is a cipher, 1, 2, ...
        """
        try:
            int(figure)
        except ValueError:
            return False
        return True
            
    def rule_notesaddition(self, words):
        "<notesnavigate>{notesaddition}"
        # if words end with Off, On or End, they are in front of the first word and separated from the last.
        if not self.noteIndexes:
            print 'notesaddition, no notes found in selection'
            return
        
        prepost = self.getFromInifile(words[-1], 'notesaddition')
        print 'prepost: "%s"'% prepost
        if not prepost:
            return
        if ":" in prepost:
            pre, post = prepost.split(":")
        else:
            pre, post = prepost[:1], prepost[-1:]
        
        startNote = self.wordsList[self.noteIndexes[0]]
        endNote = self.wordsList[self.noteIndexes[self.notesWanted-1]]
        
        startNote.updateNote(pre)
        endNote.updateNote(post)
        #for ending in ['On', 'Off']:  # strange bit here
        #    if post.endswith(ending):
        #        self.wordsList.insert(endNote, post)
        #        break
        #else:
        #    self.wordsList.insert(endNote+1, post)
        #
        #for ending in ['On', 'Off', 'End']:
        #    if pre.endswith(ending):
        #        self.wordsList.insert(startNote, pre)
        #        print 'pre "%s" ending: "%s", wordsList: %s'% (pre, ending, self.wordsList)
        #        break
        #else:
        #    print 'pre "%s" general, wordList: %s'% (pre, self.wordsList)
        #    self.wordsList.insert(startNote+1, pre)

        snippet = " ".join(map(str, self.wordsList))
        print 'new snippet: %s'% snippet
        keystroke(snippet)
        
    def rule_notechange(self, words):
        """<notesnavigate><sequence>"""
        ### accept only 1 note
        pass
        
    def rule_test(self, words):
        """test position {direction}"""
        # position first at word boundary
        direction = self.getFromInifile(words[-1], 'direction')
        self.positionAtWordBoundary(direction)
    
    def subrule_notesnavigate(self, words):
        "here | [here] [next] (note | {n2-20} notes)"
        # leave next|previous for the moment, assume always count from the beginning
        DIR = 'right'
        if self.hasCommon(words, 'here'):
            natqh.buttonClick()
        
        try:
            nStr = self.getNumbersFromSpoken(words)[0] # returns a string or None
            n = int(nStr)
        except IndexError:
            n = 1
        if n == 1:
            gotoNext = self.hasCommon(words, 'next')
            if gotoNext:
                print 'move right one note! Todo'
        self.notesWanted = n
        self.getNextNotes(n)        
        
        
    def getNextNotes(self, n=1):
        DIR = 'right'
        if reIsWhiteSpace.match(self.getnextchar()):
            # inside a word, go left until at left word boundary
            while not reIsWhiteSpace.match(self.getpreviouschar()):
                keystroke("{left}")
        notesFound = 0
        self.notesWanted = n
        
        # sometimes shift+ctrl+right does not select a complete note or a command word,
        # so therefore the while:
        i = 0
        while notesFound < n and i < 20:
            notesToGo = n - notesFound
            print 'go right: %s'% notesToGo
            t =self.getselectionafterkeystroke("{shift+ctrl+%s %s}"% (DIR, notesToGo))
            i += 1
            while t and t[-1] != ' ' and i < 20:
                # not at right word boundary, proceed 1
                print 'go one further...'
                t = self.getselectionafterkeystroke("{shift+%s}"% DIR)
                i += 1
            self.wordsList, self.noteIndexes = self.analyseString(t)
            print 'wordsList: %s, noteIndexes: %s'% (self.wordsList, self.noteIndexes)
            notesFound = len(self.noteIndexes)
    
    def getPreviousNotes(self, n=1):
        ## assume after a note, so move left until at word boundary and then select left.
        while reIsWhiteSpace.match(self.getpreviouschar()):
            keystroke("{left}")
        notesFound = 0
        #notesWanted = n
        DIR = "left"

        # sometimes shift+ctrl+left does not select a complete note or a command word,
        # so therefore the while:
        i = 0
        while notesFound < n and i < 20:
            notesToGo = n - notesFound
            t =self.getselectionafterkeystroke("{shift+ctrl+%s %s}"% (DIR, notesToGo))
            i += 1
            while t and t[0] != ' ' and i < 20:
                # not at left word boundary, proceed 1
                print 'getPreviousNotes go one further... got: "%s"'% t
                i += 1
                t = self.getselectionafterkeystroke("{shift+%s}"% DIR)
            print 'result getPreviousNotes: %s'% t
            #t = self.getselectionafterkeystroke("{shift+%s}"% DIR)
            #print 'result getPreviousNotes one more: %s'% t
            
            self.wordsList, self.noteIndexes = self.analyseString(t)
            notesFound = len(self.noteIndexes)
            print 'wordsList: %s, noteIndexes: %s, notesFound: %s'% (self.wordsList, self.noteIndexes, notesFound)
    
        
    def gotResults(self,words,fullResults):
        """flush last part of utterance"""
        if self.hadFigure:
            return
        
        output = []
        self.finishNote()
        
        if not self.newNotes:
            return
        
        print '===newNotes: %s'% self.newNotes
        
        
        if not self.wordsList:
            # check if just before a new note
            if self.getnextchar().strip():
                print 'get next note'
                self.getNextNotes()

        if self.wordsList:
            print 'merge notes in wordsList'
            for i, note in enumerate(self.newNotes):
                if i < len(self.noteIndexes):
                    self.wordsList[self.noteIndexes[i]].updateNote(self.newNotes[i])
                else:
                    self.wordsList.append(note)
                    self.wordsList.append(' ')
            keystroke(''.join([str(item) for item in self.wordsList]))
            return
        # see if first note is a note, if so, output notes otherwise
        # change previous note (for example add rythm)
        noteOne = self.newNotes[0]
        if isinstance(noteOne, LyNote):
            if noteOne.isNote():
                # a valid note, if no space before, make one:
                if self.getpreviouschar().strip():
                    print 'previous char true, make a space'
                    output.append(' ')
            else:
                # a LyNote object, but not a valid note, so a correction of the
                # previous one:
                self.getPreviousNotes(1)
                print 'noteIndexes: %s, notes: %s'% (self.noteIndexes, self.wordsList)
                self.wordsList[self.noteIndexes[-1]].updateNote(noteOne)
                output.extend(self.wordsList)
                self.newNotes.pop(0)
        else:
            # not a LyNote, such as a bar, put a space if it is not there:
            if self.getpreviouschar().strip():
                print 'previous char true, make a space'
                output.append(' ')
            

        
        for note in self.newNotes:
            output.append(str(note))
            if not str(note).endswith("{enter}"):
                output.append(' ')
            
        keystroke(''.join([str(item) for item in output]))
        
                
        
    def finishNote(self):
        """flush if far enough"""
        t = []
        for name in ['note', 'pitch', 'rythm', 'point', 'noteaddition']:
            s = getattr(self, name, None)
            if s:
                print 'name: %s, content: "%s"'% (name, s)
                t.append(s)
                setattr(self, name, "")
        if t:
            note = LyNote(''.join(t))
            self.newNotes.append(note)


        #    if reIsWhiteSpace.match(self.getpreviouschar()):
        #    keystroke("{left}")
        #
        #        # tie after the previous note
        #        while 1:
        #            leftofcursor = self.getselectionafterkeystroke('{shift+left}')
        #            if leftofcursor == ' ':
        #                keystroke('{right}{left}')
        #            else:
        #                keystroke('{right}')
        #                break
        #        # now output at correct place:
        #        keystroke(t)
        #else:
        #    ## self.note:
        #    # ensure a space
        #    leftofcursor = self.getselectionafterkeystroke('{shift+left}')
        #    keystroke('{right}')
        #    if leftofcursor != ' ':
        #        keystroke(' ')
        #    # new note:
              
    def getnextchar(self):
        """get character right of the cursor
        """
        t = self.getselectionafterkeystroke("{shift+right}")
        if t:
            keystroke("{shift+left}")
        if t: return t[0]
        else: return ""

    def getpreviouschar(self):
        """get character right of the cursor
        """
        t = self.getselectionafterkeystroke("{shift+left}")
        if t:
            keystroke("{shift+right}")
        print 'getpreviouschar, t: "%s"'% t
        if t: return t[-1]
        else: return ""
        
    def getFigurePart(self):
        # go left then right for selecting the note at the cursor position
        natqh.saveClipboard()
        for i in range(20):
            if self.getpreviouschar() != "<":
                keystroke("{left}")
            else:
                break
        else:
            print 'getFigurePart, did not find "<", stop the macro'
            keystroke("{right 20}")
            return
        for i in range(10):
            if self.getnextchar() != ">":
                keystroke("{shift+right}")
            else:
                break
        else:
            print 'getFigurePart, did not find ">", stop the macro'
        result = self.getClipboardFromSelection()
        natqh.restoreClipboard()
        return result
        
    def makeSelection(self, direction, n):
        """select and get (via clipboard) a number of notes
        """
        # test if notes have been all taken
        natqh.saveClipboard()  # action("CLIPSAVE")
            
        reverseDirections = dict(left='right', right='left')    
        reverseDirection = reverseDirections[direction]
        self.positionWordBoundary(reverseDirection)
        #keystroke('{ctrl+shift+%s %s}'% (direction, n))
        t = natqh.getClipboard()
        
        natqh.restoreClipboard()  #  action("CLIPRESTORE")
        
    def getselectionafterkeystroke(self, keys=None, visibleWait=None):
        """do the keystroke and return the selected text
        
        omit the {ctrl+c}, this one is done in this function.
        
        if keys is omitted, this is a check if there is some selection on.
        
        if visibleWait is set (simply 1 or True) a little longer pause is done so the user can
        see it happen...
        
        
        """
        natqh.clearClipboard()
        kkeys = keys.replace("{", "{{}")
        print 'getselectionafterkeystroke, %s'% kkeys
        if keys:
            keystroke(keys)
        natqh.shortWait()
        keystroke("{ctrl+c}")
        if visibleWait:
            natqh.visibleWait()
        else:
            natqh.shortWait()
        t = natqh.getClipboard()
        print 'result getselectionafterkeystroke: "%s"'% t
        return t
      
    def analyseString(self, S):
        """split string in "words", leave the whitespace and return a second list of the note indexes
        
        return wordsList, notesIndexes, both being a list. the length of noteIndexes gives the number
        of notes found.
        """
        wordsList = reSplitInWords.split(S)
        outputWords = []
        noteIndexes = []
        lyn = None
        inComment = 0
        for i, w in enumerate(wordsList):
            if inComment:
                outputWords.append(w)
                if w.find('\n') >= 0:
                    inComment = 0
                continue
            
            
            if w and w[0] in 'abcdefg':
                lyn2 = LyNote(w)
                if lyn2.isNote():
                    print 'valid note: %s'% lyn2
                    noteIndexes.append(i)
                    if lyn:
                        outputWords.append(lyn)
                    lyn = copy.copy(lyn2)
                    lyn2 = None
                else:
                    if lyn:
                        outputWords.append(lyn)
                        lyn = None
                    outputWords.append(w)
            else:
                if lyn:
                    outputWords.append(lyn)
                    lyn = None
                if w.startswith("%"):
                    inComment = 1
                outputWords.append(w)


                    
        if lyn:
            outputWords.append(lyn)
        return outputWords, noteIndexes
        
        
    def keystroke(self, keys):
        """internal keys for frescobaldi can have {] (braces), output them separate
        """
        L = keys.split("{")
        for k in L:
            if k == '{':
                print 'open brace...'
                natlink.playString("{", 0x200)
                natqh.visibleWait()
            else:
                keystroke(k)
                
                
    #def positionAtWordBoundary(self, direction):
    #    """go into the direction until at word boundary"""
    #    reverseDirections = dict(left='right', right='left')    
    #    reverseDirection = reverseDirections[direction]
    #    while 1:
    #        t = None
    #        keystroke('{shift+%s}{ctrl+c}'%direction)
    #        natqh.visibleWait()
    #        t = natqh.getClipboard()
    #        if t == ' ':
    #            keystroke('{%s}'% reverseDirection)
    #            break
    #        keystroke("{%s}{%s}"% (reverseDirection, direction))
    #    else:
    #        print 'no space found in positionWordBoundary'
    #        return
    #   
       
    def getClipboardFromSelection(self):
        action("<<copy>>")
        natqh.shortWait()
        snippet = natqh.getClipboard()
        return snippet
        
            
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

