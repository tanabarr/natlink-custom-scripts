from __future__ import generators
# -*- coding: latin-1 -*-
#$Revision: 522 $, $Date: 2013-11-22 19:06:06 +0100 (vr, 22 nov 2013) $, $Author: quintijn $
#misc utility functions from Quintijn, used in unimacro and in
#local programs.
#copyright Quintijn Hoogenboom,  QH software, training & advies
import sys

try:
    import checkpath
    checkpath.checkpath()
except:
    pass

import types, string, os, shutil, copy, filecmp, pywintypes
import glob, re, sys, traceback
import time, filecmp
if sys.platform != 'linux2':
    import win32com.client
    from win32gui import GetClassName, EnumWindows, GetWindowText, GetWindow
import urllib, difflib
from htmlentitydefs import codepoint2name
import locale
locale.setlocale(locale.LC_ALL, '')

class QHError(Exception):
    pass

# for the testing
if sys.platform == 'win32':
    testdrive = "C:"
elif sys.platform == 'linux2':
    testdrive = "/home/etta"
else:
    testdrive = ''  # ??

_allchars = string.maketrans('', '')

def translator(frm='', to='', delete='', keep=None):
    """closure function to implement the string.translate functie
    python cookbook (2), ch 1 recipe 9

# functions below, see also testUtilsqh.py in unittest.
>>> fixwordquotes('\x91aa\x92')
"'aa'"
>>> fixwordquotes('\x93bb\x94')
'"bb"'

>>> normaliseaccentedchars('d\xe9sir\xe9 //\xddf..# -..e.')
'desireyf-e'

# this one should go before normaliseaccentedchars
#(and after splitting of the extension and folder parts)
>>> fixdotslash('abc/-.def this is no extension.')
'abc_-_def this is no extension_'

## normalise a inivars key (or section)
>>> fixinivarskey('abcd')
'abcd'
>>> fixinivarskey("abcd e'f  g")
'abcd ef  g'
    """
    if len(to) == 1:
        to = to * len(frm)
    trans = string.maketrans(frm, to)
    if keep is not None:
        delete = _allchars.translate(_allchars, keep.translate(_allchars, delete))
    def translate(s):
        return s.translate(trans, delete)
    return translate

fixwordquotes = translator('\x91\x92\x93\x94', "''\"\"")
###removenoncharacters = translator('
fixinivarskey = translator(keep=string.letters + ' ')
## function to make translation from e acute to e etc. goes into a translate function with translator
def isaccented(c):
    t = chr(c)
    try:
        name = codepoint2name[c]
    except KeyError:
        return
    if name == t:
        return
    if len(name) > 1:
        return name[0]

# fast translator functions:
accented = [(chr(c), isaccented(c)) for c in range(192,256) if isaccented(c)]
ffrom = ''.join([c for (c,d) in accented])
tto = ''.join([d.lower() for (c,d) in accented])
normaliseaccentedchars = translator(ffrom, tto, keep=ffrom + string.letters + string.digits + "-_")
ffrom = './'
tto = '__'
fixdotslash = translator(ffrom, tto)
ffrom = './ '
tto = '___'
fixdotslashspace = translator(ffrom, tto)

del ffrom
del tto
del accented
del isaccented
del codepoint2name

def curry(func, *args, **kwds):
    """curry from python cookbook, example 15.7,

    and python cookbook two: example 16.4.

    used for example for class FullTable, which is curried from TableLite

    >>> from HTMLgen import TableLite
    >>> str(TableLite())
    '\\n<table cellspacing="0"></table>'
    >>> FullTable = curry(TableLite, border=0, cellpadding=0, cellspacing=0, width = '100%')
    >>> str(FullTable())
    '\\n<table border="0" cellpadding="0" cellspacing="0" width="100%"></table>'

    """
    def curried(*moreargs, **morekwds):
        kw = kwds.copy()
        kw.update(morekwds)
        return func(*(args+moreargs), **kw)
    return curried

class peek_ahead(object):
    """Iterator that can look ahead one step

    From example 16.7 from python cookbook 2.

    The preview can be inspected through it.preview

    ignoring duplicates:
    >>> it = peek_ahead('122345567')
    >>> for i in it:
    ...     if it.preview == i:
    ...         continue
    ...     print i,
    1 2 3 4 5 6 7

    getting duplicates together:
    >>> it = peek_ahead('abbcdddde')
    >>> for i in it:
    ...     if it.preview == i:
    ...         dup = 1
    ...         while 1:
    ...             i = it.next()
    ...             dup += 1
    ...             if i != it.preview:
    ...                 print i*dup,
    ...                 break
    ...     else:
    ...         print i,
    ...
    a bb c dddd e

    """
    sentinel = object() #schildwacht
    def __init__(self, it):
        self._nit = iter(it).next
        self.preview = None
        self._step()
    def __iter__(self):
        return self
    def next(self):
        result = self._step()
        if result is self.sentinel: raise StopIteration
        else: return result
    def _step(self):
        result = self.preview
        try: self.preview = self._nit()
        except StopIteration: self.preview = self.sentinel
        return result

class peek_ahead_stripped(peek_ahead):
    """ Iterator that strips the lines of text, and returns (leftSpaces,strippedLine)

    sentinel is just False, such that peeking ahead can check for truth input

    >>> lines = '\\n'.join(['line1', '', ' one space ahead','', '   three spaces ahead, 1 empty line before'])
    >>> import StringIO
    >>> list(peek_ahead_stripped(StringIO.StringIO(lines)))
    [(0, 'line1'), (0, ''), (1, 'one space ahead'), (0, ''), (3, 'three spaces ahead, 1 empty line before')]

    example of testing look ahead

    >>> lines = '\\n'.join(['line1', '', 'line2 (last)'])
    >>> it = peek_ahead_stripped(StringIO.StringIO(lines))
    >>> for spaces, text in it:
    ...     print 'current line: |', text, '|',
    ...     if it.preview is it.sentinel:
    ...         print ', cannot preview, end of peek_ahead_stripped'
    ...     elif it.preview[1]:
    ...         print ', non empty preview: |', it.preview[1], '|'
    ...     else:
    ...         print ', empty preview'
    current line: | line1 | , empty preview
    current line: |  | , non empty preview: | line2 (last) |
    current line: | line2 (last) | , cannot preview, end of peek_ahead_stripped

    """
    sentinel = peek_ahead.sentinel
    
    def next(self):
        result = self._step()
        if result is self.sentinel: raise StopIteration
        else: return result
    def _step(self):
        """collect the line and do the processing"""
        result = self.preview
        try:
            line = self._nit().rstrip()
            self.preview = (len(line) - len(line.lstrip()), line.lstrip())
        except StopIteration: self.preview = self.sentinel
        return result

import collections
class peekable(object):
    """ An iterator that supports a peek operation. 
    
    this is a merge of example 19.18 of python cookbook part 2, peek ahead more steps
    and the simpler example 16.7, which peeks ahead one step and stores it in
    the self.preview variable.
    
    Adapted so the peek function never raises an error, but gives the
    self.sentinel value in order to identify the exhaustion of the iter object.
    
    Example usage:
    
    >>> p = peekable(range(4))
    >>> p.peek()
    0
    >>> p.next(1)
    [0]
    >>> p.isFirst()
    True
    >>> p.preview
    1
    >>> p.isFirst()
    True
    >>> p.peek(3)
    [1, 2, 3]
    >>> p.next(2)
    [1, 2]
    >>> p.peek(2) #doctest: +ELLIPSIS
    [3, <object object at ...>]
    >>> p.peek(1)
    [3]
    >>> p.next(2)
    Traceback (most recent call last):
    StopIteration
    >>> p.next()
    3
    >>> p.isLast()
    True
    >>> p.next()
    Traceback (most recent call last):
    StopIteration
    >>> p.next(0)
    []
    >>> p.peek()  #doctest: +ELLIPSIS
    <object object at ...>
    >>> p.preview #doctest: +ELLIPSIS
    <object object at ...>
    >>> p.isLast()  # after the iter process p.isLast remains True
    True
    """
    sentinel = object() #schildwacht
    def __init__(self, iterable):
        self._nit = iter(iterable).next  # for speed
        self._iterable = iter(iterable)
        self._cache = collections.deque()
        self._fillcache(1)          # initialize the first preview already
        self.preview = self._cache[0]
        self.count = -1  # keeping the count, possible to check
                         # isFirst and isLast status
    def __iter__(self):
        return self
    def _fillcache(self, n):
        """fill _cache of items to come, with one extra for the preview variable
        """
        if n is None:
            n = 1
        while len(self._cache) < n+1:
            try:
                Next = self._nit()
            except StopIteration:
                # store sentinel, to identify end of iter:
                Next = self.sentinel
            self._cache.append(Next)
    def next(self, n=None):
        """gives next item of the iter, or a list of n items
        
        raises StopIteration if the iter is exhausted (self.sentinel is found),
        but in case of n > 1 keeps the iter alive for a smaller "next" calls
        """
        self._fillcache(n)
        if n is None:
            result = self._cache.popleft()
            if result == self.sentinel:
                # find sentinel, so end of iter:
                self.preview = self._cache[0]
                raise StopIteration
            self.count += 1
        else:
            result = [self._cache.popleft() for i in range(n)]
            if result and result[-1] == self.sentinel:
                # recache for future use:
                self._cache.clear()
                self._cache.extend(result)
                self.preview = self._cache[0]
                raise StopIteration
            self.count += n
        self.preview = self._cache[0]
        return result
    
    def isFirst(self):
        """returns true if iter is at first position
        """
        return self.count == 0

    def isLast(self):
        """returns true if iter is at last position or after StopIteration
        """
        return self.preview == self.sentinel
        
    def peek(self, n=None):
        """gives next item, without exhausting the iter, or a list of 0 or more next items
        
        with n == None, you can also use the self.preview variable, which is the first item
        to come.
        """
        self._fillcache(n)
        if n is None:
            result = self._cache[0]
        else:
            result = [self._cache[i] for i in range(n)]
        return result
      
def get_best_match(texts, match_against, ignore=' ', treshold=0.9):
    """Get the best matching from texts, none if treshold is not reached
    
    texts: list of texts to choose from
    match_against: text wanted
    ignore: junk characters (set eg to "_ ")
    treshold: best match must be at least this value.
    
    """
    # JUNK =  space _
    # now time to figre out the matching
    ratio_calc = difflib.SequenceMatcher(lambda x: x in ignore)
    ratio_calc.set_seq1(match_against)

    ratios = {}
    best_ratio = 0
    best_text = ''

    for text in texts:
        # set up the SequenceMatcher with other text
        ratio_calc.set_seq2(text)

        # calculate ratio and store it
        ratios[text] = ratio_calc.ratio()

        # if this is the best so far then update best stats
        if ratios[text] > best_ratio:
            best_ratio = ratios[text]
            best_text = text

    if best_ratio > treshold:
        return best_text


def isSubList(largerList, smallerList):
    """returns 1 if smallerList is a sub list of largerList

>>> isSubList([1,2,4,3,2,3], [2,3])
1
>>> isSubList([1,2,3,2,2,2,2], [2])
1
>>> isSubList([1,2,3,2], [2,4])


    """
    if not smallerList:
        raise ValueError("isSubList: smallerList is empty: %s"% smallerList)
    item0 = smallerList[0]
    lenSmaller = len(smallerList)
    lenLarger = len(largerList)
    if lenSmaller > lenLarger:
        return    # can not be sublist
    # get possible relevant indexes for first item
    indexes0 = [i for (i,item) in enumerate(largerList) if item == item0 and i <= lenLarger-lenSmaller]
    if not indexes0:
        return
    for start in indexes0:
        slice = largerList[start:start+lenSmaller]
        if slice == smallerList:
            return 1
    



def ifelse(var, ifyes, ifno):
    """ternary operator simulated, if var: True else: False

    idea from "learning python"

    >>> x = []
    >>> print ifelse(x, 'a', 'b')
    b
    >>> y = 'yes'
    >>> print ifelse(y, 12, 23)
    12
    """
    if var:
        return ifyes
    else:
        return ifno


