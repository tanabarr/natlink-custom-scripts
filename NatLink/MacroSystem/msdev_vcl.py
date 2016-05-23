# NatLink macro definitions for NaturallySpeaking
# coding: latin-1
# Generated by vcl2py 2.8.5, Mon May 23 13:19:05 2016

import natlink
from natlinkutils import *
from VocolaUtils import *


class ThisGrammar(GrammarBase):

    gramSpec = """
        <folder> = ('Temp' | 'Downloads' | 'Vocola' | 'NatLink' ) ;
        <file> = ('Temp' ) ;
        <1> = ('Open' | 'Close' | 'Recent' | 'Save' ) 'Workspace' ;
        <2> = 'Workspace' ('one' | 'two' | 'three' | 'four' | 'five' | 'six' | 'seven' | 'eight' | 'nine' | 10) ;
        <3> = 'Open File' ;
        <4> = 'Open File' <folder> ;
        <5> = 'Close' ('File' | 'That' ) ;
        <6> = 'Save File' ;
        <7> = 'Buffer' <file> ;
        <8> = 'Find in Files' ;
        <9> = 'Find in Files' <folder> ;
        <38> = 'Find in' <folder> ;
        <10> = 'Toggle Read Only' ;
        <39> = 'Read Only' ;
        <11> = 'Full Screen' ;
        <12> = 'New' ('Search' | 'Find' ) ;
        <13> = 'Find New' ;
        <14> = 'Find That' ;
        <15> = 'Find' ('Down' | 'Up' ) ;
        <16> = 'Next Bookmark' ;
        <digit> = ('zero' | 'one' | 'two' | 'three' | 'four' | 'five' | 'six' | 'seven' | 'eight' | 'nine') ;
        <17> = 'Line Number' ;
        <18> = 'Line Number' <digit> ;
        <40> = 'Line' <digit> ;
        <19> = 'Line Number' <digit> <digit> ;
        <41> = 'Line' <digit> <digit> ;
        <20> = 'Line Number' <digit> <digit> <digit> ;
        <42> = 'Line' <digit> <digit> <digit> ;
        <21> = 'Line Number' <digit> <digit> <digit> <digit> ;
        <43> = 'Line' <digit> <digit> <digit> <digit> ;
        <22> = 'Output' ('Go' | 'Start' | 'End' ) ;
        <23> = 'Output Clear' ;
        <24> = 'Rebuild' ;
        <25> = 'Rebuild All' ;
        <26> = 'Project Settings' ;
        <27> = ('Set' | 'Clear' | 'Toggle' ) ('Breakpoint' | 'Bookmark' ) ;
        <28> = 'Edit Breakpoints' ;
        <44> = 'Breakpoints' ;
        <29> = 'Remove All Breakpoints' ;
        <45> = 'Remove Breakpoints' ;
        <30> = 'Exceptions' ;
        <31> = 'Reset Exceptions' ;
        <32> = 'Continue' ;
        <33> = 'Execute' ;
        <34> = 'Restart' ;
        <35> = 'Stop Debugging' ;
        <36> = 'Break Now' ;
        <37> = 'Single Step' ;
        <any> = <1>|<2>|<3>|<4>|<5>|<6>|<7>|<8>|<9>|<38>|<10>|<39>|<11>|<12>|<13>|<14>|<15>|<16>|<17>|<18>|<40>|<19>|<41>|<20>|<42>|<21>|<43>|<22>|<23>|<24>|<25>|<26>|<27>|<28>|<44>|<29>|<45>|<30>|<31>|<32>|<33>|<34>|<35>|<36>|<37>;
        <sequence> exported = <any>;
    """
    
    def initialize(self):
        self.load(self.gramSpec)
        self.currentModule = ("","",0)
        self.ruleSet1 = ['sequence']

    def gotBegin(self,moduleInfo):
        # Return if wrong application
        window = matchWindow(moduleInfo,'msdev','')
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

    def get_folder(self, list_buffer, functional, word):
        if word == 'Temp':
            list_buffer += 'C:\\Temp'
        elif word == 'Downloads':
            list_buffer += 'C:\\Users\\tan\\Downloads'
        elif word == 'Vocola':
            list_buffer += 'C:\\NatLink\\Vocola'
        elif word == 'NatLink':
            list_buffer += 'C:\\NatLink\\MacroSystem'
        return list_buffer

    def get_file(self, list_buffer, functional, word):
        if word == 'Temp':
            list_buffer += 'C:\\Temp\\temp.txt'
        return list_buffer

    # ('Open' | 'Close' | 'Recent' | 'Save') 'Workspace'
    def gotResults_1(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+f}'
            word = fullResults[0 + self.firstWord][0]
            if word == 'Open':
                top_buffer += 'w'
            elif word == 'Close':
                top_buffer += 'k'
            elif word == 'Recent':
                top_buffer += 'r'
            elif word == 'Save':
                top_buffer += 'v'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
            if len(words) > 2: self.gotResults_1(words[2:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 10, '(\'Open\' | \'Close\' | \'Recent\' | \'Save\') \'Workspace\'', e)
            self.firstWord = -1

    # 'Workspace' 1..10
    def gotResults_2(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+f}r'
            word = fullResults[1 + self.firstWord][0]
            top_buffer += self.convert_number_word(word)
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
            if len(words) > 2: self.gotResults_2(words[2:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 11, '\'Workspace\' 1..10', e)
            self.firstWord = -1

    # 'Open File'
    def gotResults_3(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+o}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_3(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 13, '\'Open File\'', e)
            self.firstWord = -1

    # 'Open File' <folder>
    def gotResults_4(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+o}'
            word = fullResults[1 + self.firstWord][0]
            top_buffer = self.get_folder(top_buffer, False, word)
            top_buffer += '{Enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
        except Exception, e:
            handle_error('msdev.vcl', 14, '\'Open File\' <folder>', e)
            self.firstWord = -1

    # 'Close' ('File' | 'That')
    def gotResults_5(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+f}c'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
            if len(words) > 2: self.gotResults_5(words[2:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 15, '\'Close\' (\'File\' | \'That\')', e)
            self.firstWord = -1

    # 'Save File'
    def gotResults_6(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+s}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_6(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 16, '\'Save File\'', e)
            self.firstWord = -1

    # 'Buffer' <file>
    def gotResults_7(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+o}'
            word = fullResults[1 + self.firstWord][0]
            top_buffer = self.get_file(top_buffer, False, word)
            top_buffer += '{Enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
        except Exception, e:
            handle_error('msdev.vcl', 18, '\'Buffer\' <file>', e)
            self.firstWord = -1

    # 'Find in Files'
    def gotResults_8(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+e}i'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_8(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 20, '\'Find in Files\'', e)
            self.firstWord = -1

    # 'Find in Files' <folder>
    def gotResults_9(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+e}i{Tab_2}'
            word = fullResults[1 + self.firstWord][0]
            top_buffer = self.get_folder(top_buffer, False, word)
            top_buffer += '{Shift+Tab_2}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
        except Exception, e:
            handle_error('msdev.vcl', 21, '\'Find in Files\' <folder>', e)
            self.firstWord = -1

    # 'Find in' <folder>
    def gotResults_38(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+e}i{Tab_2}'
            word = fullResults[1 + self.firstWord][0]
            top_buffer = self.get_folder(top_buffer, False, word)
            top_buffer += '{Shift+Tab_2}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
        except Exception, e:
            handle_error('msdev.vcl', 21, '\'Find in\' <folder>', e)
            self.firstWord = -1

    # 'Toggle Read Only'
    def gotResults_10(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+f}a{Right}*{Enter}{Shift+Tab}{End}{Shift+F10}r'
            top_buffer = do_flush(False, top_buffer);
            dragon_arg1 = ''
            dragon_arg1 += '1000'
            saved_firstWord = self.firstWord
            call_Dragon('Wait', 'i', [dragon_arg1])
            self.firstWord = saved_firstWord
            top_buffer += '{Alt+r}{Enter}{Esc}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_10(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 24, '\'Toggle Read Only\'', e)
            self.firstWord = -1

    # 'Read Only'
    def gotResults_39(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+f}a{Right}*{Enter}{Shift+Tab}{End}{Shift+F10}r'
            top_buffer = do_flush(False, top_buffer);
            dragon_arg1 = ''
            dragon_arg1 += '1000'
            saved_firstWord = self.firstWord
            call_Dragon('Wait', 'i', [dragon_arg1])
            self.firstWord = saved_firstWord
            top_buffer += '{Alt+r}{Enter}{Esc}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_39(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 24, '\'Read Only\'', e)
            self.firstWord = -1

    # 'Full Screen'
    def gotResults_11(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+v}u'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_11(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 28, '\'Full Screen\'', e)
            self.firstWord = -1

    # 'New' ('Search' | 'Find')
    def gotResults_12(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{F3}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
            if len(words) > 2: self.gotResults_12(words[2:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 29, '\'New\' (\'Search\' | \'Find\')', e)
            self.firstWord = -1

    # 'Find New'
    def gotResults_13(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+f}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_13(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 30, '\'Find New\'', e)
            self.firstWord = -1

    # 'Find That'
    def gotResults_14(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+F3}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_14(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 31, '\'Find That\'', e)
            self.firstWord = -1

    # 'Find' ('Down' | 'Up')
    def gotResults_15(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            word = fullResults[1 + self.firstWord][0]
            if word == 'Down':
                top_buffer += '{F3}'
            elif word == 'Up':
                top_buffer += '{Shift+F3}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
            if len(words) > 2: self.gotResults_15(words[2:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 32, '\'Find\' (\'Down\' | \'Up\')', e)
            self.firstWord = -1

    # 'Next Bookmark'
    def gotResults_16(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{F2}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_16(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 33, '\'Next Bookmark\'', e)
            self.firstWord = -1

    def get_digit(self, list_buffer, functional, word):
        list_buffer += self.convert_number_word(word)
        return list_buffer

    # 'Line Number'
    def gotResults_17(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+g}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_17(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 36, '\'Line Number\'', e)
            self.firstWord = -1

    # 'Line Number' <digit>
    def gotResults_18(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+g}'
            word = fullResults[1 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            top_buffer += '{Enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
        except Exception, e:
            handle_error('msdev.vcl', 37, '\'Line Number\' <digit>', e)
            self.firstWord = -1

    # 'Line' <digit>
    def gotResults_40(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+g}'
            word = fullResults[1 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            top_buffer += '{Enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
        except Exception, e:
            handle_error('msdev.vcl', 37, '\'Line\' <digit>', e)
            self.firstWord = -1

    # 'Line Number' <digit> <digit>
    def gotResults_19(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+g}'
            word = fullResults[1 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            word = fullResults[2 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            top_buffer += '{Enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 3
        except Exception, e:
            handle_error('msdev.vcl', 38, '\'Line Number\' <digit> <digit>', e)
            self.firstWord = -1

    # 'Line' <digit> <digit>
    def gotResults_41(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+g}'
            word = fullResults[1 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            word = fullResults[2 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            top_buffer += '{Enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 3
        except Exception, e:
            handle_error('msdev.vcl', 38, '\'Line\' <digit> <digit>', e)
            self.firstWord = -1

    # 'Line Number' <digit> <digit> <digit>
    def gotResults_20(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+g}'
            word = fullResults[1 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            word = fullResults[2 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            word = fullResults[3 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            top_buffer += '{Enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 4
        except Exception, e:
            handle_error('msdev.vcl', 39, '\'Line Number\' <digit> <digit> <digit>', e)
            self.firstWord = -1

    # 'Line' <digit> <digit> <digit>
    def gotResults_42(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+g}'
            word = fullResults[1 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            word = fullResults[2 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            word = fullResults[3 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            top_buffer += '{Enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 4
        except Exception, e:
            handle_error('msdev.vcl', 39, '\'Line\' <digit> <digit> <digit>', e)
            self.firstWord = -1

    # 'Line Number' <digit> <digit> <digit> <digit>
    def gotResults_21(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+g}'
            word = fullResults[1 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            word = fullResults[2 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            word = fullResults[3 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            word = fullResults[4 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            top_buffer += '{Enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 5
        except Exception, e:
            handle_error('msdev.vcl', 40, '\'Line Number\' <digit> <digit> <digit> <digit>', e)
            self.firstWord = -1

    # 'Line' <digit> <digit> <digit> <digit>
    def gotResults_43(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+g}'
            word = fullResults[1 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            word = fullResults[2 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            word = fullResults[3 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            word = fullResults[4 + self.firstWord][0]
            top_buffer = self.get_digit(top_buffer, False, word)
            top_buffer += '{Enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 5
        except Exception, e:
            handle_error('msdev.vcl', 40, '\'Line\' <digit> <digit> <digit> <digit>', e)
            self.firstWord = -1

    # 'Output' ('Go' | 'Start' | 'End')
    def gotResults_22(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+2}{Ctrl+'
            word = fullResults[1 + self.firstWord][0]
            if word == 'Go':
                top_buffer += ''
            elif word == 'Start':
                top_buffer += 'Home'
            elif word == 'End':
                top_buffer += 'End'
            top_buffer += '}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
            if len(words) > 2: self.gotResults_22(words[2:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 42, '\'Output\' (\'Go\' | \'Start\' | \'End\')', e)
            self.firstWord = -1

    # 'Output Clear'
    def gotResults_23(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer = do_flush(False, top_buffer);
            dragon_arg1 = ''
            dragon_arg1 += '4'
            dragon_arg2 = ''
            eval_template2_arg1 = ''
            eval_template2_arg1 += '{"n":1, "e":2, "s":3, "w":4, "ne":5, "se":6, "sw":7, "nw":8}[%a]'
            eval_template2_arg2 = ''
            eval_template2_arg2 += 'sw'
            dragon_arg2 += eval_template(eval_template2_arg1, eval_template2_arg2)
            saved_firstWord = self.firstWord
            call_Dragon('SetMousePosition', 'iii', [dragon_arg1, dragon_arg2])
            self.firstWord = saved_firstWord
            top_buffer = do_flush(False, top_buffer);
            dragon_arg1 = ''
            dragon_arg1 += '2'
            dragon_arg2 = ''
            eval_template2_arg1 = ''
            eval_template2_arg1 += '15*%a'
            eval_template2_arg2 = ''
            eval_template2_arg2 += '3'
            dragon_arg2 += eval_template(eval_template2_arg1, eval_template2_arg2)
            dragon_arg3 = ''
            eval_template2_arg1 = ''
            eval_template2_arg1 += '15*%a'
            eval_template2_arg2 = ''
            eval_template2_arg2 += '-4'
            dragon_arg3 += eval_template(eval_template2_arg1, eval_template2_arg2)
            saved_firstWord = self.firstWord
            call_Dragon('SetMousePosition', 'iii', [dragon_arg1, dragon_arg2, dragon_arg3])
            self.firstWord = saved_firstWord
            top_buffer = do_flush(False, top_buffer);
            dragon_arg1 = ''
            dragon_arg1 += '2'
            dragon_arg2 = ''
            dragon_arg2 += '1'
            saved_firstWord = self.firstWord
            call_Dragon('ButtonClick', 'ii', [dragon_arg1, dragon_arg2])
            self.firstWord = saved_firstWord
            top_buffer += 'r'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_23(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 43, '\'Output Clear\'', e)
            self.firstWord = -1

    # 'Rebuild'
    def gotResults_24(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{F7}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_24(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 47, '\'Rebuild\'', e)
            self.firstWord = -1

    # 'Rebuild All'
    def gotResults_25(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+b}r'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_25(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 48, '\'Rebuild All\'', e)
            self.firstWord = -1

    # 'Project Settings'
    def gotResults_26(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+F7}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_26(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 49, '\'Project Settings\'', e)
            self.firstWord = -1

    # ('Set' | 'Clear' | 'Toggle') ('Breakpoint' | 'Bookmark')
    def gotResults_27(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            word = fullResults[1 + self.firstWord][0]
            if word == 'Breakpoint':
                top_buffer += '{F9}'
            elif word == 'Bookmark':
                top_buffer += '{Ctrl+F2}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 2
            if len(words) > 2: self.gotResults_27(words[2:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 53, '(\'Set\' | \'Clear\' | \'Toggle\') (\'Breakpoint\' | \'Bookmark\')', e)
            self.firstWord = -1

    # 'Edit Breakpoints'
    def gotResults_28(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+F9}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_28(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 54, '\'Edit Breakpoints\'', e)
            self.firstWord = -1

    # 'Breakpoints'
    def gotResults_44(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+F9}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_44(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 54, '\'Breakpoints\'', e)
            self.firstWord = -1

    # 'Remove All Breakpoints'
    def gotResults_29(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+F9}{Alt+l}{Enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_29(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 55, '\'Remove All Breakpoints\'', e)
            self.firstWord = -1

    # 'Remove Breakpoints'
    def gotResults_45(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+F9}{Alt+l}{Enter}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_45(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 55, '\'Remove Breakpoints\'', e)
            self.firstWord = -1

    # 'Exceptions'
    def gotResults_30(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+d}e'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_30(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 56, '\'Exceptions\'', e)
            self.firstWord = -1

    # 'Reset Exceptions'
    def gotResults_31(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+d}e{Alt+t}'
            top_buffer = do_flush(False, top_buffer);
            dragon_arg1 = ''
            dragon_arg1 += 'OK'
            saved_firstWord = self.firstWord
            call_Dragon('ControlPick', 's', [dragon_arg1])
            self.firstWord = saved_firstWord
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_31(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 57, '\'Reset Exceptions\'', e)
            self.firstWord = -1

    # 'Continue'
    def gotResults_32(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{F5}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_32(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 59, '\'Continue\'', e)
            self.firstWord = -1

    # 'Execute'
    def gotResults_33(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+F5}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_33(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 60, '\'Execute\'', e)
            self.firstWord = -1

    # 'Restart'
    def gotResults_34(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Ctrl+Shift+F5}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_34(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 61, '\'Restart\'', e)
            self.firstWord = -1

    # 'Stop Debugging'
    def gotResults_35(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Shift+F5}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_35(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 62, '\'Stop Debugging\'', e)
            self.firstWord = -1

    # 'Break Now'
    def gotResults_36(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{Alt+d}b'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_36(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 63, '\'Break Now\'', e)
            self.firstWord = -1

    # 'Single Step'
    def gotResults_37(self, words, fullResults):
        if self.firstWord<0:
            return
        try:
            top_buffer = ''
            top_buffer += '{F10}'
            top_buffer = do_flush(False, top_buffer);
            self.firstWord += 1
            if len(words) > 1: self.gotResults_37(words[1:], fullResults)
        except Exception, e:
            handle_error('msdev.vcl', 64, '\'Single Step\'', e)
            self.firstWord = -1

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
