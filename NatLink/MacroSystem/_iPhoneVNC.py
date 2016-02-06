#
# Python Macro Language for Dragon NaturallySpeaking
#

import natlink
from natlinkutils import *
import win32gui as wg
from os import system
from subprocess import Popen
import ioutils as iou
import logging
from time import sleep
import wmi
from VocolaUtils import *

#logging.basicConfig(level=logging.INFO)

# local path constants
TUNNEL_BATCH=r"C:\win scripts\iphone usb.bat"
VNC_EXE=r'C:\Program Files\TightVNC\tvnviewer.exe'
VNC_CONF=r'C:\win scripts\localhost-5904.vnc'
SCP_EXE=r'C:\Program Files (x86)\WinSCP\winscp.exe'
SCP_SITE=r'iphone'

class ThisGrammar(GrammarBase):

    """ Class application objects to store grid reference of window
    buttons on Windows without "say what you see" Dragon NaturallySpeaking
    functionality. To be developed to use the either grid reference or
    MouseGrid coordinate utterances. There should be functionality to add
    buttons in real-time, need to be backed up in persistent database.
    with iOS seven use the "say" functionality to dictate, avoids key
    latching over the VNC connection """

    # function mappings to process coordinates for drag action
    dragDirMapx = {
        'right': lambda x,d: x+d, 'left': lambda x,d: x-d,
        'up': lambda x,d: x, 'down': lambda x,d: x,
    }
    dragDirMapy = {
        'right': lambda y,d: y, 'left': lambda y,d: y,
        'up': lambda y,d: y-d, 'down': lambda y,d: y+d
    }
    dispMap = {
        # default distances to drag (pixels)
        'right': 190,'left': 190,'up': 250,'down':250
    }

    # Todo: embed this list of strings within grammar to save space
    # mapping of keyboard keys to virtual key code to send as key input
    # VK_SPACE,VK_UP,VK_DOWN,VK_LEFT,VK_RIGHT,VK_RETURN,VK_BACK
    kmap = {
        'space': 0x20, 'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27,
        'enter': 0x0d, 'backspace': 0x08, 'delete': 0x2e, 'leftclick': 0x201,
        'rightclick': 0x204, 'doubleclick': 0x202}

    nullTitles = ['Default IME', 'MSCTFIME UI', 'Engine Window',
                  'VDct Notifier Window', 'Program Manager',
                  'Spelling Window', 'Start']

    # dictionary of application objects, preferably read from file
    appDict = {}
    # set application dict value to application object with possible window title list
    appDict.update({"iphoneWin": iou.AppWindow(["tans-iPhone",
                                                "tans-iphone.local",
                                                "vodafone",
                                                "iPhone - TightVNC Viewer"],
                                               None),
                    "xbmcChromeWin": iou.AppWindow(["XBMC - Google Chrome",],
                                                   None)})
    # appSelectionStr = '(' + str(appDict.keys()).strip('][').replace(',','|') +\
    #')'
    appSelectionStr = None

    windows = iou.Windows(appDict=appDict, nullTitles=nullTitles)

    # Todo: embed this list of strings within grammar to save space
    # list of android screencast buttons
    # InitialiseMouseGrid coordination commands
    windows.appDict["iphoneWin"].mimicCmds.update(
    #logging.debug(appDict["iphoneWin"].mimicCmds)
        {'back': ['one'],
         'cancel': ['three'],
         'personal hotspot toggle': [],
         'show': [],
         'home': [],
         'wake': [],
         'trust': ['four', 'nine'],
         'switch screens': ['eight'],
         'end': ['eight'],
         'answer': ['nine', 'seven', 'two', 'two'],
         'call': ['seven', 'five', 'eight'],
         'messages': ['one', 'five', 'eight'],
         'app store': ['five', 'seven'],
         'settings': ['six', 'eight'],
         'maps': ['five','one', 'two'],
         'what app': ['eight', 'three'],
         'maps text': ['two'],
         'message ok': ['five', 'eight'],
         'dismiss': ['five', 'eight','eight', 'eight'],
         'bluetooth on': ['three', 'eight', 'five', 'eight'],
         # drag context
         'drag up': ['eight','two','eight'],
         'drag down': ['two','eight', 'two', 'eight'],
         'drag left': ['nine','eight','three'],
         'drag right': ['seven','eight','three', 'two'],
         # call context
         'contacts': ['eight', 'eight'],
         'recent': ['seven', 'nine'],
         'favourites': ['seven', 'eight', 'four'],
         'keypad': ['nine', 'seven'],
         # messages context
         'new message': ['three', 'six'],
         'send message middle': ['six', 'eight', 'six'],
         'send message bottom': ['nine', 'eight'],
         'message text middle': ['five', 'eight'],
         'message text bottom': ['eight', 'eight'], #five', 'eight'],
         # recent context
         'view all': ['two', 'four'],
         'view missed': ['two', 'six'],
         # contacts list context
         '2828 search text': [],
         ## separate grammar for the below two
         #'select entry': [],
         #'select entry details': [],
         # contact context
         'first number': ['five','two'],
         'delete contact': ['eight',],
         'contact send message': ['four' ,'eight'],
         # keypad context
         'keypad call': ['eight',],
         '86 call again': [],
         # in call keypad context
         'incall keypad': ['five','two','two'],
         '82 zero': [],
         '18 one': [],
         '28 two': [],
         '38 tree': [],
         '43 four': [],
         '52 five': [],
         '62 six': [],
         '48 seven': [],
         '58 eight': [],
         '68 nine': [],
         'key star': [],
         'key hash': [],
         '381 contact call': [],
         '858 contact send message': [],
         '852 contact voice call': [],
         '98 call voicemail': [],
         '6 flicker': [],
         '8 end middle': [],
         '83 what SAP': [],
         '9 select route': [],
         '8528 start navigation': [],
         '776 stop navigation': [],
         '354 close overview': [],
         '7 call cancel': [],
         '9 call back': [],
         '2528 return to call': []
         })

    ## Note: recognition seems to be dependent on the numbers being spelt out in
    # words. Button location macros/strings should be persisted in file or
    # database. Redis?
    num_to_word =\
    ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

    # translate shorthand keys into proper dictionary entry
    # requires mapping numbers to words
    cDict = appDict["iphoneWin"].mimicCmds
    for k in cDict.keys():
      if str(k)[0].isdigit():
        coordinates,command=str(k).split(' ',1)
        coordinates_list= [num_to_word[int(i)] for i in coordinates]