def isSubList(largerList, smallerList):
    """returns 1 if smallerList is a sub list of largerList

for use in voicecode...

>>> isSubList([1,2,4,3,2,3], [2,3])
1
>>> isSubList([1,2,3,2,2,2,2], [2])
1
>>> isSubList([1,2,3,2], [2,4])


    """
    if not smallerList:
        raise ValueError("isSubList: smallerList is empty: %s"% smallerList)
    item0 = smallerList[0]
    lenSmaller = len(smallerList)
    lenLarger = len(largerList)
    if lenSmaller > lenLarger:
        return    # can not be sublist
    # get possible relevant indexes for first item
    indexes0 = [i for (i,item) in enumerate(largerList) if item == item0 and i <= lenLarger-lenSmaller]
    if not indexes0:
        return
    for start in indexes0:
        slice = largerList[start:start+lenSmaller]
        if slice == smallerList:
            return 1
    



# helper string functions:
def replaceExt(fileName, ext):
    """change extension of file

>>> replaceExt("a.psd", ".jpg")
'a.jpg'
>>> replaceExt("a/b/c/d.psd", "jpg")
\'a/b/c/d.jpg'
    """
    ext = addToStart(ext, ".")
    fileName = str(fileName)
    a, extOld = os.path.splitext(fileName)
    return a + ext

def getExt(fileName):
    """return the extension of a file

>>> getExt("a.psd")
'.psd'
>>> getExt("a/b/c/d.psd")
'.psd'
>>> getExt("abcd")
''
>>> getExt("a/b/xyz")
''
    """
    a, ext = os.path.splitext(fileName)
    return ext


def removeFromStart(text, toRemove, ignoreCase=None):
    """returns the text with "toRemove" stripped from the start if it matches
>>> removeFromStart('abcd', 'a')
'bcd'
>>> removeFromStart('abcd', 'not')
'abcd'

working of ignoreCase:

>>> removeFromStart('ABCD', 'a')
'ABCD'
>>> removeFromStart('ABCD', 'ab', ignoreCase=1)
'CD'
>>> removeFromStart('abcd', 'ABC', ignoreCase=1)
'd'

    """
    if ignoreCase:
        text2 = text.lower()
        toRemove = toRemove.lower()
    else:
        text2 = text
    if text2.startswith(toRemove):
        return text[len(toRemove):]
    else:
        return text

def removeFromEnd(text, toRemove, ignoreCase=None):
    """returns the text with "toRemove" stripped from the end if it matches

>>> removeFromEnd('a.jpg', '.jpg')
'a'
>>> removeFromEnd('b.jpg', '.gif')
'b.jpg'

working of ignoreCase:

>>> removeFromEnd('C.JPG', '.jpg')
'C.JPG'
>>> removeFromEnd('D.JPG', '.jpg', ignoreCase=1)
'D'
>>> removeFromEnd('d.jpg', '.JPG', ignoreCase=1)
'd'

    """
    if ignoreCase:
        text2 = text.lower()
        toRemove = toRemove.lower()
    else:
        text2 = text
    if text2.endswith(toRemove):
        return text[:-len(toRemove)]
    else:
        return text

def addToStart(text, toAdd, ignoreCase=None):
    """returns text with "toAdd" added at the start if it was not already there

    if ignoreCase:
        return the start of the string with the case as in "toAdd"

>>> addToStart('a-text', 'a-')
'a-text'
>>> addToStart('text', 'b-')
'b-text'
>>> addToStart('B-text', 'b-')
'b-B-text'

working of ignoreCase:

>>> addToStart('C-Text', 'c-', ignoreCase=1)
'c-Text'
>>> addToStart('d-Text', 'D-', ignoreCase=1)
'D-Text'

    """
    if ignoreCase:
        text2 = text.lower()
        toAdd2 = toAdd.lower()
    else:
        text2 = text
        toAdd2 = toAdd
    if text2.startswith(toAdd2):
        return toAdd + text[len(toAdd):]
    else:
        return toAdd + text

def addToEnd(text, toAdd, ignoreCase=None):
    """returns text with "toAdd" added at the end if it was not already there

    if ignoreCase:
        return the end of the string with the case as in "toAdd"

>>> addToEnd('a.jpg', '.jpg')
'a.jpg'
>>> addToEnd('b', '.jpg')
'b.jpg'

working of ignoreCase:

>>> addToEnd('Cd.JPG', '.jpg', ignoreCase=1)
'Cd.jpg'
>>> addToEnd('Ef.jpg', '.JPG', ignoreCase=1)
'Ef.JPG'

    """
    if ignoreCase:
        text2 = text.lower()
        toAdd2 = toAdd.lower()
    else:
        text2 = text
        toAdd2 = toAdd
    if text2.endswith(toAdd2):
        return text[:-len(toAdd)] + toAdd
    else:
        return text + toAdd

def firstLetterCapitalize(t):
    """capitalize only the first letter of the string
    """
    if t:
        return t[0].upper() + t[1:]
    else:
        return ""

def extToLower(fileName):
    """leave name part intact, but change extension to lowercase
>>> extToLower("aBc.jpg")
'aBc.jpg'
>>> extToLower("ABC.JPG")
'ABC.jpg'
>>> extToLower("D:/a/B/ABC.JPG")
'D:/a/B/ABC.jpg'



    """
    f, ext = os.path.splitext(fileName)
    return f + ext.lower()


def appendBeforeExt(text, toAppend):
    """append text just before the extension of the filename part

>>> appendBeforeExt("short.html", '__t')
'short__t.html'
>>> appendBeforeExt("http://a/b/c/d/long.html", '__b')
'http://a/b/c/d/long__b.html'
    """
    base, ext = os.path.splitext(text)
    return base + toAppend + ext

def getBaseFolder(globalsDict):
    """get in a module the folder of this module.

    either sys.argv[0] (when run direct) or
    __file__, which can be empty. In that case take the working directory
    """
    baseFolder = ""
    if globalsDict['__name__']  == "__main__":
        baseFolder = os.path.split(sys.argv[0])[0]
        print 'baseFolder from argv: %s'% baseFolder
    elif globalsDict['__file__']:
        baseFolder = os.path.split(globalsDict['__file__'])[0]
        print 'baseFolder from __file__: %s'% baseFolder
    if not baseFolder:
        baseFolder = os.getcwd()
        print 'baseFolder was empty, take wd: %s'% baseFolder
    return baseFolder

Classes = ('ExploreWClass', 'CabinetWClass')


def partition_range(max_range):
    """partition for milla website in lengths of 3 or 4
    
>>> partition_range(3)
[[0], [1], [2]]
>>> partition_range(5)
[[0], [1], [2], [3, 4]]
>>> partition_range(8)
[[0, 1], [2, 3], [4, 5], [6, 7]]
>>> partition_range(12)
[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]]

    """
    lst = range(max_range)
    if max_range <= 4:
        return [[i] for i in lst]
    elif max_range == 5:
        L = [[i] for i in range(4)]
        L[3].append(4)
        return L
    elif max_range == 6:
        return [[0, 1], [2, 3], [4, 5]]
    elif max_range == 7:
        return [[0], [1, 2], [3, 4], [5, 6]]
    elif max_range == 8:
        return [[0, 1], [2, 3], [4, 5], [6, 7]]
    else:
        return [lst] # alle images achter elkaar, scrollen afhankelijk van de browser
    



        

def unravelList(menu):
    """unravel from menu list to dropdown list order
    
>>> unravelList([1, [2, [3, 4, 5], 6], 7, 8])
[[1, 7, 8], [2, 6], [3, 4, 5]]

    """
    L, M = [], None
    for elt in menu:
        if type(elt) == types.ListType:
            M = unravelList(elt)
        else:
            L.append(elt)
    if M and type(M) == types.ListType:
        M.insert(0, L)
        return M
    else:
        return [L]

reUnix=re.compile(r'[^\w-]')
def toUnixName(t, glueChar="", lowercase=1, canHaveExtension=1, canHaveFolders=1):
    """get rid of unwanted characters, only letters and '-'
    leading numbers get a _ in front

    default: all to lowercase, if lowercase = 0: convert extension to lowercase anyway

    default: file can have extension and folders. If set to 0, also \\, / and . are removed from name.

    split into folder/file parts if needed.
    
    glueChar can be "_" or "-" as well ("_" for avp, michel)

>>> toUnixName('')
Traceback (most recent call last):
ValueError: toUnixName, name has no valid characters: ||
>>> toUnixName('-abcd')
'_-abcd'

>>> toUnixName('aDc')
'adc'
>>> toUnixName('a.b-99? .d')
'a_b-99.d'
>>> toUnixName('a.b-99? .d', canHaveExtension=0)
'a_b-99_d'
>>> toUnixName('.a^.jpg')
'_a.jpg'
>>> toUnixName('6-barge.txt')
'_6-barge.txt'
>>> toUnixName('-6-barge.html')
'_-6-barge.html'

>>> toUnixName('D:/abc.def/-6-barge.html')
'D:/abc_def/_-6-barge.html'
>>> toUnixName('D:/abc.def/Thaddeus M'+chr(252)+'ller.html')
'D:/abc_def/thaddeusmuller.html'
>>>


    """
    t = os.path.normpath(t)
    t = t.replace('\\', '/')
    if canHaveFolders and t.find('/') >= 0:
        L  = []
        parts = t.split('/')
        for part in parts:
            
            if part  != parts[ - 1]:
                canHaveExtension2 = 0 # folder parts never extension
            else:
                canHaveExtension2 = canHaveExtension
            if lowercase and not (len(part) == 2 \
                               and part[-1] == ":"):
                part = part.lower()
            sofar = path('/'.join(L))/part
            if sofar.isdir():
                # prevent "website name" from being converted
                L.append(part)
                continue
            L.append(toUnixName(part,lowercase=lowercase, canHaveFolders=0,
                                canHaveExtension=canHaveExtension2))
        return '/'.join(L)

    if len(t) == 2 and t.endswith(":"):
        return t.upper()
    if t == "..":
        return t
    # now for the dir/file part:
    if canHaveExtension:
        trunk, ext = os.path.splitext(t)
    else:
        # also remove . and / (and \)
        trunk, ext = t, ''
    if glueChar == "_":
        trunk = fixdotslashspace(trunk) # . --> _ and / -->> _ also space to "_"
    elif glueChar:
        raise ValueError('toUnixName, glueChar may only be "" or "_", not "%s"'% glueChar)
    else:
        trunk = fixdotslash(trunk) # . --> _ and / -->> _
        
    trunk = normaliseaccentedchars(trunk)
    if lowercase:
        trunk = trunk.lower()

    # remove possible invalid chars from extension:
    if ext and ext[0] == ".":
        ext = "." + normaliseaccentedchars(ext[1:])
        ext = ext.lower()  # always to lowercase

    if not trunk:
        raise ValueError("toUnixName, name has no valid characters: |%s|"% trunk)
    if trunk[0] in '-0123456789':
        trunk = "_" + trunk
    return trunk + ext

str2unix = toUnixName

def sendkeys_escape(str):
    """escape with {} keys that have a special meaning in sendkeys
    + ^ % ~ { } [ ]

>>> sendkeys_escape('abcd')
'abcd'
>>> sendkeys_escape('+bcd')
'{+}bcd'
>>> sendkeys_escape('+a^b%c~d{f}g[h]i')
'{+}a{^}b{%}c{~}d{{}f{}}g{[}h{]}i'
>>> sendkeys_escape('+^%~{}[]')
'{+}{^}{%}{~}{{}{}}{[}{]}'

    """
    return ''.join(map(_sendkeys_escape, str))
def _sendkeys_escape(s):
    """Escape one character in the set or return if different"""
    if s in ('+', '^', '%', '~', '{' , '}' , '[' , ']' ) :
        return '{%s}' % s
    else:
        return s



