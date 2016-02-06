#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# unittestLilypond.py
#   This script performs some basic tests of the LyNote class which handles lilypond input strings
#   This has nothing to do with speech recognition, but here because a Unimacro grammar "frescobaldi.py"
#   is developed in order to do inputs for lilypond in frescobalde.
#
import sys, unittest, types
import os
import os.path
import TestCaseWithHelpers
import lynote

def getBaseFolder(globalsDict=None):
    """get the folder of the calling module.

    either sys.argv[0] (when run direct) or
    __file__, which can be empty. In that case take the working directory
    """
    globalsDictHere = globalsDict or globals()
    baseFolder = ""
    if globalsDictHere['__name__']  == "__main__":
        baseFolder = os.path.split(sys.argv[0])[0]
        print 'baseFolder from argv: %s'% baseFolder
    elif globalsDictHere['__file__']:
        baseFolder = os.path.split(globalsDictHere['__file__'])[0]
        print 'baseFolder from __file__: %s'% baseFolder
    if not baseFolder:
        baseFolder = os.getcwd()
        print 'baseFolder was empty, take wd: %s'% baseFolder
    return baseFolder

thisDir = getBaseFolder(globals())
logFileName = os.path.join(thisDir, "testresult.txt")

#---------------------------------------------------------------------------
# These tests should be run after we call natConnect
# no reopen user at each test anymore..
# no default open window (open window will be the calling program)
# default .ini files pop up when you first run this test. just ignore them.
class UnittestLyNote(TestCaseWithHelpers.TestCaseWithHelpers):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def checkLyResult(self, expNote, lyn):
        """check the parts of the note (lyn) against the expected values
        """
        note, elevation, duration, additions, backslashed = expNote
        self.assertEqual(note, lyn.note, 'note not equal "%s", expected: "%s", got: "%s"'% (lyn.originalInput, note, lyn.note))
        self.assertEqual(elevation, lyn.elevation, 'elevation not equal "%s", expected: "%s", got: "%s"'% (lyn.originalInput, elevation, lyn.elevation))
        self.assertEqual(duration, lyn.duration, 'duration not equal "%s", expected: "%s", got: "%s"'% (lyn.originalInput, duration, lyn.duration))
        self.assertEqual(additions, lyn.additions, 'additions not equal "%s", expected: "%s", got: "%s"'% (lyn.originalInput, additions, lyn.additions))
        self.assertEqual(backslashed, lyn.backslashed, 'backslashed not equal "%s", expected: "%s", got: "%s"'% (lyn.originalInput, backslashed, lyn.backslashed))
    
    def tttestSimpleNote(self):
        """test a few basic examples of a lilypond note
        """
        for s, expNote in [("g,8.", ("g", ",", "8.", "", None)),
                        ("a,,8", ("a", ",,", "8", "", None)),
                        ("cis", ("cis", "", "", "", None)),
                        ("aes'(", ("aes", "'", "", "(", None)),
                        (r"d4([\melisma", ("d", "", "4", "([", ['\\melisma'])),
                        (r"ais,,32..\melismaEnd]\break\)", ("ais", ",,", "32..", r"]\)", [r'\melismaEnd', r'\break']))]:
                        
            lyn = lynote.LyNote(s)
            self.checkLyResult( expNote, lyn )
            self.assert_(lyn.isNote(), '"%s" should be a note (isNote function), not: %s'% (s, lyn.isNote()))
            print 'testSimpleNote OK: "%s", result: "%s"'% (s, lyn)

    def testIncompleteNoteAndUpdate(self):
        """test a few basic examples of a lilypond note
        """
        for s, expNote in [(",8.", ("", ",", "8.", "", None)),
                        ("8", ("", "", "8", "", None)),
                        ("\melismaEnd", ("", "", "", "", [r"\melismaEnd"])),
                        (r",,1\melismaEnd]\break\)", ("", ",,", "1", r"]\)", [r'\melismaEnd', r'\break']))]:
                        
            lyn = lynote.LyNote(s)
            self.checkLyResult( expNote, lyn )
            print 'testIncompleteNote OK: "%s", result: "%s"'% (s, lyn)

        updateNote = ","            
        orgNote = "g'4("
        lyorg = lynote.LyNote(orgNote)
        lyorg.updateNote(updateNote)
        expUpdated = ("g", "", "4", "(", None)
        self.checkLyResult( expUpdated, lyorg )
        print 'testIncompleteNote "%s" updated with "%s" OK, result: "%s"'% (orgNote, updateNote, lyorg)

        updateNote = "8"            
        orgNote = "a'4("
        lyorg = lynote.LyNote(orgNote)
        lyorg.updateNote(updateNote)
        expUpdated = ("a", "'", "8", "(", None)
        self.checkLyResult( expUpdated, lyorg )
        print 'testIncompleteNote "%s" updated with string "%s" OK, result: "%s"'% (orgNote, updateNote, lyorg)

        lyorg = lynote.LyNote(orgNote)
        lyupdate = lynote.LyNote(updateNote)
        lyorg.updateNote(lyupdate)
        self.checkLyResult( expUpdated, lyorg )
        print 'testIncompleteNote "%s" updated with instance "%s" OK, result: "%s"'% (orgNote, lyupdate, lyorg)






        updateNote = "c'8..\melisma"            
        orgNote = "b'4("
        lyorg = lynote.LyNote(orgNote)
        lyorg.updateNote(updateNote)
        expUpdated = ("c", "''", "8..", "(", [r"\melisma"])
        self.checkLyResult( expUpdated, lyorg )
        print 'testIncompleteNote "%s" updated with "%s" OK, result: "%s"'% (orgNote, updateNote, lyorg)

        lyorg = lynote.LyNote(orgNote)
        lyupdate = lynote.LyNote(updateNote)
        lyorg.updateNote(lyupdate)
        self.checkLyResult( expUpdated, lyorg )
        print 'testIncompleteNote "%s" updated with instance "%s" OK, result: "%s"'% (orgNote, lyupdate, lyorg)

    def tttestReBackslashedWord(self):
        r"""test \break, \melisma etc, but refuse \( and \)"""
        for s in ['', r'\)']:
            m = lynote.reBackslashedWord.match(s)
            self.assertEqual(None, m, 'string "%s" should not match reBackslashWord'% s)
            print 'testReBackslashedWord: correct fail to match "%s"'% s
        for s in [r'\break', r'\melismaEnd']:
            m = lynote.reBackslashedWord.match(s)
            if m is None:
                self.fail('string r"%s" should match reBackslashWord'% s)
            print 'testReBackslashedWord: correct match of "%s"'% s
            
    def tttestStrAndRepr(self):
        """check the correct str and repr result"""        
        for s in ["g,8.", "a,,8"]:
            expStr = s
            lyn = lynote.LyNote(s)
            self.assertEqual(expStr, str(lyn), 'str of "%s" fails ("%s")'% (s, str(lyn)))
            print 'testStrAndRepr: correct str "%s" (being the same)'% s
            expRepr = "lynote: " + s
            self.assertEqual(expRepr, repr(lyn), 'repr of "%s" fails ("%s")'% (s, repr(lyn)))
            print 'testStrAndRepr: correct repr "%s" (of "%s")'% (s, repr(s))
            
            
        
            
def log(t):
    print t

def run():
    log('starting unittestLyNote')
    # trick: if you only want one or two tests to perform, change
    # the test names to her example def test....
    # and change the word 'test' into 'tttest'...
    # do not forget to change back and do all the tests when you are done.
    suite = unittest.makeSuite(UnittestLyNote, 'test')
##    natconnectOption = 0 # no threading has most chances to pass...
    result = unittest.TextTestRunner().run(suite)
    print result
if __name__ == "__main__":
    run()
