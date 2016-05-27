# NatLink macro definitions for NaturallySpeaking
# coding: latin-1
# Generated by vcl2py 2.8.5, Fri May 27 08:53:10 2016

import natlink
from natlinkutils import *
from VocolaUtils import *


class ThisGrammar(GrammarBase):

    gramSpec = """
        <n> = ('zero' | 'one' | 'two' | 'three' | 'four' | 'five' | 'six' | 'seven' | 'eight' | 'nine') ;
        <1> = 'recent files' ;
        <2> = 'zoom in' <n> ;
        <13> = 'zoom in' ;
        <3> = 'zoom out' <n> ;
        <14> = 'zoom out' ;
        <4> = 'go to page' <n> <n> <n> ;
        <17> = 'go to page' <n> <n> ;
        <16> = 'go to page' <n> ;
        <15> = 'go to page' ;
        <5> = ('two page' | 'reading' ) 'mode' ;
        <6> = 'previous page' ;
        <7> = 'navigation window' ;
        <8> = 'reading window' ;
        <9> = 'close navigation window' ;
        <10> = 'next' ;
        <11> = 'previous' ;
        <12> = 'close' ;
        <any> = <1>|<2>|<13>|<3>|<14>|<4>|<17>|<16>|<15>|<5>|<6>|<7>|<8>|<9>|<10>|<11>|<12>;
        <sequence> exported = <any>;
    """
    
    def initialize(self):
        self.load(self.gramSpec)
        self.currentModule = ("","",0)
        self.ruleSet1 = ['sequence']

    def gotBegin(self,moduleInfo):
        # Return if wrong application
        window = matchWindow(moduleInfo,'foxitreader','')
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

    def get_n(self, list_buffer, functional, word):
        list_buffer += self.convert_number_word(word)
        return list_buffer

    # 'recent files'
    def gotResults_1(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+f}r'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_1(words[1:], fullResults)
        except Exception, e:
            handle_error('foxitreader.vcl', 5, '\'recent files\'', e)
            self.firstWord = -1

    # 'zoom in' <n>
    def gotResults_2(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            when_value = ''
            word = fullResults[1 + self.firstWord][0]
            when_value = self.get_n(when_value, True, word)
            if when_value != "":
                limit2 = ''
                word = fullResults[1 + self.firstWord][0]
                limit2 = self.get_n(limit2, True, word)
                for i in range(to_long(limit2)):
                    top_buffer += '{Ctrl+'
                    top_buffer += '='
                    top_buffer += '}'
            else:
                limit2 = ''
                limit2 += '1'
                for i in range(to_long(limit2)):
                    top_buffer += '{Ctrl+'
                    top_buffer += '='
                    top_buffer += '}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
        except Exception, e:
            handle_error('foxitreader.vcl', 6, '\'zoom in\' <n>', e)
            self.firstWord = -1

    # 'zoom in'
    def gotResults_13(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            when_value = ''
            when_value += ''
            if when_value != "":
                limit2 = ''
                limit2 += ''
                for i in range(to_long(limit2)):
                    top_buffer += '{Ctrl+'
                    top_buffer += '='
                    top_buffer += '}'
            else:
                limit2 = ''
                limit2 += '1'
                for i in range(to_long(limit2)):
                    top_buffer += '{Ctrl+'
                    top_buffer += '='
                    top_buffer += '}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_13(words[1:], fullResults)
        except Exception, e:
            handle_error('foxitreader.vcl', 6, '\'zoom in\'', e)
            self.firstWord = -1

    # 'zoom out' <n>
    def gotResults_3(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            when_value = ''
            word = fullResults[1 + self.firstWord][0]
            when_value = self.get_n(when_value, True, word)
            if when_value != "":
                limit2 = ''
                word = fullResults[1 + self.firstWord][0]
                limit2 = self.get_n(limit2, True, word)
                for i in range(to_long(limit2)):
                    top_buffer += '{Ctrl+minus}'
            else:
                limit2 = ''
                limit2 += '1'
                for i in range(to_long(limit2)):
                    top_buffer += '{Ctrl+minus}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
        except Exception, e:
            handle_error('foxitreader.vcl', 7, '\'zoom out\' <n>', e)
            self.firstWord = -1

    # 'zoom out'
    def gotResults_14(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            when_value = ''
            when_value += ''
            if when_value != "":
                limit2 = ''
                limit2 += ''
                for i in range(to_long(limit2)):
                    top_buffer += '{Ctrl+minus}'
            else:
                limit2 = ''
                limit2 += '1'
                for i in range(to_long(limit2)):
                    top_buffer += '{Ctrl+minus}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_14(words[1:], fullResults)
        except Exception, e:
            handle_error('foxitreader.vcl', 7, '\'zoom out\'', e)
            self.firstWord = -1

    # 'go to page' <n> <n> <n>
    def gotResults_4(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+g}'
            top_buffer = do_flush(False, top_buffer);
            dragon_arg1 = ''
            dragon_arg1 += '100'
            saved_firstWord = self.firstWord
            call_Dragon('Wait', 'i', [dragon_arg1])
            self.firstWord = saved_firstWord
            when_value = ''
            word = fullResults[1 + self.firstWord][0]
            when_value = self.get_n(when_value, True, word)
            if when_value != "":
                word = fullResults[1 + self.firstWord][0]
                top_buffer = self.get_n(top_buffer, False, word)
                word = fullResults[2 + self.firstWord][0]
                top_buffer = self.get_n(top_buffer, False, word)
                word = fullResults[3 + self.firstWord][0]
                top_buffer = self.get_n(top_buffer, False, word)
                top_buffer += '{enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 4
        except Exception, e:
            handle_error('foxitreader.vcl', 16, '\'go to page\' <n> <n> <n>', e)
            self.firstWord = -1

    # 'go to page' <n> <n>
    def gotResults_17(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+g}'
            top_buffer = do_flush(False, top_buffer);
            dragon_arg1 = ''
            dragon_arg1 += '100'
            saved_firstWord = self.firstWord
            call_Dragon('Wait', 'i', [dragon_arg1])
            self.firstWord = saved_firstWord
            when_value = ''
            word = fullResults[1 + self.firstWord][0]
            when_value = self.get_n(when_value, True, word)
            if when_value != "":
                word = fullResults[1 + self.firstWord][0]
                top_buffer = self.get_n(top_buffer, False, word)
                word = fullResults[2 + self.firstWord][0]
                top_buffer = self.get_n(top_buffer, False, word)
                top_buffer += ''
                top_buffer += '{enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 3
        except Exception, e:
            handle_error('foxitreader.vcl', 16, '\'go to page\' <n> <n>', e)
            self.firstWord = -1

    # 'go to page' <n>
    def gotResults_16(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+g}'
            top_buffer = do_flush(False, top_buffer);
            dragon_arg1 = ''
            dragon_arg1 += '100'
            saved_firstWord = self.firstWord
            call_Dragon('Wait', 'i', [dragon_arg1])
            self.firstWord = saved_firstWord
            when_value = ''
            word = fullResults[1 + self.firstWord][0]
            when_value = self.get_n(when_value, True, word)
            if when_value != "":
                word = fullResults[1 + self.firstWord][0]
                top_buffer = self.get_n(top_buffer, False, word)
                top_buffer += ''
                top_buffer += ''
                top_buffer += '{enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
        except Exception, e:
            handle_error('foxitreader.vcl', 16, '\'go to page\' <n>', e)
            self.firstWord = -1

    # 'go to page'
    def gotResults_15(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+g}'
            top_buffer = do_flush(False, top_buffer);
            dragon_arg1 = ''
            dragon_arg1 += '100'
            saved_firstWord = self.firstWord
            call_Dragon('Wait', 'i', [dragon_arg1])
            self.firstWord = saved_firstWord
            when_value = ''
            when_value += ''
            if when_value != "":
                top_buffer += ''
                top_buffer += ''
                top_buffer += ''
                top_buffer += '{enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_15(words[1:], fullResults)
        except Exception, e:
            handle_error('foxitreader.vcl', 16, '\'go to page\'', e)
            self.firstWord = -1

    # ('two page' | 'reading') 'mode'
    def gotResults_5(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{esc}{esc}{alt}{v}{'
            word = fullResults[0 + self.firstWord][0]
            if word == 'two page':
                top_buffer += '4'
            elif word == 'reading':
                top_buffer += 'o'
            top_buffer += '}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
            if len(words) > 2: self.gotResults_5(words[2:], fullResults)
        except Exception, e:
            handle_error('foxitreader.vcl', 20, '(\'two page\' | \'reading\') \'mode\'', e)
            self.firstWord = -1

    # 'previous page'
    def gotResults_6(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+pgup}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_6(words[1:], fullResults)
        except Exception, e:
            handle_error('foxitreader.vcl', 24, '\'previous page\'', e)
            self.firstWord = -1

    # 'navigation window'
    def gotResults_7(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+b}{enter}{del}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_7(words[1:], fullResults)
        except Exception, e:
            handle_error('foxitreader.vcl', 29, '\'navigation window\'', e)
            self.firstWord = -1

    # 'reading window'
    def gotResults_8(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            limit = ''
            limit += '2'
            for i in range(to_long(limit)):
                top_buffer += '{Ctrl+Alt+s}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_8(words[1:], fullResults)
        except Exception, e:
            handle_error('foxitreader.vcl', 30, '\'reading window\'', e)
            self.firstWord = -1

    # 'close navigation window'
    def gotResults_9(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{f4}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_9(words[1:], fullResults)
        except Exception, e:
            handle_error('foxitreader.vcl', 31, '\'close navigation window\'', e)
            self.firstWord = -1

    # 'next'
    def gotResults_10(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+tab}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_10(words[1:], fullResults)
        except Exception, e:
            handle_error('foxitreader.vcl', 32, '\'next\'', e)
            self.firstWord = -1

    # 'previous'
    def gotResults_11(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{ctrl+shift+tab}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_11(words[1:], fullResults)
        except Exception, e:
            handle_error('foxitreader.vcl', 33, '\'previous\'', e)
            self.firstWord = -1

    # 'close'
    def gotResults_12(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+w}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_12(words[1:], fullResults)
        except Exception, e:
            handle_error('foxitreader.vcl', 34, '\'close\'', e)
            self.firstWord = -1

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