##import sys, traceback
def print_exc_plus(filename=None, skiptypes=None, takemodules=None,
                   specials=None):
    """ Print the usual traceback information, followed by a listing of
    all the local variables in each frame.
    
    
    """
    #print 'specials:', specials
    # normal traceback:
    traceback.print_exc()
    tb = sys.exc_info()[2]
    while tb.tb_next:
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back
    stack.reverse()
    traceback.print_exc()
    L = []
    # keys that are in specialsSitegen are recorded in next array:
    specialsDict = {}
    push = L.append

    push('traceback date/time: %s'% time.asctime(time.localtime(time.time())))
    pagename = ''
    menuname = ''
    for frame in stack:
        if takemodules and not filter(None, [frame.f_code.co_filename.find(t) > 0 for t in takemodules]):
            continue
        functionname = frame.f_code.co_name
        push('\nFrame "%s" in %s at line %s' % (frame.f_code.co_name,
                                frame.f_code.co_filename,
                                frame.f_lineno))
        keys = []
        values = []
        for key, value in frame.f_locals.items():
            if key[0:2] == '__':
                continue
            try:
                v = repr(value)
            except:
                continue
            if skiptypes and filter(None, [v.find(s) == 1 for s in skiptypes]):
                continue
            keys.append(key)
            if functionname == 'go' and key == 'self':
                if v.find('Menu instance') > 0:
                    menuname = value.name
                    push('menu name: %s'% menuname)
            if functionname == 'makePage' and key == 'self':
                if v.find('Page instance') > 0:
                    pagename = value.name
                    push('page name: %s'% pagename)

            # we must _absolutely_ avoid propagating exceptions, and str(value)
            # COULD cause any exception, so we MUST catch any...:
            v = v.replace('\n', '|')
            values.append(v)
        if keys:
            maxlenkeys = max(15, max(map(len, keys)))
            allowedlength = 80-maxlenkeys
            kv = zip(keys, values)
            kv.sort()
            for k,v in kv:
                if v.startswith('<built-in method'):
                    continue
                if len(v) > allowedlength:
                    half = allowedlength/2
                    v = v[:half] + " ... " + v[-half:]
                push(k.rjust(maxlenkeys) + " = " + v)
    if specials:
        stack.reverse()
        for frame in stack:
            if 'self' in frame.f_locals:
                push('\ncontents of self (%s)'% repr(frame.f_locals['self']))
                inst = frame.f_locals['self']
                keys, values = [], []
                for key in dir(inst):
                    value = getattr(inst, key)
                    if key[0:2] == '__':
                        continue
                    try:
                        v = repr(value)
                    except:
                        continue
                    if skiptypes and filter(None, [v.find(s) == 1 for s in skiptypes]):
                        continue
                    # specials for eg sitegen
                    if specials and key in specials:
                        #print 'found specialskey: %s: %s'% (key, v)
                        specialsDict[key] = v
                    keys.append(key)
                    # we must _absolutely_ avoid propagating exceptions, and str(value)
                    # COULD cause any exception, so we MUST catch any...:
                    v = v.replace('\n', '|')
                    values.append(v)
                if not keys:
                    break
                maxlenkeys = max(15, max(map(len, keys)))
                allowedlength = 80-maxlenkeys
                for k,v in zip(keys, values):
                    if len(v) > allowedlength:
                        half = allowedlength/2
                        v = v[:half] + " ... " + v[-half:]
                    push(k.rjust(maxlenkeys) + " = " + v)
                break
            else:
                print 'no self of HTMLDoc found'

    callback = []

    if menuname:
        push('menu: %s'% menuname)
        callback.append('menu: %s'% menuname)
    elif pagename == 'index':
        push('menu: top')
        callback.append('menu: top')
        
    if pagename:
        push('page: %s'% pagename)
        callback.append('page: %s'% pagename)
    push('\ntype: %s, value: %s'% (sys.exc_info()[0], sys.exc_info()[1]))
    callback.append('error: %s'%sys.exc_info()[1])

    print '\nerror occurred:'
    callback = '\n'.join(callback)
    print callback

    sys.stderr.write('\n'.join(L))
    sys.stderr.write(callback)
    #print 'result specialsDict: %s'% specialsDict
    return callback, specialsDict

def cleanTraceback(tb, filesToSkip=None):
    """strip boilerplate in traceback (unittest)

    the purpose is to skip the lines "Traceback" (only if filesToSkip == True),
    and to skip traceback lines from modules that are in filesToSkip.

    in use with unimacro unittest and voicecode unittesting.

    filesToSkip are (can be "unittest.py" and "TestCaseWithHelpers.py"

    """
    L = tb.split('\n')
    snip = "  ..." # leaving a sign of the stripping!
    if filesToSkip:
        singleLineSkipping = ["Traceback (most recent call last):"]
    else:
        singleLineSkipping = None
    M = []
    skipNext = 0
    for line in L:
        # skip the traceback line:
        if singleLineSkipping and line in singleLineSkipping:
            continue
        # skip trace lines from one one the filesToSkip and the next one
        # UNLESS there are no leading spaces, in case we hit on the error line itself.
        if skipNext and line.startswith(" "):
            skipNext = 0
            continue
        if filesToSkip:
            for f in filesToSkip:
                if line.find(f + '", line') >= 0:
                    skipNext = 1
                    if M and  M[-1] == snip:
                        pass
                    else:
                        M.append(snip)
                    break
            else:
                skipNext = 0
                M.append(line)

    return '\n'.join(M)

    # calculate the relative path, if ffrom and fto are files (not directoryies)
def relpathdirs(ffrom, fto):
    """calculate the relative directory's

    >>> relpathdirs('a/b/c', 'a/d')
    '../../d'
    >>> relpathdirs(path('a/b/c'), 'a/d')
    '../../d'
    >>> relpathdirs(path('a/b/c'), path('a/d'))
    '../../d'
    >>> relpathdirs(path('a'), path('a'))
    ''
    >>> relpathdirs(path(''), path('a'))
    'a'
    >>> relpathdirs(path('a'), path(''))
    '..'
    >>> relpathdirs(path('.'), path('a'))
    'a'
    >>> relpathdirs(path('a'), path('.'))
    '..'


    """
    if type(ffrom) == types.StringType:
        ffrom = path(ffrom)
    if type(fto) == types.StringType:
        fto = path(fto)
    fromList = filter(None, ffrom.splitall())
    toList = filter(None, fto.splitall())
    if not toList:
        relpath = path(('../')*len(fromList))
        return relpath
    while fromList and toList and fromList[0] == toList[0]:
        fromList.pop(0)
        toList.pop(0)
    relpath = path('../'*len(fromList))/toList
    return relpath

def commonprefix(ffrom, fto):
    """collate the commonprefix of two folders
    >>> commonprefix('a/b/c', 'a/d')
    'a'
    >>> commonprefix(path('a'), path('a'))
    'a'
    >>> commonprefix(path(''), path('a'))
    ''

    """
    if type(ffrom) == types.StringType:
        ffrom = path(ffrom)
    if type(fto) == types.StringType:
        fto = path(fto)
    fromList = filter(None, ffrom.splitall())
    toList = filter(None, fto.splitall())
    common = []
    while fromList and toList and fromList[0] == toList[0]:
        common.append(fromList.pop(0))
        toList.pop(0)
    return '/'.join(common)

# calculate the relative path, if ffrom and fto are files (not directoryies)
def relpathfiles(ffrom, fto):
    """calculate the relative files (tail1 is irrelevant)

    ffrom and fto are (if necessary) converted to path instances

    >>> relpathfiles('a/b/c/t.txt', 'a/d/a.txt')
    '../../d/a.txt'
    >>> relpathfiles('a/t.txt', 'a/a.txt')
    'a.txt'


    """
    if type(ffrom) == types.StringType:
        ffrom = path(ffrom)
    if type(fto) == types.StringType:
        fto = path(fto)

    head1, tail1 = ffrom.split()
    head2, tail2 = fto.split()
    if tail1 and tail2:
        return relpathdirs(head1,head2)/tail2
    else:
        return 'fout, tail1 of tail2 leeg'

#
foundHandle = None
def getWindowWithTitle(wantedTitle, checkendstring=None):
    """find window that has the exact title. For kontrol
    check can be "endstring", look for endstring.

    """
    global foundHandle
    foundHandle = None
    if checkendstring:
        EnumWindows(lookForWindowTextEnd, wantedTitle)
    else:
        EnumWindows(lookForWindowText, wantedTitle)

    return foundHandle

def isValidWindow(hndle):
    try:
        testHndle = GetWindow(hndle, 0)
    except pywintypes.error, details:
        if details[0] == 1400:
            return
    return testHndle

def GetProcIdFromWnd(wHndle):
    """from window handle to proc id
    """
    parent = wHndle
    testHndle = isValidWindow(wHndle)
    if not testHndle:
        print 'no window with hndle: %s'% wHndle
        return
    print 'testHndle: %s'% testHndle
    while 1:
        nextParent = GetParent(parent)
        if nextParent == 0 or nextParent == parent: break
        parent = nextParent
    wHndle = parent
    pHndle, parent = GetWindowThreadProcessId(wHndle)
    print 'pHndle: %s, parent: %s (window handle: %s)'% (pHndle, parent, wHndle)
    return pHndle

def killProcess(pHndle):
    PROCESS_TERMINATE = 1
    handle = OpenProcess(PROCESS_TERMINATE, 0, pHndle)
    print 'handle to kill: %s'% handle
    TerminateProcess(handle, -1)
    CloseHandle(handle)


def lookForWindowTextEnd(hwnd, text):
    global foundHandle

    if GetWindowText(hwnd).strip().endswith(text):
        foundHandle = hwnd
        return
    return 1



def lookForWindowText(hwnd, text, endstring):
    global foundHandle
    if GetWindowText(hwnd).strip() == text:
        foundHandle = hwnd
        return
    return 1

if sys.platform != 'linux2':

    def getIEProcesses(filterClasses=None):
        """get running IE, my computer and explorer processes
        ### getIEProcesses() return something like:
    
        [('projects', 'file:///D:/projects', 262740, 'CabinetWClass'),
        ('Google', 'http://www.google.nl/', 394500, 'IEFrame'),
        ('Google', 'http://www.google.nl/', 2360846, 'IEFrame'),
        ('My Documents', 'file:///D:/Mijn%20documenten', 198480, 'ExploreWClass')]
    
        each tuple being (LocationName, LocationURL, hwnd, ClassName)
    
        ClassName:
            CabinetWClass == my computer
            ExploreWClass == Windows Explorer
            IEFrame == Internet Explorer
    
    ###>>> getIEProcesses()
    ###>>> getIEProcesses(filterClasses=['IEFrame'])
    
        """
        ShellWindowsCLSID = '{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'
        ShellWindows = win32com.client.Dispatch(ShellWindowsCLSID)
        L = []
        for s in ShellWindows :
            if str(s).startswith('Microsoft Internet Explorer'):
    ##            print '-'*40
    ##            print s
    ##            print s.LocationName
    ##            print s.LocationURL
    ##            print s.HWND
    ##            print GetClassName(s.HWND)
                ClassName = GetClassName(s.HWND)
                if filterClasses and ClassName not in filterClasses:
                    continue
                try:
                    L.append((str(s.LocationName), str(s.LocationURL), s.HWND, ))
                except UnicodeEncodeError:
                    pass # leave these alone
        return L


# Utility functions QH softwaretraining & advies
#
# Uses python 2.2 and higher, because of sting functions
# and generator functions.

def getSublists(L, maxLen, sepLen):
    """generator function, that gives pieces of the list, up to
    the maximum length, accounting for the separator length
    """
    if not L:
        yield L
        return
    listPart = [L[0]]
    lenPart = len(L[0])
    for w in L[1:]:
        lw = len(w)
        if lw + lenPart > maxLen:
            yield listPart
            listPart = [w]
            lenPart = lw
        else:
            lenPart += lw + sepLen
            listPart.append(w)
    yield listPart

def getWordsUntilLength(t, maxLength):
    """take words until maxLength is reached
>>> getWordsUntilLength('this is a test', 60)
'this is a test'
>>> getWordsUntilLength('this is a test', 7)
'this is'
>>> getWordsUntilLength('this is a test', 2)
'this'
    
    
    """
    t = t.replace(',', '')
    t = t.replace('.', '')
    T = t.split()
    while T:
        t = ' '.join(T)
        if len(t) <= maxLength:
            return t
        T.pop()
    else:
        # return first word
        return t

def splitLongString(S, maxLen=70, prefix='', prefixOnlyFirstLine=0):
    """Splits a (long) string into newline separated parts,

    a list of strings is returned.

    possibly with a fixed prefix, or a prefix for the first line only.
    Possibly items inside the line are separated by a given separator

    maxLen = maximum line length, can be exceeded is a very long word is there
    prefix = text that is inserted in front of each line, default ''
    prefixOnlyFirstLine = 1: following lines as blank prefix, default 0
    >>> splitLongString('foo', 80)
    ['foo']
    >>> splitLongString(' foo   bar and another set of  words  ', 80)
    ['foo bar and another set of words']
    >>> splitLongString(' foo   bar and another set of  words  ', 20,
    ... prefix='    # ')
    ['    # foo bar and', '    # another set of', '    # words']
    >>> splitLongString(' foo   bar and another set of  words  ', 20,
    ... prefix='entry = ', prefixOnlyFirstLine=1)
    ['entry = foo bar and', '        another set', '        of words']
    """
    assert type(S) == types.StringType
    L = map(string.strip, S.split())
    lOut = []
    for part in getSublists(L, maxLen=maxLen-len(prefix), sepLen=1):
        lOut.append(prefix + ' '.join(part))
        if prefixOnlyFirstLine:
            prefix = ' '*len(prefix)
    return lOut