#        print command
#        print coordinates_list
        del cDict[k]
        cDict.update({command: coordinates_list})

    # List of buttons
    appButtonStr = '|'.join(cDict.keys())

    gramSpec = """
        <iphoneselect> exported = select entry ({0}) [details];
        <iphonetap> exported = ({1});
        <iphonewake> exported = (iphone wake|iphone focus);
        <iphonefiles> exported = iphone files;
    """.format(str(range(20)).strip('[]').replace(', ','|'),appButtonStr)

    def initialize(self):
        self.load(self.gramSpec)
        self.activate('iphonewake')
        self.currentModule = ("","",0)
        self.ruleSet2 = ['iphonefiles', 'iphonetap','iphoneselect']  # context-dependent

    def gotBegin(self,moduleInfo):
        #self.activate('iphonewake',window=0)  # context-independent
        try:
            self.activate('iphonewake')
        except:
            pass
        # Return if wrong application
        window = matchWindow(moduleInfo,'tvnviewer','')
        if not window: return None
        self.firstWord = 0
        # Return if same window and title as before
        if moduleInfo == self.currentModule: return None
        self.currentModule = moduleInfo

        self.deactivateAll()
        title = string.lower(moduleInfo[1])
        if string.find(title,'') >= 0:
            for rule in self.ruleSet2:
                try:
                    self.activate(rule,window)
                except natlink.BadWindow:
                    pass

    def gotResults_iphonetap(self, words, fullResults):
        # rule to tap on the specific point on iPhone screen specified in cmd dictionary
        appName = 'iphoneWin'
        return self.winAction(words[:], appName)
        #return self.winAction(words[1 :], appName)

    def gotResults_iphonewake(self, words, fullResults):
        """Grammar to start iPhone vnc session. find or create connection to
		iPhone"""
        appName = 'iphoneWin'
