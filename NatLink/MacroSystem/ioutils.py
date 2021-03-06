#
# macro utilities for creating macro-behaviours
#
import logging
from sqlite3 import OperationalError, connect
from win32gui import GetFocus, SetFocus, ShowWindow, IsWindowVisible, GetWindowText, EnumWindows, BringWindowToTop, SetForegroundWindow
#import os
from subprocess import call
import time
import wmi

#logging.basicConfig(level=logging.INFO)

### DECORATORS ###

def sanitise_movement(func):
    def checker(*args,**kwargs):
#        print args
#        print kwargs
        ret = func(*args,**kwargs)
        return ret
    return checker

### CLASSES ###

class MacroObj():
    def __init__(self,string='',flags=0):
        self.string=string
        self.flags=flags

UPDATES_USAGE = "#keyboard macro (name, string, flag) tuples\n" \
                "#flag '0xff' prevents macro preprocessing e.g. vim/screen\n"

class FileStore():
    """ manage the storage of configurations to file """

    #logger=logging.getLogger('')

    def __init__(self,defaults_filename='defaults.conf',
                 updates_filename='updates.conf',
                 working_directory='c:/Natlink/Natlink/MacroSystem/',
                 preDict={},delim="|",
                 db_filename='natlink.db',
                 schema=None):
        #print os.getcwd()
#        self.updates_filename=updates_filename
        self.postDict=preDict
        self.delimchar=delim
        self.wd=working_directory
        count=0
        if schema:
            logging.info("schema present")
            count = self.readdb(schema)
        if not count:
            count = self.readfile(defaults_filename)
        if count:
            logging.info("%d macros"% count)
            count = self.readfile(updates_filename)
            print count
            if count:
                logging.info("%d updated macros"% count)
                count = self.writefile()
                logging.info("%d macros to file"% (count))
                if schema:
                    count = self.writedb(schema)
                    logging.info("%d macros to db, cleaning updates file"
                                 % (count))
                    with open(self.wd + updates_filename,'w') as myfile:
                        myfile.write(UPDATES_USAGE)
        else:
            logging.error('could not open : %s' %
                                  defaults_filename)

    def readfile(self, filename):
        logging.info("opening %s" % self.wd+filename)
        count=0
        try:
            with open(self.wd + filename,'r') as myfile:
                for line in myfile:
        #            logging.debug("reading %s" % line)
                    if not line.startswith('#'):
                        try:
            #                logging.debug(str(line.split('|',3)))
                            gram, macro, flags = line.split('|')
                            #logging.debug("%s  %s  %s" % (str(gram), str(macro), str(flags).strip(r'r\n')))
                            self.postDict[gram] = MacroObj(macro, int(flags.strip(r'r\n ')))
                            count+=1
                        except:
                            logging.info("%s line not a macro entry" % line)
        except:
            logging.error('could not open : %s' % filename)
        finally:
            return count

    def writefile(self, output_filename='output.conf'):
        logging.info("writing to file...")
        outfile_fd=open(self.wd + output_filename,'w')
        #eogging.debug('keys: %s' % self.postDict.keys())
        outfile_fd.write('keyboard macro (name, string, flag) tuples')
        count=0
        for gram, macroobj in self.postDict.iteritems():
            try:
                outfile_fd.write('\n' + str(self.delimchar).join([gram,
                                            macroobj.string,
                                            str(macroobj.flags)]))
                count+=1
            except:
                pass
        return count

    def readdb(self, schema, db_filename='natlink.db', table_name='kb_macros'):
        logging.info("reading from database...")
        count=0
        try:
            conn = connect(self.wd + db_filename)
            c = conn.cursor()
            col_names= schema.replace(' text','')
            c.execute("SELECT %s FROM %s" % (col_names, table_name))
            for row in c.fetchall():
                gram, macro_raw, flags = row
                macro=self.customdecodechars(macro_raw)
                self.postDict[gram] = MacroObj(macro, int(flags)) # .strip(r'r\n ')))