def cleanString(s):
    """converts a string with leading and trailing and
    intermittent whitespace into a string that is stripped
    and has only single spaces between words
    >>> cleanString('foo bar')
    'foo bar'
    >>> cleanString('foo  bar')
    'foo bar'
    >>> cleanString('\\n foo \\n\\n  bar ')
    'foo bar'
    >>> cleanString('')
    ''

    """
    return ' '.join(map(lambda x: x.strip(), s.split()))

def formatListColumns(List, lineLen = 70, sort = 0):
    """formats a list in columns

    Uses a generator function "splitList", that gives a sequence of
    sub lists of length n.

    The items are separated by at least two spaces, if the list
    can be placed on one line, the list is comma separated

    >>> formatListColumns([''])
    ''
    >>> formatListColumns(['a','b'])
    'a, b'
    >>> formatListColumns(['foo', 'bar', 'longer entry'], lineLen=5)
    'foo\\nbar\\nlonger entry'
    >>> formatListColumns(['foo', 'bar', 'longer entry'], lineLen=5, sort=1)
    'bar\\nfoo\\nlonger entry'
    >>> print formatListColumns(['afoo', 'bar', 'clonger', 'dmore', 'else', 'ftest'], lineLen=20, sort=1)
    afoo      dmore
    bar       else
    clonger   ftest
    >>> print formatListColumns(['foo', 'bar', 'longer entry'], lineLen=20)
    foo   longer entry
    bar

    """
    if sort:
        List.sort(caseIndependentSort)
    s = ', '.join(List)

    # short list, simply join with comma space:
    if len(s) <= lineLen:
        return s

    maxLen = max(map(len, List))

    # too long elements in list, return "\n" separated string:
    if maxLen > lineLen:
        return '\n'.join(List)


    nRow = len(s)/lineLen + 1
    lenList = len(List)

    # try for successive number of rows:
    while nRow < lenList/2 + 2:
        lines = []
        for i in range(nRow):
            lines.append([])
        maxLenTotal = 0
        for parts in splitList(List, nRow):
            maxLenParts = max(map(len, parts)) + 2
            maxLenTotal += maxLenParts
            for i in range(len(parts)):
                lines[i].append(parts[i].ljust(maxLenParts))
        if maxLenTotal > lineLen:
            nRow += 1
        else:
            return '\n'.join(map(string.strip, map(string.join, lines)))
    else:
        # unexpected long list:
        return '\n'.join(List)

hasDoubleQuotes = re.compile(r'^".*"$')
hasSingleQuotes = re.compile(r"^'.*'$")

def convertToPythonArgs(text):
    """convert to numbers and strings,

    IF argument is enclosed in " " or ' ' it is kept as a string.
    

    """    
    text = text.strip()
    if not text:
        return    # None
    L = text.split(',')
    L = map(_convertToPythonArg, L)
    return tuple(L)

def convertToPythonArgsKwargs(text):
    """convert to numbers and strings,

    IF argument is enclosed in " " or ' ' it is kept as a string.

    also do kwargs now...
>>> convertToPythonArgsKwargs('')
((), {})
>>> convertToPythonArgsKwargs('hello')
(('hello',), {})
>>> convertToPythonArgsKwargs('width=50')
((), {'width': 50})
>>> convertToPythonArgsKwargs('"hello", width=50')
(('hello',), {'width': 50})

    

    """
    L = []
    K = {}
    text = text.strip()
    if not text:
        return    tuple(L), K  # None
    textList = text.split(',')
    for arg in textList:
        if arg.find("=") > 0:
            kw, arg2 = map(string.strip, arg.split("=", 1))
            if kw.find(" ") == -1:
                arg2 = _convertToPythonArg(arg2)
                K[kw] = arg2
            else:
                L.append(arg.strip())
        else:
            L.append(_convertToPythonArg(arg))
    return tuple(L), K

def _convertToPythonArg(t):
    t = t.strip()
    if not t: return ''

    # if input string is a number, return string directly
    try:
        i = int(t)
        if t == '0':
            return 0
        if t.startswith('0'):
            print 'warning convertToPythonArg, could be int, but assume string: %s'% t
            return '%s'% t
        return i
    except ValueError:
        pass
    try:
        f = float(t)
        if t.find(".") >= 0:
            return f
        else:
            print 'warning convertToPythonArg, can be float, but assume string: %s'% t
            return '%s'% t
    except ValueError:
        pass

    # now proceeding with strings:    
    if hasDoubleQuotes.match(t):
        return t[1:-1]
    elif hasSingleQuotes.match(t):
        return t[1:-1]
    else:
        return t
##    elif hasDoubleQuote.search(t):
##        return "'%s'"% t
##    else:
##        return '"%s"'% t
        


def caseIndependentSort(a,b):
    """sort alphabetically, all converted to lower case

    """

    a, b = string.lower(a), string.lower(b)
    return cmp(a, b)

def splitList(L, n):
    """generator function that splits a list in sublists of length n

    """
    O = []
    for l in L:
        O.append(l)
        if len(O) == n:
            yield O
            O = []
    if O:
        yield O

def opj(*args):
    """smart os.path.join function, can accept also list/tuple

    always returns "/" instead of os.sep
    and returns a path instance!

    >>> opj('')
    ''
    >>> opj('a')
    'a'
    >>> opj('a', 'b')
    'a/b'
    >>> opj(['a', 'b'])
    'a/b'
    >>> str(opj(['a', ('..', 'b', '..', 'c'), 'b']))
    'c/b'
    >>> opj(['a', ('..', 'b', '..', 'c'), 'b'])
    'c/b'
    >>> p = opj(['a', 'b', '..', '.'], 'd/e/f/.././g')
    >>> p
    'a/d/e/g'
    >>> str(p)
    'a/d/e/g'
    """
    if not args:
        return ''
    l = []
    for a in args:
        if not a:
            continue
        elif isStringLike(a):
            l.append(a)
        elif type(a) == types.ListType:
            l.append(apply(opj, tuple(a)))
        elif type(a) == types.TupleType:
            l.append(apply(opj, a))
        else:
            raise SitegenError('invalid type for opj: %s'% `a`)
    if not l:
        return ''
    return path('/'.join(l))
##    if os.sep == '\\' and string.find(p, '\\'):
##        return string.replace(p, '\\', '/')
##    else:
##        return p
reNumberLike = re.compile(r'^[0-9.,]+$')
def looksLikeNumber(t):
    """string looks like int or float, return 1
>>> looksLikeNumber('1')
1
>>> looksLikeNumber('')
>>> looksLikeNumber('0.3')
1
>>> looksLikeNumber('3.45a')

>>> looksLikeNumber('36,45')
1
>>> looksLikeNumber('36/37.5')
1
>>> looksLikeNumber('36 / 37.5')
1
>>> looksLikeNumber('3-5,7')
1
>>> looksLikeNumber('3.456/7,57')
1
>>> looksLikeNumber('3.456b/c7,57')


    """
    t = str(t).strip()

    for sep in '-', '/':
        if sep in t:
            res = None
            for T in t.split(sep):
                res = looksLikeNumber(T.strip()) or res
            return res

    if reNumberLike.match(t):
        return 1



def isStringLike(anobj):
    """test is an object is string like

    See python cookbook 3.2
    >>> isStringLike('')
    1
    >>> isStringLike(0)
    0
    >>> isStringLike(path('a/b/c'))
    1
    >>> isStringLike(['a'])
    0
    """
    try: anobj + ''
    except: return 0
    return 1

def checkFolderExistence(*args):
    """raises error if folder not valid (mostly non-existent)

    arguments can be a string (giving the path of the folder),
    a list or a tuple of these, or several of previous things

    If all is okay, this function returns silent,
    otherwise raises OSError


    """
    for a in args:
        if not a:
            continue
        elif type(a) == types.StringType:
            if os.path.isdir(a):
                pass
            elif os.path.exists(a):
                raise OSError, 'path exists, but is not a folder: %s'% a
            else:
                raise OSError, 'folder does not exist: %s'% a

        elif type(a) == types.ListType:
            apply(checkFolderExistence, tuple(a))
        elif type(a) == types.TupleType:
            apply(checkFolderExistence, a)
        else:
            raise Exception('invalid type for checkFolderExistence: %s'% `a`)

def checkFileExistence(folderOrPath, *args):
    """raises error if file not valid (mostly non-existent)

    first argument is the folder, the rest
    can be a string (giving the path of the folder),
    a list or a tuple of these, or several of previous things


    each time the folder is joined with the file part and checked

    If all is okay, this function returns silent,
    otherwise raises OSError

    >>> folderName = testdrive + '/qhtemp'
    >>> makeEmptyFolder(folderName)
    >>> touch(folderName, "a.ini", "b.ini")
    >>> checkFileExistence(folderName, 'a.ini')
    >>> checkFileExistence(folderName, ['a.ini'])
    >>> checkFileExistence(folderName, ('a.ini', 'b.ini'))
    >>> checkFileExistence(folderName, ('a.ini', 'b.ini'))
    >>> listOfNames = [os.path.join(folderName, 'a.ini'), os.path.join(folderName, 'b.ini')]
    >>> checkFileExistence(listOfNames)


    """
    if not args:
        p = folderOrPath
        if isStringLike(p):
            p = str(p)
            if os.path.isfile(p):
                return
            elif os.path.exists(p):
                raise OSError, 'path exists, but is not a file: %s'% p
            else:
                raise OSError, 'file does not exist: %s'% p
        elif type(p) == types.ListType or type(p) == types.TupleType:
            for P in p:
                checkFileExistence(P)
            return

    # now process the other arguments, folderOrPath must be a folder
    folder = folderOrPath
    checkFolderExistence(folder)  # raises error if folder is not a valid folder
    for a in args:
        if not a:
            continue
        elif type(a) == types.StringType:
            checkFileExistence(os.path.join(folder, a))
        elif type(a) == types.ListType or type(a) == types.TupleType:
            for A in a:
                checkFileExistence(folder, A)
        else:
            raise Exception('invalid type for checkFileExistence: %s'% `a`)

def makeEmptyFolder(*args):
    """delete a folder and creates it again

    arguments can be a string (giving the path of the folder),
    a list or a tuple of these, or several of previous things

    if all goes well, action is performed.  If something goes wrong
    an OSError is raised

    >>> folderName = testdrive + '/qhtemp'
    >>> try: shutil.rmtree(folderName)
    ... except OSError: pass
    >>> makeEmptyFolder(folderName)
    >>> os.listdir(folderName)
    []
    >>> makeEmptyFolder(folderName)
    >>> os.listdir(folderName)
    []
    >>> makeEmptyFolder(folderName, folderName)
    >>> os.listdir(folderName)
    []
    >>> makeEmptyFolder([folderName])
    >>> os.listdir(folderName)
    []

    """
    for a in args:
        if not a:
            continue
        if isStringLike(a):
            a = str(a).replace('\\', '/') # make outside path instances!
        if isStringLike(a):
            if os.path.isdir(a):
                if os.path.isdir(a):
                    shutil.rmtree(a)
                if os.path.exists(a):
                    raise OSError, 'path already exists, but is not a folder, or could not be deleted: %s'% a
            os.mkdir(a)

        elif type(a) == types.ListType:
            apply(makeEmptyFolder, tuple(a))
        elif type(a) == types.TupleType:
            apply(makeEmptyFolder, a)
        else:
            raise Exception('invalid type for makeEmptyFolder: %s'% `a`)


def createFolderIfNotExistent(*args):
    """create a folder if it doesn't exist yet

    arguments can be a string (giving the path of the folder),
    a list or a tuple of these, or several of previous things

    if all goes well, action is performed.  If something goes wrong
    an OSError is raised

    >>> folderName = path(testdrive + '/qhtemp')
    >>> try: folderName.rmtree()
    ... except OSError: pass
    >>> createFolderIfNotExistent(folderName)
    >>> os.listdir(folderName)
    []
    >>> createFolderIfNotExistent(folderName)
    >>> os.listdir(folderName)
    []

    """
    for a in args:
        if isStringLike(a):
            a = str(a) # make outside path instances!
        if not a:
            continue
        elif isStringLike(a):
            if os.path.isdir(a):
                continue
            elif os.path.exists(a):
                raise OSError, 'path already exists, but is not a folder: %s'% a
            else:
                try:
                    os.mkdir(a)
                except OSError:
                    try:
                        os.makedirs(a)
                    except OSError:
                        raise OSError, 'cannot create folder: %s'% a

        elif type(a) == types.ListType:
            apply(createIfNotExistent, tuple(a))
        elif type(a) == types.TupleType:
            apply(createIfNotExistent, a)
        else:
            raise Exception('invalid type for createIfNotExistent: %s'% `a`)

