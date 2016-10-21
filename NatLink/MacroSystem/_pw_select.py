#
# Python Macro Language for Dragon NaturallySpeaking
# Passwords 
#

import natlink
from natlinkutils import *

class ThisGrammar(GrammarBase):

    gramSpec = """
        <start> exported =
        insert (password ( 1 | 2 | 3 | 4 | 5 | 6 ) | email ( 1 | 2 | 3 ) | logon ( 1 | 2 | 3 | 4 | 5 | 6 | 7 ) | address | address work | employee number | mobile phone | home phone | static );
    """

    def gotResults_start(self,words,fullResults):
        # execute a control-left drag down 30 pixels
        #x,y = natlink.getCursorPos()
        if words [1] == 'password':
            if (int(words[2]) == 2):
                natlink.playString('siemens') 
            elif (int(words[2]) == 3):
                natlink.playString('ellenstewart')
            elif (int(words[2]) == 4):
                natlink.playString('nabarrostewart')
            elif (int(words[2]) == 5):
                natlink.playString('cideric306')
            elif (int(words[2]) == 6):
                natlink.playString('s13m3ns')
            elif (int(words[2]) == 7):
                natlink.playString('chemring1')
            else:
                natlink.playString('test')
        elif words [1] == 'logon':
            if (int(words[2]) == 2):
                natlink.playString('admin') 
            elif (int(words[2]) == 3):
                natlink.playString('tnxvn1')
            elif (int(words[2]) == 4):
                natlink.playString('resnet1')
            elif (int(words[2]) == 5):
                natlink.playString('tan.gotdns.com')
            elif (int(words[2]) == 6):
                natlink.playString('tans.gotdns.com')
            else:
                natlink.playString('GER\\tanabarr')
        elif words [1] == 'address':
            if words [2] == 'work':
                natlink.playString("""
Tom Nabarro
Intel Corporation
Pipers way
Swindon
SN3 1RJ

+44 7786 260986 is my mobile
+44 1793 403000 is Intel switchboard
""")
            else:
                natlink.playString('The Limes, 87 High St, Standlake, Oxfordshire, ox29 7rh.') 
        elif words [1] == 'employee':
            if words [2] == 'pin':
                    natlink.playString('46912944') 
            elif words [2] == 'number':
                    natlink.playString('10695475') 
        elif words [1] == 'home':
                natlink.playString('01865 300939') 
        elif words [1] == 'mobile':
                natlink.playString('07786260986') 
        elif words [1] == 'static':
                natlink.playString('46.227.149.232') 
        else:
            if (int(words[2]) == 3):
                natlink.playString('whizz2000@hotmail.com') 
            elif (int(words[2]) == 2):
                natlink.playString('tom.nabarro@outlook.com') 
            else:
                natlink.playString('tom.nabarro@intel.com')
        
    '''
        natlink.playEvents( [ (wm_syskeydown,0x12,1),
                              (wm_keydown,0x09,1),
                              (wm_keyup,0x09,1),#(wm_lbuttondown,x,y),
                              (wm_keydown,0x09,1),
                              (wm_keyup,0x09,1),#(wm_lbuttondown,x,y),
                              #(wm_mousemove,x,y+30),
                              #(wm_lbuttonup,x,y+30),
                               (wm_syskeyup,0x12,1)
                            ] )
        ( 1 | 2 );
    '''

    def initialize(self):
        self.load(self.gramSpec)
        self.activateAll()

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