#        retries = 2 #3
#        # try to locate and focus iPhone window
#       for i in xrange(retries):
        if 'wake' in words: 
            # clear stored handle
            app = self.appDict[str(appName)]  # AppWindow object
            try:
                app.winHandle = None
                print("{} window handle cleared".format(appName))
            except:
                pass
        # return index of application window title
        if self.windows.winDiscovery(appName=appName):
            #print "return from function discovery"
            # supplied the key of the intended window name
            return self.winAction(words[1:], appName)
        else:
            print(str(self.__module__) +  "debug: iphone window not found")
            # window doesn't exist, might need to start USB tunnel application
            # as well as vnc
            if 'itunnel_mux.exe' not in [c.Name for c in wmi.WMI().Win32_Process()]:
                print(str(self.__module__) +  "debug: itunnel process not found, starting...")
                itun_p = Popen([TUNNEL_BATCH, "&"])
            vnc_p = Popen([VNC_EXE, '-optionsfile=' + VNC_CONF])
            # vnc_p=Popen('C:\\Program Files (x86)\\TightVNC\\vncviewer.exe' +\
            #            ' localhost:5904 -password test')
            #vnc_p = Popen([VNC_EXE, '-host=127.0.0.1', '-port=5904', '-password=test'])
            # wait for creation
            print(str(self.__module__) +  "debug: waiting for VNC process creation")
            sleep(2)
            # window should now exist, discover again
            self.windows.winDiscovery(appName=appName)
            print "return from function discovery"
            # supplied the key of the intended window name
            return self.winAction(words[1:], appName)
#        print(str(self.__module__) +  "info:" 'retries exceeded, could not connect with phone ')

    def gotResults_iphonefiles(self, words, fullResults):
        """Grammar to start iPhone winscp session. find or create connection to
	    iPhone"""
        winscp_p = Popen([SCP_EXE, SCP_SITE])
        sleep(2)
#        appName = 'iphoneWin'
#        retries = 2 #3
#        # try to locate and focus iPhone window
#        for i in xrange(retries):
#            # window doesn't exist, might need to start USB tunnel application
#      	    # as well as vnc
#            if 'itunnel_mux.exe' not in [c.Name for c in wmi.WMI().Win32_Process()]:
#                print(str(self.__module__) +  "debug: itunnel process not found, starting...")
#                itun_p = Popen([TUNNEL_BATCH, "&"])
#           	winscp_p = Popen([SCP_EXE, SCP_SITE])
#	    print(str(self.__module__) +  "debug: waiting for SCP process creation")
#	    sleep(2)
#	    # window should now exist, discover again
#        print(str(self.__module__) +  "info:" 'retries exceeded, could not connect with phone ')

    def gotResults_iphoneselect(self, words, fullResults):
        """ Gives coordinates of an entry in a list on the iPhone. Receives the
        number of entries in the list (actually how many entries, given the
        size on the screen, would fit into the screen dimensions), the offset
        index of the first usable entry from top (how many entries Could fit
        above the first usable entry, give the index of the first usable entry)
        and the index of the desired entry. TODO: click on contact buttons on
        the right of entries """
        # static variables:
        appName = "iphoneWin"
        num_entries = 14
        offset_index = 3
        select_int=(int(words[2]))
        cmdwords= words[:2]
        self.gotResults_iphonetap(cmdwords, fullResults)
        # now target window should be in focus and ready
        # can use global variables populated by iphonetap
        hwin = self.windows.appDict[appName].winHandle
        if hwin:
            x,y,x1,y1 = wg.GetWindowRect(hwin)
            logging.debug('window Rect: %d,%d,%d,%d'% (x,y,x1,y1))
            if len(words) > 3 and str(words[3]) == 'details':
                # selectable blue Arrow on the right side of the contact
                x_ofs = x + 17*(x1 - x)/18
            else:
                # otherwise click in the centre (horizontal)
                x_ofs = x + (x1 - x)/2
            y_inc = (y1 - y)/num_entries
            y_ofs = y + y_inc/2 + (select_int + offset_index - 1)*y_inc
            logging.debug('horizontal: %d, vertical: %d, vertical increments: %d'%
                      (x_ofs,y_ofs,y_inc))
            if (select_int + offset_index - num_entries - 1) <= 0:
                # if entering search text,hide keypad
                natlink.playString('{enter}',0)
                self.click('leftclick',x=x_ofs,y=y_ofs)
        return