def touch(folder, *args):
    """touches a file, in a given folder

    a file doesn't exist before an empty file is created,
    otherwise the modification date/time is set

    if only one argument is given, this must be the complete path,
    or a sequence (list or tuple) of full paths.

    is more arguments are given,p first argument is the folder,
    the rest can be a string (giving the path of the folder),
    a list or a tuple of these, or several of previous things


    each time the folder is joined with the file part and touched

    If all is okay, this function returns silent,
    otherwise raises OSError
    >>> folderName = testdrive + '/qhtemp'
    >>> makeEmptyFolder(folderName)
    >>> touch(folderName, 'a.ini')
    >>> os.listdir(folderName)
    ['a.ini']
    >>> touch(folderName, ['a.ini'])
    >>> os.listdir(folderName)
    ['a.ini']
    >>> touch(folderName, ('a.ini', 'b.ini'))
    >>> os.listdir(folderName)
    ['a.ini', 'b.ini']
    >>> listOfNames = [os.path.join(folderName, 'a.ini'), os.path.join(folderName, 'c.ini')]
    >>> touch(listOfNames)
    >>> sorted(os.listdir(folderName))
    ['a.ini', 'b.ini', 'c.ini']



    """
    if isStringLike(folder):
        folder = str(folder).replace('\\', '/')

    if not args:
        # Only one argument, folder is the whole path!
        # skip folders
        if isStringLike(folder):
            if os.path.exists(folder):
                if os.path.isfile(folder):
                    os.utime(folder, None)  #skip folders!
            else:
                fsock = open(folder, 'w')
                fsock.close()

        elif type(folder) == types.ListType or type(folder) == types.TupleType:
            for f in folder:
                touch(f)
        return

    for a in args:
        if not a:
            continue
        elif type(a) == types.StringType:
            p = os.path.join(folder, a)
            touch(p)

        elif type(a) == types.ListType or type(a) == types.TupleType:
            for A in a:
                p = os.path.join(folder, A)
                touch(p)
        else:
            raise Exception('invalid type for touch is: %s'% `a`)

##def isOutOfDate(newer, older):
##    """check if out is newer than in
##    >>> folderName = path(testdrive + '/qhtemp')
##    >>> makeEmptyFolder(folderName)
##    >>> touch(folderName, 'older.ini')
##    >>> time.sleep(1)
##    >>> touch(folderName, 'newer.ini')
##
##    if out is newer, OutOfDate:
##    >>> isOutOfDate(folderName/'older.ini', folderName/'newer.ini')
##    True
##    >>> isOutOfDate(folderName/'newer.ini', folderName/'older.ini')
##    True
##
##    notexist (out) does not exist, not OutOfDate
##    >>> isOutOfDate(folderName/'older.ini', folderName/'notexist.ini')
##    True
##
##    notexist (inf) does not exist, OutOfDate:
##    >>> isOutOfDate(folderName/'notexist.ini', folderName/'newer.ini')
##    True
##
##    """
##    dateIn = getFileDate(inf)
##    dateOut = getFileDate(out)
##    return dateOut > dateIn

def copyIfOutOfDate(inf, out, reverse=None):
    """copy if section file is out of date

    Copy file from source to object, if object is nonexistent,
    or source has been changed more recently than object.
    folders must exist before.
    """
##    If target is more recent "reverse" comes into action:
##        if reverse = true, the reverse action is performed (without prompt)
##        if reverse = false, a QHError is raised,
##        if reverse is a function, the result can be
##            "y", reverse action is done
##            "n", reverse action is not done
##            other: a QHError is raised.
##
##        the "reverse" function is called with text as first variable.
##
##    >>> folderName = testdrive + '/qhtemp'
##    >>> folderName2 = testdrive + '/qhtemp\\notexist'
##    >>> makeEmptyFolder(folderName)
##    >>> touch(folderName, 'a.ini')
##    >>> copyIfOutOfDate(opj(folderName, 'a.ini'), opj(folderName, 'b.ini'))
##    copied file c:/qhtemp/a.ini to c:/qhtemp/b.ini
##    >>> copyIfOutOfDate(opj(folderName, 'a.ini'), opj(folderName, 'b.ini'))
##    >>> copyIfOutOfDate(opj(folderName, 'b.ini'), opj(folderName, 'a.ini'))
##
##    >>> import time
##    >>> time.sleep(3)
##    >>> touch(opj(folderName, 'b.ini'))
##    >>> copyIfOutOfDate(opj(folderName, 'a.ini'), opj(folderName, 'b.ini'))
##    Traceback (most recent call last):
##    QHError: copyIfOutOfDate: target c:/qhtemp/b.ini is newer than source: c:/qhtemp/a.ini
##
##    >>> copyIfOutOfDate(opj(folderName, 'a.ini'), opj(folderName, 'b.ini'), reverse=1)
##    copied file c:/qhtemp/b.ini to c:/qhtemp/a.ini
##
##    now call with 2 utility functions revTrue (giving "y"), revFalse (returning "n")
##    and revAbort (returning something else)
##
##    >>> time.sleep(3)
##    >>> touch(opj(folderName, 'b.ini'))
##    >>> copyIfOutOfDate(opj(folderName, 'a.ini'), opj(folderName, 'b.ini'), reverse=revAbort)
##    Traceback (most recent call last):
##    QHError: copyIfOutOfDate: target c:/qhtemp/b.ini is newer than source: c:/qhtemp/a.ini
##    >>> copyIfOutOfDate(opj(folderName, 'a.ini'), opj(folderName, 'b.ini'), reverse=revFalse)
##    >>> copyIfOutOfDate(opj(folderName, 'a.ini'), opj(folderName, 'b.ini'), reverse=revTrue)
##    copied file c:/qhtemp/b.ini to c:/qhtemp/a.ini
##
##    After the last call the dates are equal again:
##
##    >>> copyIfOutOfDate(opj(folderName, 'a.ini'), opj(folderName, 'b.ini'))
##
##
##
##
##
##    """
    dateIn = getFileDate(inf)
    dateOut = getFileDate(out)
    if not (dateIn or dateOut):
        infstr = str(inf)
        outstr = str(out)

        raise QHError('Cannot copy files, input "%s" and "%s" both do not exist\n\nWaarschijnlijk heb je een tikfout gemaakt bij het invoeren van de bestandsnaam.\n'% (infstr, outstr))
    if abs(dateIn - dateOut) < 0.00001:
        return  # OK
    elif dateIn > dateOut:
        try:
            shutil.copy2(inf, out)
        except (IOError, OSError):
            exc_value = sys.exc_info()[1]

            raise QHError('Cannot copy file %s to %s\n\nMogelijk is de uitvoerfile geopend. Soms moet je de computer opnieuw starten om deze melding kwijt te raken.\n\nMessage: %s' % (inf, out, exc_value))
        print 'copied file %s to %s' % (inf, out)
    else:   # dateOut > dateIn!!
        if filecmp.cmp(inf, out):
            print 'dateOut > dateIn, but equal, changing timestamps to "now" of \n%s and \n%s'% (inf, out)
            touch(out)
            touch(inf)
            return
        
        if type(reverse) in (types.FunctionType, types.MethodType):
##            print 'func reverse: %s'% reverse
            p, shortname = os.path.split(inf)
            pr = 'file: %s\n\ntarget %s is newer than source: %s\n\ncopy target to source?\n\nDit is soms gevaarlijk. Kies "Nee" in twijfelgevallen en vraag zonodig QH.\n'% (shortname, out, inf)
            res = apply(reverse, (pr,))
            if res:
                try:
                    shutil.copy2(out, inf)
                except (IOError, OSError):
                    raise QHError('Cannot copy (back) file %s to %s\n\nWaarschijnlijk is de invoerfile geopend. Soms moet je de computer opnieuw starten om deze melding kwijt te raken.\n' % (inf, out))
        ##                print 'answer was y'
            else:
                return
        elif reverse:
            # do the reverse action, because dates are ok, this will trigger
            # no prompt...
            try:
                shutil.copy2(out, inf)
            except (IOError, OSError):
                raise QHError('Cannot copy (back) file %s to %s\n\nWaarschijnlijk is de invoerfile geopend. Soms moet je de computer opnieuw starten om deze melding kwijt te raken.\n' % (inf, out))

def checkIfOutOfDate(inputfiles, outputfile):
    """if inputfile or files are newer than outputfile, return true

>>> folderName = path(testdrive + '/qhtemp')
>>> makeEmptyFolder(folderName)
>>> touch(folderName, 'older.ini', 'a.ini', 'b.ini', 'c.ini')
>>> time.sleep(2)
>>> touch(folderName, 'a.ini', 'b.ini', 'c.ini')
>>> time.sleep(2)
>>> touch(folderName, 'newer.ini')
>>> a, b, c = folderName/'a.ini', folderName/'b.ini', folderName/'c.ini'
>>> older, newer = folderName/'older.ini', folderName/'newer.ini'
>>> checkIfOutOfDate(newer, a)
True
>>> checkIfOutOfDate(older, a)
False
>>> checkIfOutOfDate([newer, older, a], b)
True
>>> checkIfOutOfDate([c, a], newer)
False



    """
    outDate = getFileDate(outputfile)
    if isinstance(inputfiles, basestring):
        inDate = getFileDate(inputfiles)
        if inDate == 0:
            raise IOError("checkIfOutOfDate: inputfile not present: %s"% inputfiles)
        return inDate >= outDate
    else:
        for inp in inputfiles:
            inDate = getFileDate(inp)
            if inDate == 0:
                raise IOError("checkIfOutOfDate: inputfile not present: %s"% inp)
            if inDate >= outDate:
                return True
        else:
            return False


def getFileDate(fileName):
    """returns the date on a file or 0 if the file does not exist

    >>> getFileDate('xtfg.dnv')
    0
    >>> #getFileDate(testdrive + "\\sites/qh/qhhtml.rc")
    # 1072694718 (not testable, changes all the time!)
    """
    try:
        return int(round(os.path.getmtime(str(fileName))))
    except os.error:
        return 0

def setFileDate(fileName):
    """set current date/time to mtime of file
    """
    try:
        return os.path.getmtime(str(fileName))
    except os.error:
        return 0
        

def splitall(path):
    """split a path into all the parts
    see python cookbook 4.15

    >>> splitall('a/b/c')
    ['a', 'b', 'c']
    >>> splitall ('/a/b/c/')
    ['/', 'a', 'b', 'c']
    >>> splitall('')
    []
    >>> splitall('C:')
    ['C:']
    >>> splitall(testdrive + '\\\\')
    ['C:']
    >>> splitall(testdrive + '\\\\a')
    ['C:', 'a']
    >>> splitall('C:/a')
    ['C:', 'a']
    >>> splitall('a\\\\b')
    ['a', 'b']
    """
    allparts =[]
    path = path.replace('\\', '/')
    while 1:
        parts = os.path.split(path)
        
        if parts[0] == path:
            toInsert = cleanupDrive(path)
            allparts.insert(0, toInsert)
            break
        elif parts[1] == path:
            toInsert = cleanupDrive(path)
            allparts.insert(0, toInsert)
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return filter(None, allparts)

def cleanupDrive(path):
    """change :\ into : or :/ into : for windows drive letters
    windows only
    """
    if sys.platform == 'win32':
        if path.endswith(':\\') or path.endswith(':/'):
            return path[:-1]
    return path

class PathError(Exception): pass