#                col_index=0
#                for col_name in col_names.split(','):
#                    #logging.info("col: %s=%s," % (col_name,row_decoded[col_index]))
#                    col_index+=1
#                print row
                count+=1
            conn.close()
        except:
            logging.info("error reading from database...")
        finally:
            return count
        # except sqlite3.OperationalError, err:
       #     logging.exception( "OperationalError: %s" % err)
       #     return 1

    def writedb(self, schema, db_filename='natlink.db', table_name='kb_macros'):
        logging.info("writing to database...")
        count = 0
        try:
            conn = connect(self.wd + db_filename)
            c = conn.cursor()
            # Create table
            c.execute("DROP TABLE %s" % (table_name))
            c.execute("CREATE TABLE %s (%s)" % (table_name, schema))
            for gram, macroobj in self.postDict.iteritems():
                # Insert a row of data
                macro_string=self.customencodechar(macroobj.string)
                print gram, macroobj.string, macro_string
                c.execute("INSERT INTO %s (%s) VALUES ('%s', '%s', '%s')" %
                        (table_name, schema.replace(' text', ''),
                         gram, macro_string, str(macroobj.flags)))
                conn.commit()
                count+=1
        #except Exception, err:
            conn.close()
        except OperationalError, err:
            logging.exception( "OperationalError: %s" % err)
        finally:
            return count

    def customencodechar(self, string):
        return string.replace("'","SNGL_QUOTE")

    def customdecodechars(self, string):
        if "SNGL_QUOTE" in string:
            new_string= str(string).replace("SNGL_QUOTE", "'")
            #logging.info("old %s, new %s" % (string, new_string))
        return string

class AppWindow:
    """class for application window object for phone screen"""

    def __init__(self, names, rect=None, hwin=None):
        self.winTitleNames = names
        self.winRect = rect
        self.winHandle = hwin
        # TODO: deprecate use of vertical offset here
        #self.vert_offset = 0
        #self.TOGGLE_VOFFSET = 9
        buttons = ['home', 'menu', 'back', 'search', 'call', 'end']
        self.mimicCmds = {}.fromkeys(buttons)


class Windows:
    """class for processing application windows"""
    
    def __init__(self, appDict={}, nullTitles=[]):
        self.appDict=appDict  # dictionary of application window objects
        self.nullTitles=nullTitles  # window titles to ignore
        self.skipTitle=None

    def _callBack_popWin(self, hwin, args):
        """ this callback function is called with handle of each top-level
        window. Window handles are used to check the of window in question is
        visible and if so it's title strings checked to see if it is a standard
        application (e.g. not the start button or natlink voice command itself).
        Populate dictionary of window title keys to window handle values. """
        #print '.' #self.nullTitles
        #nullTitles = self.nullTitles.append(self.skipTitle)
        #print nullTitles
        if IsWindowVisible(hwin):
            winText = GetWindowText(hwin).strip()
            nt = self.nullTitles + [self.skipTitle,]
            if winText and winText not in nt: # and\
                # enable duplicates #winText not in args.values():
                if winText.count('WinSCP') and winText != 'WinSCP Login':
                    if winText in args.values():
                        return
                args.update({hwin: winText})
            #else:
            #    logging.error('cannot retrieve window title %s' % winText)
