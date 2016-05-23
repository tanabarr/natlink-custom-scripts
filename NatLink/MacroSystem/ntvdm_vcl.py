# NatLink macro definitions for NaturallySpeaking
# coding: latin-1
# Generated by vcl2py 2.8.5, Mon May 23 13:19:05 2016

import natlink
from natlinkutils import *
from VocolaUtils import *


class ThisGrammar(GrammarBase):

    gramSpec = """
        <1> = 'Copy That' ;
        <2> = 'Paste That' ;
        <3> = 'Go Up' ;
        <4> = 'Go Up' ('one' | 'two' | 'three' | 'four' | 'five' | 'six' | 'seven' | 'eight' | 'nine' | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20) ;
        <any> = <1>|<2>|<3>|<4>;
        <sequence> exported = <any>;
    """
    
    def initialize(self):
        self.load(self.gramSpec)
        self.currentModule = ("","",0)
        self.ruleSet1 = ['sequence']

    def gotBegin(self,moduleInfo):
        # Return if wrong application
        window = matchWindow(moduleInfo,'ntvdm','')
        if not window: return None
        self.firstWord = 0
        # Return if same window and title as before
        if moduleInfo == self.currentModule: return None
        self.currentModule = moduleInfo

        self.deactivateAll()
        title = string.lower(moduleInfo[1])
        if string.find(title,'') >= 0:
            for rule in self.ruleSet1:
                try:
                    self.activate(rule,window)
                except natlink.BadWindow:
                    pass

    def convert_number_word(self, word):
        if   word == 'zero':
            return '0'
        elif word == 'one':
            return '1'
        elif word == 'two':
            return '2'
        elif word == 'three':
            return '3'
        elif word == 'four':
            return '4'
        elif word == 'five':
            return '5'
        elif word == 'six':
            return '6'
        elif word == 'seven':
            return '7'
        elif word == 'eight':
            return '8'
        elif word == 'nine':
            return '9'
        else:
            return word

    # 'Copy That'
    def gotResults_1(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_1(words[1:], fullResults)
        except Exception, e:
            handle_error('ntvdm.vcl', 6, '\'Copy That\'', e)
            self.firstWord = -1

    # 'Paste That'
    def gotResults_2(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+Space}ep'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_2(words[1:], fullResults)
        except Exception, e:
            handle_error('ntvdm.vcl', 7, '\'Paste That\'', e)
            self.firstWord = -1

    # 'Go Up'
    def gotResults_3(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += 'cd ..{Enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_3(words[1:], fullResults)
        except Exception, e:
            handle_error('ntvdm.vcl', 9, '\'Go Up\'', e)
            self.firstWord = -1

    # 'Go Up' 1..20
    def gotResults_4(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += 'cd '
            limit = ''
            word = fullResults[1 + self.firstWord][0]
            limit += self.convert_number_word(word)
            for i in range(to_long(limit)):
                top_buffer += '..\\'
            top_buffer += '{Enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
            if len(words) > 2: self.gotResults_4(words[2:], fullResults)
        except Exception, e:
            handle_error('ntvdm.vcl', 10, '\'Go Up\' 1..20', e)
            self.firstWord = -1

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