class path(str):
    """helper class for path functions

    p.isdir, p.isfile, p.exists, p.isabs (absolute path), p.mtime (modification time),
    p.split (in dirpart, filepart),    p.splitext (trunk, extension), p.splitall (dirpart, trunk, ext)
    p.basename (filepart without directory),    p.normpath, p.remove,
    p.rename,   p.rmtree (folder), p.mkdir,  p.copy, p.touch,
    p.chdir, p.getcwd (changing and getting the working directory),
    p.glob(pattern="*", keepAbs=1, makePath=1)
    p.listdir(makePath=0) (giving all files in folder p)
    p.walk(functionToDo, keepAbs=1, makePath=0)
    p.internetformat, p.unix (for internet filenames)

    p.encodePath, p.decodePath: file (dir)  (for gui)

    See python cookbook 4.16
    >>> import sys
    >>> root = path(sys.prefix)
    >>> sitepkgs = root/'lib'/'site-packages'
    >>> sitepkgs
    'C:/Python25/lib/site-packages'
    >>> str(sitepkgs)
    'C:/Python25/lib/site-packages'
    >>> len(sitepkgs)
    29

    >>> sitepkgs.exists()
    True
    >>> sitepkgs.isdir()
    True
    >>> sitepkgs.isfile()
    False
    >>> file = root/'subfolder'/'trunc.txt'
    >>> file.split()
    ('C:/Python25/subfolder', 'trunc.txt')
    >>> file.splitext()
    ('C:/Python25/subfolder/trunc', '.txt')
    >>> file.splitall()
    ['C:', 'Python25', 'subfolder', 'trunc.txt']
    >>> file = root/'subfolder/trunc.txt'
    >>> file.split()
    ('C:/Python25/subfolder', 'trunc.txt')
    >>> file.splitext()
    ('C:/Python25/subfolder/trunc', '.txt')
    >>> L = file.splitall()
    >>> L
    ['C:', 'Python25', 'subfolder', 'trunc.txt']
    >>> path(L)
    'C:/Python25/subfolder/trunc.txt'
    >>> path(L[0])/L[1:]
    'C:/Python25/subfolder/trunc.txt'

    >>> type(root)
    <class 'utilsqh.path'>
    >>> isStringLike(root)
    1
    >>> type(root/'test.txt')
    <class 'utilsqh.path'>
    >>> (root/'test.txt').isfile()
    False


    when a list is the constructor, the path is joined again:

    >>> L = path('C:/a/b/c.txt').splitall()
    >>> m = path(L)
    >>> m
    'C:/a/b/c.txt'



    """
    def __new__(self, val):
        """this is the constructor for in new instance!

        Perform the additional checks and only work with "/"

        small cases:

        >>> path('')
        ''
        >>> path('.')
        ''
        >>> path('/')
        '/'
        >>> path('../..')
        '../..'
        >>> path('../../')
        '../..'
        >>> path('C:/')
        'C:/'
        >>> path('C:')
        'C:/'

        """


        if type(val) == types.ListType or type(val) == types.TupleType:
            v = '/'.join(val).replace('//', '/')
            v = os.path.normpath(v).replace('\\', '/')
        else:
            try:
                v = os.path.normpath(str(val)).replace('\\', '/')
            except UnicodeEncodeError:
                print 'cannot convert unicode into string: %s'% val
                raise
        while v.endswith('/.'):
            v = v[:-2]
        while v.startswith('./'):
            v = v[2:]
        if v == '.':
            v = ''
        if v.endswith(":"):
            v += "/"
        if len(v) > 1 and v[1] == ':':
            v = v[0].upper() + v[1:]
        return str.__new__(self, v)

    #def __str__(self):
    #    return str.__str__(self)

    def __eq__(self, other):
        """compare normalised paths
>>> path(testdrive + r"\\abd\\def.ini") == testdrive + r"\\abd\\def.ini"
True
>>> path(testdrive + r"\\abd\\def.ini") == path(testdrive + r"/abd/def.ini")
True
>>> path(testdrive + r"\\abd\\def.ini") == path(testdrive + r"/other")
False


        """
        if not isinstance(other, self.__class__):
            if isinstance(other, basestring):
                other = path(other)
        return str(self).lower() == str(other).lower()


    def __div__(self, other):
        """make new instance with "/" operator

        >>> v = path('c:/f')
        >>> v/''
        'C:/f'
        >>> v/'a/b/'
        'C:/f/a/b'
        >>> v/'.'
        'C:/f'

        side cases, in use with relpathdirs and relpathfiles:

        >>> path('../'*1)/['a', 'b']
        '../a/b'
        >>> path('../'*2)/[]
        '../..'
        >>> path('../'*1)/['']
        '..'
        >>> path('../'*0)/[]
        ''
        >>> path('../'*0)/['a','b']
        'a/b'

        """
        if not self:
##            print 'path div, not self or .: return other'
            return path(other)
        elif other:
            if type(other) == types.ListType or type(other) == types.TupleType:
                com = os.path.join(str(self), '/'.join(other))
            else:
                com = os.path.join(str(self), str(other))
            return path(com)
        else:
            return self

    def __add__(self, other):
        """make new instance just adding the string

        >>> v = path('abc')
        >>> v += 'd'
        >>> v
        'abcd'

        but only in the last part of the path. If "/" is found in 2nd part, then error
        >>> path('a/b/c') + 'd'
        'a/b/cd'
        >>> path('a/b') + 'd/e.txt'
        Traceback (most recent call last):
        PathError: no addition in path parts allowed a/b + d/e.txt

        >>> v + 'xyz'
        'abcdxyz'
        >>> type(v)
        <class 'utilsqh.path'>


        """
        if other.find('/') >= 0 or other.find('\\') >= 0:
            raise PathError('no addition in path parts allowed %s + %s'% (self, path(other)))
        return path(str(self) + str(other))

    def replace(self, tin, tout):
        """replace function works on strings
>>> v = path('abc')
>>> b = path('b')
>>> x = path('xxx')
>>> v.replace(b, x)
'axxxc'


        """
        V = str(self).replace(str(tin), str(tout))
        return path(V)

    def mtime(self):
        """give mod time"""
        return getFileDate(str(self))

    def isdir(self):
        """wrapper for os.path functions"""
        return os.path.isdir(self)
    def exists(self):
        """wrapper for os.path functions"""
        return os.path.exists(self)
    def isfile(self):
        """wrapper for os.path functions"""
        return os.path.isfile(self)
    def isabs(self):
        """wrapper for os.path functions"""
        return os.path.isabs(self)
    def split(self):
        """wrapper for os.path.split, returns path(first) and str(second)
        """
        s = os.path.split(str(self))
        return path(s[0]), s[1]
    def splitdirslisttrunkext(self):
        """split into a list of directory parts, the file trunk and the file extension
        """
        L = self.splitall()
        if not L:
            return [], "", ""
        if len(L) == 1:
            trunk, ext = os.path.splitext(L[0])
            return [], trunk, ext
        else:
            trunk, ext = os.path.splitext(L[-1])
            return L[:-1], trunk, ext
            
    def splitext(self):
        return os.path.splitext(str(self))
    def splitall(self):
        """return list of all parts"""
        L = str(self).split('/')
        return L
    def basename(self):
        """gives basename

        >>> path(testdrive + r"/a/bcd.txt").basename()
        'bcd.txt'
        """
        return path(os.path.basename(str(self)))

    def normpath(self):
        """ return normalised path as string
        """
        return os.path.normpath(str(self))

    def remove(self):
        """removal of file

        """
        if self.isfile():
            os.remove(str(self))
        else:
            raise PathError('remove only for files, not for: %s'% (self))

    def rename(self, other):
        """rename
        """
        os.rename(str(self), str(other))

    def rmtree(self, ignore=None):
        """remove whole folder tree
        possibly ignoring items from a list ([".svn"]) as folder names


        """
        if self.isdir():
            if ignore:
                for f in self.listdir():
                    f2 = self/f
                    if f2.isdir():
                        if f in ignore:
                            continue
                        else:
                            f2.rmtree(ignore=ignore)
                    else:
                        f2.remove()
            else:
                shutil.rmtree(str(self))
        elif self.exists():
            raise PathError('rmtree only for folders, not for: %s'% (self))
        else:
            raise PathError('output folder does not exist: %s'% (self))

    def mkdir(self, newpath=None):
        """make new folder


        """
        if newpath:
            createFolderIfNotExistent(self/newpath)
        else:
            createFolderIfNotExistent(self)

    def copy(self, out):
        """copy file"""
        if self.isfile():
            try:
                shutil.copy2(str(self), str(out))
            except OSError:
                raise PathError('cannot copy file %s to %s' % (self, out))
        elif self.isdir():
            if path(out).isdir():
                try:
                    shutil.rmtree(str(out))
                except OSError:
                    raise PathError('cannot remove previous dir: %s' % out)
            try:
                shutil.copytree(str(self), str(out))
            except OSError:
                raise PathError('cannot copy folder %s to %s' % (self, out))


    def copywithoutsvn(self, outPath):
        """copy file, leave svn intact"""
        outPath = path(outPath)
        if outPath.isdir():
            outPath.rmtree(ignore=[".svn"])
        else:
            outPath.mkdir()

        allFiles = self.listdir()
        for f in allFiles:
            if (self/f).isdir():
                if f == '.svn':
                    continue
                subdir = self/f
                subOut = outPath/f
                subdir.copywithoutsvn(subOut)
            else:
                (self/f).copy(outPath/f)

    def touch(self):
        """mark file or touch date
        >>> p = path('c:/aaa.txt')
        >>> p.touch()
        >>> p.isfile()
        True
        >>> p.remove()
        >>> p.isfile()
        False
        """
        touch(self)

    def chdir(self):
        """change directory

>>> makeEmptyFolder('C:/temp')
>>> p = path('c:/temp')
>>> p.chdir()
>>> p.getcwd()
'C:/temp'


        """
        os.chdir(str(self))

    def getcwd(self):
        """get working directory

        see above"""
        return path(os.getcwd())

    def glob(self, pattern="*", keepAbs=1, makePath=1):
        """glob a path, default = "*"

        default options: give absolute paths as path instances
        Use listdir if you want all files relative to the path


>>> folderName = path(testdrive + '/qhtemp')
>>> makeEmptyFolder(folderName)
>>> touch(folderName, 'a.ini', 'b.txt')
>>> g = folderName.glob()
>>> g
['C:/qhtemp/a.ini', 'C:/qhtemp/b.txt']
>>> type(g[0])
<class 'utilsqh.path'>
>>> g = folderName.glob('*.txt', keepAbs=0)
>>> g
['b.txt']
>>> type(g[0])
<class 'utilsqh.path'>
>>> g = folderName.glob('*.txt', keepAbs=0, makePath=0)
>>> g
['b.txt']
>>> type(g[0])
<type 'str'>


        """
        if not self.isdir():
            raise PathError("glob must start with folder, not with: %s"% self)
        L = glob.glob(str(self/pattern))
        return self._manipulateList(L, keepAbs, makePath)

    def listdir(self):
        """give list relative to self, default strings, not path instances!

        >>> folderName = path(testdrive + '/qhtemp')
        >>> makeEmptyFolder(folderName)
        >>> touch(folderName, 'a.ini', 'b.txt')
        >>> L = path(folderName).listdir()
        >>> L
        ['a.ini', 'b.txt']
        >>> type(L[0])
        <type 'str'>

        """
        if not self.isdir():
            raise PathError("listdir only works on folders, not with: %s"% self)
        L = os.listdir(str(self))
        # note keepAbs is a formality here, listdir gives relative files only:
        return L


    def walk(self, functionToDo, keepAbs=1, makePath=0):
        """return the arg list when walking self

        assume arg is a list,
        functionToDo must use exactly 3 parameters,
        1 list "arg"
        2 dirname
        3 list of filenames
        path(testdrive + "/projects").walk(testWalk, keepAbs=1, makePath=0)

        optional parameters:
        keepAbs: 1 (default) do nothing with the resulting paths
                 0: strip off the prefix, being the calling instance
        makePath 0 (default) do not to do this
                 1: make the resulting items path instances

        setting up the files:

>>> folderName = path(testdrive + '/qhtemp')
>>> makeEmptyFolder(folderName)
>>> makeEmptyFolder(folderName/"afolder")
>>> makeEmptyFolder(folderName/"bfolder")
>>> touch(folderName, 'f.ini', 'ff.txt')
>>> touch(folderName/"afolder", 'aa.ini')
>>> touch(folderName/"bfolder", 'b.ini', 'bb.txt')

trying the first test walk:

>>> L = folderName.walk(testWalk)
>>> L
['C:/qhtemp', 'afolder', 'bfolder', 'f.ini', 'ff.txt', 'C:/qhtemp/afolder', 'aa.ini', 'C:/qhtemp/bfolder', 'b.ini', 'bb.txt']
>>> L = folderName.walk(testWalk, keepAbs=0)
Traceback (most recent call last):
PathError: path._manipulateList with keepAbs: 0, 7 items of the list do not have C:/qhtemp as start
>>> L = folderName.walk(testWalk, keepAbs=1, makePath=1)
>>> L
['C:/qhtemp', 'afolder', 'bfolder', 'f.ini', 'ff.txt', 'C:/qhtemp/afolder', 'aa.ini', 'C:/qhtemp/bfolder', 'b.ini', 'bb.txt']

trying the second test walk:

>>> folderName.walk(testWalk2, makePath=1)
['C:/qhtemp/afolder', 'C:/qhtemp/bfolder', 'C:/qhtemp/f.ini', 'C:/qhtemp/ff.txt', 'C:/qhtemp/afolder/aa.ini', 'C:/qhtemp/bfolder/b.ini', 'C:/qhtemp/bfolder/bb.txt']
>>> folderName.walk(testWalk2, keepAbs=0, makePath=1)
['afolder', 'bfolder', 'f.ini', 'ff.txt', 'afolder/aa.ini', 'bfolder/b.ini', 'bfolder/bb.txt']

third test, skip folders, note the list is path instances now,
converted back to strings or not by the parameter makePath:

>>> folderName.walk(walkOnlyFiles, makePath=1)
['C:/qhtemp/f.ini', 'C:/qhtemp/ff.txt', 'C:/qhtemp/afolder/aa.ini', 'C:/qhtemp/bfolder/b.ini', 'C:/qhtemp/bfolder/bb.txt']
>>> folderName.walk(walkOnlyFiles, keepAbs=0, makePath=1)
['f.ini', 'ff.txt', 'afolder/aa.ini', 'bfolder/b.ini', 'bfolder/bb.txt']


        """
        arg = []
        if not self.isdir():
            raise PathError("walk must start with folder, not with: %s"% self)
        os.path.walk(str(self), functionToDo, arg)
        return self._manipulateList(arg, keepAbs, makePath)

    def _manipulateList(self, List, keepAbs, makePath):
        """helper function for treating a result of listdir or glob

>>> folderName = path(testdrive + '/qhtemp')
>>> makeEmptyFolder(folderName)
>>> touch(folderName, 'a.ini', 'b.txt')
>>> L = [folderName/'a.ini', folderName/'b.txt']
>>> F = folderName._manipulateList(L, keepAbs=1, makePath=0)
>>> F
['C:/qhtemp/a.ini', 'C:/qhtemp/b.txt']
>>> type(F[0])
<type 'str'>
>>> F = folderName._manipulateList(L, keepAbs=1, makePath=1)
>>> F
['C:/qhtemp/a.ini', 'C:/qhtemp/b.txt']
>>> type(F[0])
<class 'utilsqh.path'>

>>> F = folderName._manipulateList(L, keepAbs=0, makePath=0)
>>> F
['a.ini', 'b.txt']
>>> type(F[0])
<type 'str'>
>>> F = folderName._manipulateList(L, keepAbs=0, makePath=1)
>>> F
['a.ini', 'b.txt']
>>> type(F[0])
<class 'utilsqh.path'>
>>> L = [folderName/'a.ini', 'b.txt']
>>> F = folderName._manipulateList(L, keepAbs=1, makePath=1)
>>> F
['C:/qhtemp/a.ini', 'b.txt']
>>> F = folderName._manipulateList(L, keepAbs=0, makePath=1)
Traceback (most recent call last):
PathError: path._manipulateList with keepAbs: 0, 1 items of the list do not have C:/qhtemp as start


        """
        if not List:
            return List
        L = List[:]
        if not keepAbs:
            # make relative:
            length = len(self)
            strPath = str(self)
            if not self.endswith("/"):
                length += 1
            L = [k[length:] for k in L if k.find(strPath) == 0]
            if len(L) !=len(List):
                raise PathError("path._manipulateList with keepAbs: %s, %s items of the list do not have %s as start"%
                                (keepAbs, len(List)-len(L), self))

        if makePath:
            return map(path, L)
        else:
            return map(str, map(path, L))

    def internetformat(self):
        """convert to file:/// and fill with %20 etc
>>> path(testdrive + "/a/b.html").internetformat()
'file:///C:/a/b.html'
>>> path(testdrive + "/a/a b.html").internetformat()
'file:///C:/a/a%20b.html'
>>> path("a/b c.html").internetformat()
'a/b%20c.html'
>>> path(testdrive + "\").internetformat()
'file:///C:/'

seems to happen too:

>>> path('file:/C:/a/b.html').internetformat()
'file:///C:/a/b.html'

        see testing in testPath

        """
        if self.startswith("file:///"):
            return str(self)
        elif len(self) > 2 and self[1:3] == ":/":
            start, rest = self[0], self[3:]
            return 'file:///'+start.upper() + ":/" + self._quote_rest(rest)
        elif self.startswith("file:/") and len(self) > 9:
            start, letter, colonslash, rest = self[:5], self[6], self[7:9], self[9:]
            if letter in string.letters and colonslash == ':/':
                return 'file:///' + letter.upper() + colonslash + self._quote_rest(rest)
            else:
                return str(self)
        else:
            return self._quote_rest(str(self))
        
    def _quote_rest(self, restofurl):
        """for internetformat above"""
        
        restList = restofurl.split("/")
        quotedList = map(urllib.quote, restList)
        return "/".join(quotedList)

    def unix(self, glueChar="", lowercase=1, canHaveExtension=1, canHaveFolders=1):
        """convert to unixlike name

        no leading - or 0-9, put a _ in front
        no other characters than [a-zA-Z0-9_] allowed

        with lowercase = 0 uppercase is preserved. (Default = 1,
                           convert all to lowercase

        if there are folders (and canHaveFolders=1), the folder parts are always
        converted with canHaveExtension=0

        the extension is always converted to lowercase.
        also see toUnixName above.

>>> path('aap').unix()
'aap'
>>> path('aap.jpg').unix()
'aap.jpg'
>>> path('AAP.jpg').unix()
'aap.jpg'
>>> path('AAP.JPG').unix(lowercase=0)      # extension is always converted
'AAP.jpg'
>>> path('A 800-34.jpg').unix()
'a800-34.jpg'
>>> path(testdrive + "/A?Bc/C- - +    98/A .txt").unix()
'C:/abc/c--98/a.txt'

# with e acute and Y acute
>>> path(testdrive + "/d\xe9\xddf").unix()
'C:/deyf'

# path starting with a digit:
>>> path(testdrive + "/3d/4a.txt").unix()
'C:/_3d/_4a.txt'

# path starting with "-":
>>> path(testdrive + "/-3d/-4a.txt").unix()
'C:/_-3d/_-4a.txt'

        """
        return path(toUnixName(str(self), glueChar=glueChar,
                               lowercase=lowercase,
                               canHaveExtension=canHaveExtension,
                               canHaveFolders=canHaveFolders))


    def replaceExt(self, ext):
        """replace extension, sometimes because of uppercase

        """
        return path(replaceExt(self, ext))

    def getExt(self):
        """return the extension (including the .) or empty string if no extension
        """
        return getExt(self)

    def hasExt(self):
        """return true if name has an extension
        """
        return getExt(self) != ""

    def encodePath(self):
        """encode to file (dir)

        used in gui inputoutput and kontrol (minimal)

>>> path(testdrive + "/a/b.txt").encodePath()
'b.txt (C:/a)'
>>> path("b.txt").encodePath()
'b.txt ()'
>>> path(testdrive + "/").encodePath()
' (C:/)'


        return a string
        """
        Folder, File = self.split()
        return '%s (%s)'% (File, Folder)