#               and filter(lambda x: x in args[0], winText.split()):

    def winDiscovery(self, appName=None, winTitle=None, beginTitle=None,
                     skipTitle=None):
        """ support finding and focusing on application window or simple window
        title. Find the index and focuses on the first match of any of these.
        Applications within the application dictionary could have a number
        window_titles associated. """
        wins = {}
        hwin = None
        index = None

        # before enumerating available windows check we haven't already got a
        # window handle saved for this application window
        if appName:
            #logging.debug("{0}: looking for application {1}".format("window discovery (app)", appName))
            # trying to find window title of selected application within window
            # dictionary from an application window object. 
            app = self.appDict[str(appName)]  # AppWindow object
            try:
                # attempt to load a previously saved handle
                if app.winHandle:
                    logging.debug("{0}: found window handle for application {1}".format("window discovery (app)", appName))
                    #TO DO: investigate permission denied 
                    #test if window is already in foreground xdoesn't work
                    ##logging.debug(GetFocus())
                    #if not int(app.winHandle) == int(GetFocus()):
                    #SetFocus(int(app.winHandle))
                    try:
                        #ShowWindow(int(app.winHandle), 1) #SW_RESTORE)
                        SetForegroundWindow(app.winHandle)
                        BringWindowToTop(app.winHandle)
                        return (str(app.winHandle), wins)
                    except:
                        logging.debug("{0}: saved handle now invalid,"
                                      " removing entry".format("window discovery"
                                      " (app)"))
            except AttributeError:
                # window handle not valid for application, let's find it!
                logging.debug("{0}: window handle for application {1} not found".format("window discovery (app)", appName))
                pass

        # we haven't got the handle for this application window stored, to find
        # it we need to enumerate available windows on the screen

        # skip title if provided as a parameter
        self.skipTitle = skipTitle
        # TODO: uuse FindWindow with class instead.
        # losonumerate windows into dictionary  "wins" through callback function
        EnumWindows(self._callBack_popWin, wins)
        # clear the skip title that was passed into this function
        self.skipTitle = None
        total_windows = len(wins)
        logging.debug("%s: %d windows enumerated" % ("window discovery", total_windows))

#        # Check if there are more than 1 VNC viewer windows, In normal
#        # operation this will indicate receive buffer error w/ phone.
#        name = [proc.Name for proc in wmi.WMI().Win32_Process()]
#        #print names
#
#        if len(filter(lambda x: 'tvnviewer.exe' in x, names)) > 1:
#            print(str(self.__module__) +  "debug: closing existing VNC windows")
#            retval = 0
#            while True:
#                if retval != 0:
#                    break
#                print(str(self.__module__) +  "debug: killing VNC window")
#                retval = call(["taskkill", "/IM", "tvnviewer.exe", "/F"])
#                time.sleep(1)

        # check the titles provided in the window application object
        if appName:
            # check if winTitleNames is a list and add name to append to namelist
            if getattr(app.winTitleNames, 'append', None):
                logging.debug("{0}: looking for application window titles {1}".format("window discovery (app)", app.winTitleNames))
                try:
                    for v in app.winTitleNames:
                        if v in wins.values():
                            index = wins.values().index(v) 
                            break
#                    index = next(wins.values().index(v) for v in app.winTitleNames if v
#                                 in wins.values())
                    logging.debug("{0}: found window title {1}".format("window discovery (app)", v))
                except StopIteration:
                    pass
            else:
                if app.winTitleNames in wins.values():
                    logging.debug("{0}: found window title {1}".format("window discovery (app)", app.winTitleNames))
                    index = wins.values().index(app.winTitleNames)
                
        # if no window index has been found yet,
        if not index:
            # test for whole or partial window title text matches
            if winTitle and winTitle in wins.values():
                logging.debug("{0}: found window title {1}".format("window discovery (title)", winTitle))
                index = wins.values().index(winTitle)
            elif beginTitle and filter(lambda x: x.startswith(beginTitle), wins.values()):
                for v in wins.values():
                    if v.startswith(beginTitle):
                        index = wins.values().index(v)

        # have the target application window index in the wins
        # dictionary, store this handle and set focus
        if index is not None:
            logging.debug("index of application window: %s = %d" % (wins.values()[index],index))
            hwin = (wins.keys())[index]
            logging.debug("Name: {0}, Handle: {1}".format(wins[hwin], str(hwin)))
            try:
                #app.winHandle = hwin ## this is only a local scope
                self.appDict[str(appName)].winHandle = hwin  # AppWindow object
            except:
                pass
            # ShowWindow and SetForegroundWindow are the recommended functions
            #ShowWindow(int(hwin), 1) #SW_RESTORE)
            BringWindowToTop(hwin)
            SetForegroundWindow(hwin)
            #SetActiveWindow(int(hwin))
            #app.winRect = wg.GetWindowRect(hwin)
            #return (str(hwin), wins)
            return str(hwin)
        else:
            #return (None, wins)
            return None