# use playstring instead
#    def press(self, key='space'):
#        event = self.kmap[key]
#        natlink.playEvents([(wm_keydown, event, 0),(wm_keyup, event, 0)])
    def sanitise_movement(func):
        def checker(*args,**kwargs):
            print args
            print kwargs
            ret = func(*args,**kwargs)
            return ret
        return checker

    def getDragPoints(self,x,y,displacement,dragDirection):
        """ take current cursor position, displacement and direction,
        receives starting coordinates and returns end coordinates.
        axis displacement is in direction of "dragDirection". e.g. to Drag right;
        Place mouse at beginning of desired Drag action, add displacement
        from x coordinate and return the new coordinates """

        return (self.dragDirMapx[dragDirection](x,displacement),
                   self.dragDirMapy[dragDirection](y,displacement))

    #@sanitise_movement
    def drag(self, dragDirection='up', startPos=None, dist=4):
        displacement = self.dispMap[dragDirection]
        call_Dragon('RememberPoint', '', [])
        x, y = natlink.getCursorPos()
        newx,newy = self.getDragPoints(x,y,displacement,dragDirection)
        natlink.playEvents([(wm_mousemove, newx, newy)])
        call_Dragon('DragToPoint', 'i', [])

    def click(self, clickType='leftclick', x=None, y=None):
        """get the equivalent event code of the type of mouse event to perform
        leftclick, rightclick, rightdouble-click (see kmap)"""
        event = self.kmap[clickType]
        # play events down click and then release (for left double click
        # increment from left button up event which produces no action
        # then when incremented, performs the double-click)
        # if coordinates are not supplied, just click
        if getattr(event, 'conjugate'):
            if not (x or y):
                x, y = natlink.getCursorPos()
            # TODO: remove this, too niche to be here
            # apply vertical offset dependent on presence of "personal hotspot"
            # bar across the top of the screen
            #y += self.windows.appDict[appName].vert_offset
            #y += self.vert_offset
            #logging.debug('clicking at: %d, %d'% (x,y))
            natlink.playEvents(
                [(wm_mousemove, x, y), (event, x, y), (event + 1, x, y)])
        else:
            logging.error(' incorrect click look up for the event %s'% str(clickType))
            # default to
            natlink.recognitionMimic(['mouse', 'click'])

    def winAction(self, actionKey='', appName='iphoneWin'):
	""" This is the general case where an action on the iPhone screen is executed,
	some special cases are and handled in their own grammers and ignored below"""
        # concatenate actionKey
        if getattr(actionKey, 'insert'):
            actionKey = ' '.join(actionKey)
            logging.debug(str(self.__module__) +  "debug: action Key of command concatenated: %s"% actionKey)
        # assuming the correct window is in focus
        # wake. Recognition mimic doesn't seem to be a good model. Something to
        # do with speed ofplayback etc. Grammar not always recognised as a
        # command.
        natlink.playString('{space}', 0x00)
        app = self.windows.appDict[str(appName)]
        mimicCmds = app.mimicCmds
        gramList = []
        if str(actionKey) in mimicCmds:
            # we want to get out of grid mode aftermouse positioning
            # special cases first.
            if str(actionKey) == 'home':
                natlink.recognitionMimic(['mouse', 'window'])
                natlink.recognitionMimic(['go'])
                self.click('rightclick')
            elif str(actionKey) == 'wake':
                print 'Wake action'
                natlink.recognitionMimic(['mouse', 'window'])
                time.sleep(0.5)
                # first set pointer position in bottom left of phone
                natlink.recognitionMimic(['seven','five', 'nine'])
                time.sleep(0.5)
                natlink.recognitionMimic(['go'])
                time.sleep(0.5)
                print 'Right click to focus window'
                self.click('rightclick')
                time.sleep(0.5)
                # then slide right to unlock
                self.drag(dragDirection='right', dist=2)
#            elif str(actionKey) == 'personal hotspot toggle':
#                if app.vert_offset:
#                    app.vert_offset = 0
#                else:
#                    app.vert_offset = app.TOGGLE_VOFFSET
            elif str(actionKey).startswith("select"):
                pass # function continued in its own handler
            elif str(actionKey).startswith("show"):
                pass
            elif str(actionKey).startswith("drag"):
                natlink.recognitionMimic(['mouse', 'window'])
                gramList = mimicCmds[actionKey]
                natlink.recognitionMimic(gramList)
                natlink.recognitionMimic(['go'])
                self.drag(dragDirection=actionKey.split()[1])
            else:
		# general case, process recognised grammar list and click after
                natlink.recognitionMimic(['mouse', 'window'])
                gramList = mimicCmds[actionKey]
#                print(str(self.__module__) + "debug: Grammer list for action '{0}': {1}".format(
#                    actionKey, gramList))
                natlink.recognitionMimic(gramList)
                natlink.recognitionMimic(['go'])
                self.click('leftclick')
            return 0
        else:
            print(str(self.__module__) +  'error:unknown actionKey')
            return 1

thisGrammar = ThisGrammar()
thisGrammar.initialize()


def unload():
    global thisGrammar
    if thisGrammar:
        thisGrammar.unload()
    thisGrammar = None