def decodePath(text):
    """decode to path (file or dir)

>>> decodePath('b.txt (C:/a)')
'C:/a/b.txt'
>>> decodePath('b.txt ()')
'b.txt'
>>> decodePath(' (C:/)')
'C:/'


        Return a path instance
    """
    if '(' not in text:
        return str(text)

    t = str(text)
    File, Folder = t.split('(', 1)
    Folder = Folder.rstrip(')')
    Folder = Folder.strip()
    File = File.strip()
    return path(Folder)/File

def decodePathTuple(text):
    """decode to path (file or dir) Total, Folder, File

>>> decodePathTuple('b.txt (C:/a)')
('C:/a/b.txt', 'C:/a', 'b.txt')
>>> decodePathTuple('b.txt ()')
('b.txt', '', 'b.txt')
>>> decodePathTuple(' (C:/)')
('C:/', 'C:/', '')


        Return a path instance
    """
    if '(' not in text:
        return str(text)

    t = str(text)
    File, Folder = t.split('(', 1)
    Folder = Folder.rstrip(')')
    Folder = Folder.strip()
    File = File.strip()
    return path(Folder)/File, path(Folder), path(File)




class intarray(dict):
    """array of something, for counting totals

    entries can be  spurious.  Check can be with isentry function.

    note introw instances are made automatically, only double entries
    are made!

>>> a = intarray()
>>> str(a)
'{}'
>>> print(a.strarray())
   -
>>> print(a.strarray(a.totalsarray()))
       0total
  0:   -   0
     ---   0
       0   0

>>> a[3][2] = 1
>>> str(a)
'{0: {}, 3: {2: 1}}'
>>> str(a[3])
'{2: 1}'
>>> str(a[0])
'{}'
>>> str(a[2][1])
'None'

valid entry checking:
>>> a.hasvalue(5,0)
False
>>> a.hasvalue(3,2)
True
>>> a.hasvalue(3,10)
False


>>> print(a.strarray())
   -   -   -
   -   -   -
   -   -   -
   -   -   1
>>> a[2][0] = 5
>>> a[3][1] = "20%"
>>> print(a.strarray(a.totalsarray()))
       0   1   2total
  0:   -   -   -   0
  1:   -   -   -   0
  2:   5   -   -   5
  3:   - 20%   1   1
     --- --- ---   6
       5   0   1   6
>>> print(a.strarray(a.totalsarray(rowsum=0)))
       0   1   2
  0:   -   -   -
  1:   -   -   -
  2:   5   -   -
  3:   - 20%   1
     --- --- ---
       5   0   1

>>> print(a.strarray(a.totalsarray(colsum=0)))
       0   1   2total
  0:   -   -   -   0
  1:   -   -   -   0
  2:   5   -   -   5
  3:   - 20%   1   1
>>> print(a.strarray(a.totalsarray(colsum=0, rowsum=0)))
       0   1   2
  0:   -   -   -
  1:   -   -   -
  2:   5   -   -
  3:   - 20%   1


    """
    def __init__(self):
        """define maxRow"""
        self.maxRow = 0
        dict.__init__(self)

    def __getitem__(self, i):
        """get from array, take 0 if non-existent"""
        self.maxRow = max(self.maxRow, i)
        return self.setdefault(i, introw())

    def hasvalue(self, i, j):
        if i in self:
            return self[i].hasvalue(j)
        else:
            return False

    def strarray(self, doublelist=None):
        """give str format of whole array"""
        if doublelist == None:
            doublelist = self.doublelistarray()
        if type(doublelist) == types.ListType:
            return '\n'.join([justify(r) for r in doublelist])
        else:
            return str(doublelist)

    def doublelistarray(self):
        """give array in double list, for inclusion in TABLE call"""
        maxCol = 0
        for r in range(self.maxRow+1):
            if r in self:
                maxCol = max(maxCol, self[r].maxCol)
        ALL = []
        for r in range(self.maxRow+1):
            R = []
            for c in range (maxCol +1):
                v = self[r][c]
                if v == None:
                    R.append('-')
                else:
                    R.append(v)
            ALL.append(R)
        return ALL

    def totalsarray(self, rowsum=1, colsum=1):
        """give array in double list, for inclusion in TABLE call"""
        maxCol = 0
        for r in range(self.maxRow+1):
            if r in self:
                maxCol = max(maxCol, self[r].maxCol)
        ALL = []
        TOP = ['']
        for c in range(maxCol +1):
            TOP.append(c)
        if rowsum:
            TOP.append('total')
        ALL = [TOP]
        totalSum = 0
        colSums = [0]*(maxCol+1)
        for r in range(self.maxRow+1):
            R = ['%s:'%r]
            rowSum = 0
            for c in range(maxCol +1):
                v = self[r][c]
                try:
                    vnum = int(v)
                except:
                    vnum = 0
                if v == None:
                    R.append('-')
                else:
                    rowSum += vnum
                    colSums[c] += vnum
                    R.append(v)
            if rowsum:
                R.append(rowSum)
            totalSum += rowSum
            ALL.append(R)
        if colsum:
            R = ['']
            R+= ['---']*(maxCol+1)
            if rowsum:
                R.append(totalSum)
            ALL.append(R)
            R = ['']
            R += colSums
            totalSum = 0
            if rowsum:
                for c in colSums:
                    totalSum += c
                R.append(totalSum)
            ALL.append(R)
        return ALL

