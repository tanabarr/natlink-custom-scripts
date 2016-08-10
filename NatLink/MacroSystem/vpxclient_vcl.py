# NatLink macro definitions for NaturallySpeaking
# coding: latin-1
# Generated by vcl2py 2.8.5, Wed Aug 10 09:26:46 2016

import natlink
from natlinkutils import *
from VocolaUtils import *


class ThisGrammar(GrammarBase):

    gramSpec = """
        <1> = ('start' | 'stop' | 'suspend' | 'reset' | 'shutdown guest' | 'reset guest' | 'focus' | 'close' | 'new' ) 'VM' ;
        <2> = 'search the sphere' ;
        <3> = 'open VM settings' ;
        <4> = 'open VM consul' ;
        <5> = 'escape from consul' ;
        <any> = <1>|<2>|<3>|<4>|<5>;
        <sequence> exported = <any>;
    """
    
    def initialize(self):
        self.load(self.gramSpec)
        self.currentModule = ("","",0)
        self.ruleSet1 = ['sequence']

    def gotBegin(self,moduleInfo):
        # Return if wrong application
        window = matchWindow(moduleInfo,'vpxclient','')
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

    # ('start' | 'stop' | 'suspend' | 'reset' | 'shutdown guest' | 'reset guest' | 'focus' | 'close' | 'new') 'VM'
    def gotResults_1(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{ctrl+'
            word = fullResults[0 + self.firstWord][0]
            if word == 'start':
                top_buffer += 'b'
            elif word == 'stop':
                top_buffer += 'e'
            elif word == 'suspend':
                top_buffer += 'z'
            elif word == 'reset':
                top_buffer += 't'
            elif word == 'shutdown guest':
                top_buffer += 'd'
            elif word == 'reset guest':
                top_buffer += 'r'
            elif word == 'focus':
                top_buffer += 'g'
            elif word == 'close':
                top_buffer += 'X'
            elif word == 'new':
                top_buffer += 'n'
            top_buffer += '}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
            if len(words) > 2: self.gotResults_1(words[2:], fullResults)
        except Exception, e:
            handle_error('vpxclient.vcl', 3, '(\'start\' | \'stop\' | \'suspend\' | \'reset\' | \'shutdown guest\' | \'reset guest\' | \'focus\' | \'close\' | \'new\') \'VM\'', e)
            self.firstWord = -1

    # 'search the sphere'
    def gotResults_2(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{ctrl+F}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_2(words[1:], fullResults)
        except Exception, e:
            handle_error('vpxclient.vcl', 4, '\'search the sphere\'', e)
            self.firstWord = -1

    # 'open VM settings'
    def gotResults_3(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{alt+n}v{down_4}{enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_3(words[1:], fullResults)
        except Exception, e:
            handle_error('vpxclient.vcl', 5, '\'open VM settings\'', e)
            self.firstWord = -1

    # 'open VM consul'
    def gotResults_4(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{alt+n}v{down_3}{enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_4(words[1:], fullResults)
        except Exception, e:
            handle_error('vpxclient.vcl', 6, '\'open VM consul\'', e)
            self.firstWord = -1

    # 'escape from consul'
    def gotResults_5(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer = do_flush(False, top_buffer);
            extension_arg1 = ''
            extension_arg1 += '{ctrl+alt}'
            import vocola_ext_keys
            vocola_ext_keys.send_input(extension_arg1)
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_5(words[1:], fullResults)
        except Exception, e:
            handle_error('vpxclient.vcl', 7, '\'escape from consul\'', e)
            self.firstWord = -1

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