class introw(dict):
    """row with something, preferably integers for counting totals"""
    def __init__(self):
        """define maxCol"""
        self.maxCol = 0
        dict.__init__(self)

    def hasvalue(self, i):
        return i in self

    def __getitem__(self, i):
        """get from array, take 0 if non-existent"""
        return self.get(i, None)

    def __setitem__(self, i, v):
        """keep maxCol"""
        if type(i) == types.IntType:
            self.maxCol = max(self.maxCol, i)
        dict.__setitem__(self, i, v)

def justify(s):
    S = ''
    for r in s:
        S += '%4s'%r
    return S

def emptyFolders(arg, dirname, filenames):
    """return a list of empty folders through path.walk()

    ignore .svn folders...

>>> makeEmptyFolder(testdrive + r"\\empty")
>>> makeEmptyFolder(testdrive + r"\\empty\\empty2")
>>> makeEmptyFolder(testdrive + r"\\empty\\empty2\\empty3")
>>> makeEmptyFolder(testdrive + r"\\empty\\notempty")
>>> touch(testdrive + r"\\empty\\notempty\\a.txt")
>>> print path(testdrive + r"\\empty").walk(emptyFolders)
['C:/empty/empty2', 'C:/empty/empty2/empty3']
    """
    if not filenames:
        if dirname.find("\\.svn") > 0 or dirname.find("/.svn") > 0:
            return
        arg.append(dirname)
    else:
        for f in filenames:
            f2 = path(dirname)/f
            if f2.isdir():
                if not f2.walk(emptyFolders):
                    break
            else:
                break
        else:
            arg.append(dirname)

def testWalk(arg, dir, files):
    """only for testing path.walk function
    append all names that walk receives

    """
    arg.append(dir)
    arg.extend(files)

def testWalk2(arg, dir, files):
    """only for testing path.walk function
    append all path names that walk receives
    """
    arg.extend([os.path.join(dir, f) for f in files])

def walkOnlyFiles(arg, dir, files):
    """only for testing path.walk function

    do not append folders

    """
    for f in files:
        dirplusf = path(dir)/f
        if dirplusf.isdir():
            continue
        arg.append(dirplusf)
def collectPsdFiles(arg, dir, files):
    """collect only .psd files"""
    ext = '.psd'
    for f in files:
        dirplusf = path(dir)/f
        if dirplusf.isdir():
            continue

        if dirplusf.lower().endswith(ext):
            # in case .PSD instead of .psd:
            dirplusf.replaceExt(ext)
            arg.append(dirplusf)

def touchAllFiles(arg, dir, files):
    """touch all files in folder"""
    dir = path(dir)
    touch(dir, files)
    for f in files:
        arg.append(dir/f)

def collectTifFiles(arg, dir, files):
    """collect only .tif files"""
    ext = '.tif'
    for f in files:
        dirplusf = path(dir)/f
        if dirplusf.isdir():
            continue

        if dirplusf.lower().endswith(ext):
            # in case .PSD instead of .psd:
            dirplusf.replaceExt(ext)
            arg.append(dirplusf)

def getRoot(*rootList):
    """returns the first valid directory in list

    Gives a path instance!!

    note: the double \\ is here needed for doctest only!

    >>> getRoot(testdrive + r'\\program files', r'd:\\sites', '/usr/lib')
    'C:/program files'
    >>> getRoot(testdrive + r'\\temp', testdrive + r'\\windows\\temp', r'c:\\winnt\\temp', testdrive + '/projects')
    'C:/temp'

    """
    for d in rootList:
        if type(d) in (types.ListType, types.TupleType):
            for e in d:
                e = e.replace('\\', '/')
                if os.path.isdir(e):
                    return path(e)
        else:
            d = d.replace('\\', '/')
            if os.path.isdir(d):
                return path(d)
    raise IOError('getRoot, no valid folder found in list: %s'% `rootList`)

def openAnything(source):
    """URI, filename, or string --> stream

    This function lets you define parsers that take any input source
    (URL, pathname to local or network file, or actual data as a string)
    and deal with it in a uniform manner.  Returned object is guaranteed
    to have all the basic stdio read methods (read, readline, readlines).
    Just .close() the object when you're done with it.

Taken from Mark Pilgrim, book dive into python!
>>> sock = openAnything('hello world')
>>> print sock.read()
hello world
>>> sock.seek(0)
>>> for l in sock:
...     print l
hello world

Make a short testfile and read it back:

>>> sock = open(testdrive + r'\\temp\\test.txt', 'w')
>>> sock.write('one\\ntwo\\n    three')
>>> sock.close()
>>> sock = openAnything(testdrive + r'\\temp\\test.txt')

Read back:

>>> for l in sock:
...     print l.rstrip()
one
two
    three

Or in a one liner:

>>> for l in openAnything(testdrive + r'\\temp\\test.txt'):
...     print l.rstrip()
one
two
    three

now just a string:

>>> for l in openAnything('just a string'):
...     print l.rstrip()
just a string


    """
    try:
        sourceslash = source.replace('\\', '/')
    except AttributeError:
        sourceslash = source
        
    if hasattr(source, "read"):
        return source

    if source == "-":
        import sys
        return sys.stdin

    # try to open with urllib (if source is http, ftp, or file URL)
    import urllib
    try:
        return urllib.urlopen(sourceslash)
    except (IOError, OSError):
        pass

    # try to open with native open function (if source is pathname)
    try:
        return open(sourceslash)
    except (IOError, OSError):
        pass

    # treat source as string
    import StringIO
    return StringIO.StringIO(str(source))


def checkKnownTest(basis, known="known", test="test", **kw):
    
    """test a test folder against a known folder, interactive decisions

    Give the basis, "test" must exist as sub folder, "known" is created
    as first case, if not yet present.

    "Known" is assumed to be in svn.

    if they are the same, 1 is returned, otherwise, for a response is asked
    and if relevant, windiff is started.

    Note: windiff is assumed to be in testdrive + "\windiff\windiff.exe", and calling
    windiff must have folders without spaces!

    The sub folders must be named exactly "known", "test", unless
    overridden by the variable test.

    If "frame" in kw: take this for the YesNo function

    """
    frame = kw.get("frame")
    basis = path(basis)
    ignore = kw.get("ignore", None)
    hide = kw.get("hide", None)
    if basis.find(' ') >= 0:
        raise Exception('for windiff, no spaces in path allowed: %s'% basis)

    if not basis.isdir():
        raise IOError('not a folder: %s'% basis)
    test = basis/test

    if not test.isdir():
        raise IOError('nothing to test: %s'% test)

    known = basis/known
    if not known.isdir():
        if YesNo('known does not exist yet, assume "%s" is correct?'% test, frame):
            test.rename(known)
            print 'do not forget to add "known" to svn: %s'% known
            return
    d = filecmp.dircmp(str(known), str(test), ignore=ignore, hide=hide)
#    d.doOutput(0)
    res = d.report_full_closure()
    # only checking files now, assume no folders are present:
    if not (d.left_only or d.right_only or d.diff_files):
        return 1

    if d.right_only:
        print 'new files in "test": %s'% d.right_only
        if YesNo('do you want to copy these to "known" (%s)?'% d.right_only, frame):
            for f in d.right_only:
                shutil.copy(str(test/f), str(known/f))
                print 'copied to "known": %s'% known
                print 'do not forget to add to svn: %s'% d.right_only

    if d.left_only:
        print 'possibly obsolete files in "known": %s'% known
        print 'please remove from svn: %s'% d.left_only

    if d.diff_files:
        print 'different files: %s'% d.diff_files
        # now go into windiff:
        c = path('c:/windiff/windiff.exe').normpath()
        os.chdir(basis)
        os.spawnv(os.P_NOWAIT, c,  (c, "known", test))
        if YesNo('do you want to copy these to "known" (%s)?'% d.diff_files, frame):
            for f in d.diff_files:
                shutil.copy(str(test/f), str(known/f))
            print 'copied to "known": %s'% known
    if d.funny_files:
        print 'funny files: %s'% d.diff_files

def checkKnownTestFiles(known, test, **kw):
    """test a kwown file against a test file

    if they are the same, 1 is returned, otherwise, for a response is asked
    and if relevant, windiff is started.

    Note: windiff is assumed to be in testdrive + "\windiff\windiff.exe", and calling
    windiff must have folders without spaces!

    The sub folders must be named exactly "known", "test", unless
    overridden by the variable test.

    If "frame" in kw: take this for the YesNo function

    """
    frame = kw.get("frame")
    basis = path(basis)
    ignore = kw.get("ignore", None)
    hide = kw.get("hide", None)
    if basis.find(' ') >= 0:
        raise Exception('for windiff, no spaces in path allowed: %s'% basis)

    if not basis.isdir():
        raise IOError('not a folder: %s'% basis)
    test = basis/test

    if not test.isdir():
        raise IOError('nothing to test: %s'% test)

    known = basis/known
    if not known.isdir():
        if YesNo('known does not exist yet, assume "%s" is correct?'% test, frame):
            test.rename(known)
            print 'do not forget to add "known" to svn: %s'% known
            return
    d = filecmp.dircmp(str(known), str(test), ignore=ignore, hide=hide)
#    d.doOutput(0)
    res = d.report_full_closure()
    # only checking files now, assume no folders are present:
    if not (d.left_only or d.right_only or d.diff_files):
        return 1

    if d.right_only:
        print 'new files in "test": %s'% d.right_only
        if YesNo('do you want to copy these to "known" (%s)?'% d.right_only, frame):
            for f in d.right_only:
                shutil.copy(str(test/f), str(known/f))
                print 'copied to "known": %s'% known
                print 'do not forget to add to svn: %s'% d.right_only

    if d.left_only:
        print 'possibly obsolete files in "known": %s'% known
        print 'please remove from svn: %s'% d.left_only

    if d.diff_files:
        print 'different files: %s'% d.diff_files
        # now go into windiff:
        c = path('c:/windiff/windiff.exe').normpath()
        os.chdir(basis)
        os.spawnv(os.P_NOWAIT, c,  (c, "known", test))
        if YesNo('do you want to copy these to "known" (%s)?'% d.diff_files, frame):
            for f in d.diff_files:
                shutil.copy(str(test/f), str(known/f))
            print 'copied to "known": %s'% known
    if d.funny_files:
        print 'funny files: %s'% d.diff_files



## keep locale characters intact...
reCharsSpaces = re.compile(r'[^\w -]', re.L)

def normaliseLabel(label):
    """lowercase if input is lowercase or capitalized or all uppercase

    remove double spaces and invalid character is

>>> normaliseLabel(' hello      there  ')
'hello there'
>>> normaliseLabel('Hello there')
'hello there'
>>> normaliseLabel('hello There')
'hello there'
>>> normaliseLabel('15 - 30m')
'15 - 30m'
>>> normaliseLabel('<15m')
'15m'
>>> normaliseLabel('Prijs:')
'prijs'
>>> normaliseLabel('idee�n:')
'idee\\xebn'

    """
    L = ' '.join(label.strip().split())
    L  = L.lower()
    L = reCharsSpaces.sub('', L).strip()
    return L


def YesNo(prompt, frame=None):
    if frame:
        return frame.YesNo(prompt)
    i = 0
    while i < 3:
        a = raw_input(prompt + '(yn)')
        if a in 'yYJj':
            return 1
        elif a in 'nN':
            return
    return




# three tester functions:
def revTrue(t):
    return "y"
def revFalse(t):
    return "n"
def revAbort(t):
    return

def _test():
    import doctest, utilsqh
    reload(utilsqh)

    doctest.master = None
    return  doctest.testmod(utilsqh)

def runPanel(frame, notebook):
    print 'starting cp %s'% __name__
    cp = ControlPanel(notebook, frame, -1, __name__)
    cp.addFunction(checkFolders, type="inputfolder, outputfolder")
    cp.addDefaults()
    print 'started cp %s'% __name__
    return cp

#def runIsValidWindow(h):
#    print 'isValidWindow: %s, %s'% (h, isValidWindow(h))
def runGetProcIdFromWnd(h):
    print 'whndle:%s, processid: %s'% (h, GetProcIdFromWnd(h))

def killProcIdFromWnd(h):
    pHndle = GetProcIdFromWnd(h)
    if pHndle:
        print 'kill process: %s'% pHndle
        killProcess(pHndle)
    else:
        print 'no process found: %s'% pHndle


if __name__ == "__main__":
    # three tester functions:
    def revTrue(t):
        return "y"
    def revFalse(t):
        return "n"
    def revAbort(t):
        return
    _test()
    ### werkt nog niet...
    #runIsValidWindow(1234567)
    #runGetProcIdFromWnd(461648)
    #killProcIdFromWnd(461648)
