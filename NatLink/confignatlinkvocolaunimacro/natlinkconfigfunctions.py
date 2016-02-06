# coding=latin-1
#
# natlinkconfigfunctions.py
#   This module performs the configuration functions.
#   called from natlinkconfig (a wxPython GUI),
#   or directly, see below
#
#   Quintijn Hoogenboom, January 2008
#
"""

With the functions in this module NatLink can be configured.

This can be done in three ways:
-Through the command line interface (CLI) which is started automatically
 when this module is run (with Pythonwin, IDLE, or command line of Python)
-On the command line, using one of the different command line options 
-Through the configure GUI (natlinkconfig.py), which calls into this module
 This last one needs wxPython to be installed.

*** the core directory is relative to this directory ...
    ...and will be searched for first.

Afterwards can be set:

DNSInstallDir
    - if not found in one of the predefined subfolders of %PROGRAMFILES%,
      this directory can be set in HKCU\Software\Natlink.
      Functions: setDNSInstallDir(path) (d path) and clearDNSInstallDir() (D)
      
DNSINIDir
    - if not found in one of the subfolders of %COMMON_APPDATA%
      where they are expected, this one can be set in HKCU\Software\Natlink.
      Functions: setDNSIniDir(path) (c path) and clearDNSIniDir() (C)

When NatLink is enabled natlink.pyd is registered with
      win32api.WinExec("regsvr32 /s pathToNatlinkPyd") (silent)

It can be unregistered through function unregisterNatlinkPyd() see below.      

Other functions inside this module, with calls from CLI or command line:

enableNatlink()  (e)/disableNatlink() (E)

setUserDirectory(path) (n path) or clearUserDirectory() (N)
etc.

More at the bottom, with the CLI description...

"""

ObsoleteStatusKeys = ('VocolaUsesSimpscrp', 'VocolaCommandFilesEditor')
#--------- two utility functions:
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

def getCoreDir(thisDir):
    """get the NatLink core folder, relative from the current folder

    This folder should be relative to this with ../MacroSystem/core and should
    contain natlinkmain.p, natlink.pyd, and natlinkstatus.py

    If not found like this, prints a line and returns thisDir
    SHOULD ONLY BE CALLED BY natlinkconfigfunctions.py
    """
    coreFolder = os.path.normpath( os.path.join(thisDir, '..', 'MacroSystem', 'core') )
    if not os.path.isdir(coreFolder):
        print 'not a directory: %s'% coreFolder
        return thisDir
##    PydPath = os.path.join(coreFolder, 'natlink.pyd')
    mainPath = os.path.join(coreFolder, 'natlinkmain.py')
    statusPath = os.path.join(coreFolder, 'natlinkstatus.py')
##    if not os.path.isfile(PydPath):
##        print 'natlink.pyd not found in core directory: %s'% coreFolder
##        return thisDir
    if not os.path.isfile(mainPath):
        print 'natlinkmain.py not found in core directory: %s'% coreFolder
        return thisDir
    if not os.path.isfile(statusPath):
        print 'natlinkstatus.py not found in core directory: %s'% coreFolder
        return thisDir
    return coreFolder
hadFatalErrors = []
def fatal_error(message, new_raise=None):
    """prints a fatal error when running this module
    
    print only the first!
    """
    if not hadFatalErrors:
        print '\nnatlinkconfigfunctions failed because of fatal error:'
        print
        print message
        print
        print 'Try to close Dragon and then rerun this program (in elevated mode).'
        print 'If this does not work, try to reinstall NatLink.'
        print
    if message not in hadFatalErrors:
        hadFatalErrors.append(message)
    if new_raise:
        raise new_raise
#-----------------------------------------------------

import os, sys, win32api, shutil, re, pywintypes 
thisDir = getBaseFolder(globals())
coreDir = getCoreDir(thisDir)
if thisDir == coreDir:
    raise IOError('natlinkconfigfunctions cannot proceed, coreDir not found...')
# appending to path if necessary:
if not os.path.normpath(thisDir) in sys.path:
    print 'inserting %s to pythonpath...'% thisDir
    sys.path.insert(0, thisDir)
    
if not os.path.normpath(coreDir) in sys.path:
    print 'inserting %s to pythonpath...'% coreDir
    sys.path.insert(0, coreDir)

# from core directory, use registry entries from CURRENT_USER/Software/Natlink:
import natlinkstatus, natlinkcorefunctions, RegistryDict

import os, os.path, sys, getopt, cmd, types, string, win32con

class NatlinkConfig(natlinkstatus.NatlinkStatus):
    """performs the configuration tasks of NatLink

    userregnl got from natlinkstatus, as a Class (not instance) variable, so
    should be the same among instances of this class...
    
    the checkCoreDirectory function is automatically performed at start, to see if the initialisation does not
    take place from another place as the registered natlink.pyd...
    
    
    """
    def __init__(self):
        natlinkstatus.NatlinkStatus.__init__(self, skipSpecialWarning=1)
        self.changesInInitPhase = 0
        self.DNSName = self.getDNSName()
    
    def checkCoreDirectory(self):
        """check if coreDir (from this file) and coreDirectory (from natlinkstatus) match, if not, raise error
        """
        coreDir2 = self.getCoreDirectory()
        if coreDir2.lower() != coreDir.lower():
            fatal_error('ambiguous core directory,\nfrom this module: %s\from status in natlinkstatus: %s'%
                                              (coreDir, coreDir2))
    
    def configCheckNatlinkPydFile(self):
        """see if natlink.pyd is in core directory, if not copy from correct version
        """
        self.checkedUrgent = 1
        if sys.version.find("64 bit") >= 0:
            print '============================================='
            print 'You installed a 64 bit version of python.'
            print 'NatLink cannot run with this version, please uninstall and'
            print 'install a 32 bit version of python, see http://qh.antenna.nl/unimacro,,,'
            print '============================================='
            return
        
        
        
        coreDir2 = self.getCoreDirectory()
        if coreDir2.lower() != coreDir.lower():
            fatal_error('ambiguous core directory,\nfrom this module: %s\from status in natlinkstatus: %s'%
                                              (coreDir, coreDir2))
        currentPydPath = os.path.join(coreDir, 'natlink.pyd')
        
        if not os.path.isfile(currentPydPath):
            key = 'NatlinkPydRegistered'
            print '%s does not exist, remove "%s" from natlinkstatus.ini and setup up new pyd file...'% (currentPydPath, key)
            self.userregnl.delete(key)
            natlinkPydWasAlreadyThere = 0
        else:
            natlinkPydWasAlreadyThere = 1
        wantedPyd = self.getWantedNatlinkPydFile()       # wanted original based on python version and Dragon version
        if self.checkNatlinkPydFile(fromConfig=1) == 1:  # check the need for replacing natlink.pyd without messages...
            self.checkedUrgent = None
            return 1 # all is well

        # for message:
        #fatal_error("The current file natlink.pyd is not available, the correct version or outdated, try to replace it by the proper (newer) version...")
        ## now go on with trying to replace natlink.pyd with the correct version and register it...
        wantedPydPath = os.path.join(coreDir, 'PYD', wantedPyd)
        if natlinkPydWasAlreadyThere:
            self.changesInInitPhase = 1
            result = self.copyNatlinkPydPythonVersion(wantedPydPath, currentPydPath)
            self.registerNatlinkPyd()
            if result:
                print '-'*30
                print 'Copying and registering the latest natlink.pyd was succesful.'
                print 'You can now close this program and restart Dragon.'
                print '-'*30
        else:
            result = self.copyNatlinkPydPythonVersion(wantedPydPath, currentPydPath)
            self.registerNatlinkPyd(silent=1)
        
        return result  # None if something went wrong 1 if all OK      

    def removeNatlinkPyd(self):
        """remove the natlink.pyd file (Dragon should be switched off)
        
        in order to redo the copyNatlinkPydPythonVersion again
        """
        coreDir = self.getCoreDirectory()
        currentPydFile = os.path.join(coreDir, 'natlink.pyd')
        if os.path.isfile(currentPydFile):
            try:
                os.remove(currentPydFile)
            except (WindowsError, IOError):
                fatal_error('cannot remove natlink.pyd from the core directory: %s'% coreDir)
                return
        if os.path.isfile(currentPydFile):
            fatal_error('strange, could not remove "natlink.pyd" from the core directory: "%s"'% coreDir)
            return
        # ok:
        return 1  # 

    def copyNatlinkPydPythonVersion(self, wantedPydFile, currentPydFile):
        """copy the natlink.pyd from the correct version"""
        if os.path.isfile(currentPydFile):
            self.unregisterNatlinkPyd()
            try:
                os.remove(currentPydFile)
            except WindowsError:
                fatal_error('cannot remove currentPydFile "%s",\nProbably you must exit Dragon first'% currentPydFile)
                return
            
        if os.path.isfile(wantedPydFile):
            try:
                shutil.copyfile(wantedPydFile, currentPydFile)
                print 'copied pyd (=dll) file %s to %s'% (wantedPydFile, currentPydFile)
            except:
                fatal_error("Could not copy %s to %s\nProbably you need to exit Dragon first."% (wantedPydFile, currentPydFile))
                return
        else:
            fatal_error("wantedPydFile %s is missing! Cannot copy to natlink.pyd/natlink.pyd"% wantedPydFile)
            return
        return 1
        
    def getHKLMPythonPathDict(self, flags=win32con.KEY_ALL_ACCESS, recursive=False):
        """returns the dict that contains the PythonPath section of HKLM
        
        Overload for config program, automatically set or repair the pythonpath variable if the format is not ok
        """
        version = self.getPythonVersion()
        if not version:
            fatal_error("no valid Python version available")
            return None, None
        dottedVersion = version[0] + "." + version[1]
        pythonPathSectionName = r"SOFTWARE\Python\PythonCore\%s\PythonPath"% dottedVersion
        # key MUST already exist (ensure by passing flags=...:
        #try:
        lmPythonPathDict = RegistryDict.RegistryDict(win32con.HKEY_LOCAL_MACHINE, pythonPathSectionName, flags=flags)
        #except:
        #    fatal_error("registry section for pythonpath does not exist yet: %s,  probably invalid Python version: %s"%
        #                     (pythonPathSectionName, version))
        #    return None, None
        if 'NatLink' in lmPythonPathDict.keys():
            subDict = lmPythonPathDict['NatLink']
            if isinstance(subDict, RegistryDict.RegistryDict):
                if '' in subDict.keys():
                    value = subDict['']
                    if value and type(value) in (str, unicode):
                        # all well (only the value is not tested yet):
                        return lmPythonPathDict, pythonPathSectionName                        
        # not ok, repair the setting, admin rights needed:
        if recursive:
            fatal_error("Registry entry NatLink in pythonpath cannot be set correct, This can (hopefully) be solved by closing Dragon and then running the NatLink/Unimacro/Vocola Config program with administrator rights.run this program")
            return None, None
        print '==== Set NatLink setting in PythonPath section of registry to "%s"'% coreDir
        lmPythonPathDict['NatLink'] = {'': coreDir}
        return self.getHKLMPythonPathDict(recursive=True)
                                 
 
    def checkPythonPathAndRegistry(self):
        """checks if core directory is

        1. in the sys.path
    ###    2. in the registry keys of HKLM\SOFTWARE\Python\PythonCore\2.3\PythonPath\NatLink

        the latter part is inserted again, as, for some reason the automatic loading of
        natlinkmain needs the core directory in its path. Only take the core dir now!!
        
        Instead the status.checkSysPath() function checks the existence of the core, base and user
        directories in the sys.path and sets then if necessary.

        If this last key is not there or empty
        ---set paths of coreDirectory
        ---register natlink.pyd
        It is probably the first time to run this program.

        If the settings are conflicting, either
        ---you want to reconfigure NatLink in a new place (these directories)
        ---you ran this program from a wrong place, exit and start again from the correct directory

        """
        self.checkedUrgent = None
        if __name__ == '__main__':
            print "checking PythonPathAndRegistry"
        try:
            lmPythonPathDict, PythonPathSectionName = self.getHKLMPythonPathDict(flags=win32con.KEY_ALL_ACCESS)
        except pywintypes.error:
            mess =  'The section "NatLink" does not exist and cannot be created in the registry. You probably should run this program with administrator rights'
            self.warning(mess)
            self.checkedUrgent = 1
            return None, None
        coreDir2 = self.getCoreDirectory()
        if coreDir2.lower() != coreDir.lower():
            fatal_error('ambiguous core directory,\nfrom this module: %s\from status in natlinkstatus: %s'%
                                              (coreDir, coreDir2))
        # adding the relevant directories to the sys.path variable:
        #self.checkSysPath() ## not needed in config program
        
        pathString = coreDir
##        if lmPythonPath:
##            print 'lmPythonPath: ', lmPythonPath.keys()
        if not 'NatLink' in lmPythonPathDict:
            # first time install, silently register
            self.registerNatlinkPyd(silent=1)
            self.setNatlinkInPythonPathRegistry()
            return 1
        
        lmNatlinkPathDict = lmPythonPathDict['NatLink']
        Keys = lmNatlinkPathDict.keys()
        if not Keys:
            # first time install Section is there, but apparently empty
            self.registerNatlinkPyd(silent=1)
            self.setNatlinkInPythonPathRegistry()
            return 1
        if Keys != [""]:
            if '' in Keys:
                Keys.remove("")
            fatal_error("The registry section of the pythonPathSection of HKEY_LOCAL_MACHINE:\n\tHKLM\%s\ncontains invalid keys: %s, remove them with the registry editor (regedit)\nAnd rerun this program"%
                        (PythonPathSectionName+r'\NatLink', Keys))
            

        # now section has default "" key, proceed:            
        oldPathString = lmNatlinkPathDict[""]
        if oldPathString.find(';') > 0:
            print 'remove double entry, go back to single entry'
            self.setNatlinkInPythonPathRegistry()

        oldPathString = lmNatlinkPathDict[""]
        if oldPathString.find(';') > 0:
            fatal_error("did not fix double entry in registry setting  of the pythonPathSection of HKEY_LOCAL_MACHINE:\n\tHKLM\%s\ncontains more entries separated by ';'. Remove with the registry editor (regedit)\nAnd rerun this program"%PythonPathSectionName+r'\NatLink')
        if not oldPathString:
            # empty setting, silently register
            self.registerNatlinkPyd(silent=1)
            self.setNatlinkInPythonPathRegistry()
            return 1
            
        if oldPathString.lower() == pathString.lower():
            return 1 # OK
        # now for something more serious:::
        text = \
"""
The PythonPath for NatLink does not match in registry with what this program
expects

---settings in Registry: %s
---wanted settings: %s

You probably just installed NatLink in a new location
and you ran the config program for the first time.

If you want the new settings, (re)register natlink.pyd (r)

And rerun this program...

Close %s (including Quick Start Mode), and all other Python applications
before rerunning this program.  Possibly you have to restart your computer.

If you do NOT want these new settings, simply close this program and run
from the correct place.
"""% (oldPathString, pathString, self.DNSName)
        self.warning(text)
        self.checkedUrgent = 1

    def checkIniFiles(self):
        """check if INI files are consistent
        this is done through the

        """
        result = self.NatlinkIsEnabled(silent=1)
        if result == None:
            self.disableNatlink(silent=1)
            result = self.NatlinkIsEnabled(silent=1)
            if result == None:
                text = \
"""NatLink INI file settings are inconsistently,
and cannot automatically be disabled.

Try to disable again, acquire administrator rights or report this issue
"""
                self.warning(text)
                return None
            else:
                text = \
"""NatLink INI file settings were inconsistent;
This has been repaired.

NatLink is now disabled.
"""
                self.warning(text)
        return 1
            
            
    def warning(self,text):
        """is currently overloaded in GUI"""
        if isinstance(text, basestring):
            T = text
        else:
            # list probably:
            T = '\n'.join(text)
        print '-'*60
        print T
        print '='*60
        return T
    
    def error(self,text):
        """is currently overloaded in GUI"""
        if isinstance(text, basestring):
            T = text
        else:
            # list probably:
            T = '\n'.join(text)
        print '-'*60
        print T
        print '='*60
        return T
    

    def message(self, text):
        """prints message, can be overloaded in configureGUI
        """
        if isinstance(text, basestring):
            T = text
        else:
            # list probably:
            T = '\n'.join(text)
        print '-'*60
        print T
        print '='*60

    def setstatus(self, text):
        """prints status, should be overloaded in configureGUI
        """
        if isinstance(text, basestring):
            T = text
        else:
            # list probably:
            T = '\n'.join(text)
        print '-'*60
        print T
        print '='*60

        
    def setNatlinkInPythonPathRegistry(self):
        """sets the HKLM setting of the Python registry

        do this only when needed...

        """
        lmPythonPathDict, pythonPathSectionName = self.getHKLMPythonPathDict(flags=win32con.KEY_ALL_ACCESS)
        pathString = os.path.normpath(os.path.abspath(coreDir))
        NatlinkSection = lmPythonPathDict.get('NatLink', None)
        if NatlinkSection:
            oldPath = NatlinkSection.get('', '')
        else:
            oldPath = ''
        if oldPath.lower() != pathString.lower():
            try:
                lmPythonPathDict['NatLink']  = {'': pathString}
                self.warning('Set registry setting PythonPath/NatLink to: %s"'% pathString)
            except:
                self.warning("cannot set PythonPath for NatLink in registry, probably you have insufficient rights to do this, try to run the config program with administrator rights")


    def checkNatlinkRegistryPathSettings(self, secondTry=None):
        """check if the register pythonpath variable present and matches with the previous path
        
        """
        regDict, sectionName = self.getHKLMPythonPathDict(flags=win32con.KEY_ALL_ACCESS)
        try:
            value = regDict['NatLink']
        except:
            # new install, new key:
            if not secondTry:
                try:
                    regDict['NatLink'] = coreDir
                except:
                    self.error("cannot set PythonPath/NatLink setting, run Config program with administrator rights")
                    return
                else:
                    # check if setting is completed:
                    return self.checkNatlinkRegistryPathSettings(secondTry=1)
        # key was there already:
        wantedValue = coreDir
        if value == wantedValue:
            print 'registry PythonPath/NatLink setting ok: %s'% value
            return 1
        # value different from current value:
        if secondTry:
            self.error("cannot set correct PythonPath/NatLink setting, run config program with administrator rights")
            return

        # now change to new value:
        self.warning("change PythonPath/NatLink setting in registry (HKLM section) to: %s"% coreDir)
        regDict['NatLink'] = coreDir
        return self.checkNatlinkRegistryPathSettings(secondTry=1)
        
            
        
    #def clearNatlinkFromPythonPathRegistry(self):
    #    """clears the HKLM setting of the Python registry"""
    #    lmPythonPathDict, pythonPathSectionName = self.getHKLMPythonPathDict()
    #    baseDir = os.path.join(coreDir, '..')
    #    pathString = ';'.join(map(os.path.normpath, [coreDir, baseDir]))                                            
    #    if 'NatLink' in lmPythonPathDict.keys():
    #        try:
    #            del lmPythonPathDict['NatLink']
    #        except:
    #            self.warning("cannot clear Python path for NatLink in registry (HKLM section), probably you have insufficient rights to do this")

    def printInifileSettings(self):
        print 'Settings in file "natlinkstatus.ini" in\ncore directory: "%s"\n'% self.getCoreDirectory()
        Keys = self.userregnl.keys()
        Keys.sort()
        for k in Keys:
            print "\t%  s:\t%s"% (k, self.userregnl.get(k))
        print "-"*60


    def setDNSInstallDir(self, new_dir):
        """set in registry local_machine\natlink

        """
        key = 'DNSInstallDir'
        if os.path.isdir(new_dir):
            programDir = os.path.join(new_dir, 'Program')
            if os.path.isdir(programDir):
                print 'set DNS Install Directory to: %s'% new_dir
                self.userregnl.set(key, new_dir)
            else:
                mess =  "setDNSInstallDir, directory misses a Program subdirectory: %s"% new_dir
                print mess
                return mess
        else:
            mess = "setDNSInstallDir, not a valid directory: %s"% new_dir
            print mess
            return mess
        
    def clearDNSInstallDir(self):
        """clear in registry local_machine\natlink\natlinkcore

        """
        key = 'DNSInstallDir'
        self.userregnl.delete(key)
        
    def setDNSIniDir(self, new_dir):
        """set in registry local_machine\natlink

        """
        key = 'DNSIniDir'
        if os.path.isdir(new_dir):
            # check INI files:
            nssystem = os.path.join(new_dir, self.NSSystemIni)
            nsapps = os.path.join(new_dir, self.NSAppsIni)
            if not os.path.isfile(nssystem):
                mess = 'folder %s does not have the INI file %s'% (new_dir, self.NSSystemIni)
                print mess
                return mess
            if not os.path.isfile(nsapps):
                mess =  'folder %s does not have the INI file %s'% (new_dir, self.NSAppsIni)
                print mess
                return mess
            self.userregnl.set(key, new_dir)
        else:
            mess = "setDNSIniDir, not a valid directory: %s"% new_dir
            print mess
            return mess
            
        
    def clearDNSIniDir(self):
        """clear in registry local_machine\natlink\

        """
        key = 'DNSIniDir'
        self.userregnl.delete(key)

    def setUserDirectory(self, v):
        key = 'UserDirectory'
        if v.startswith("~") or v.find("%") >= 0:
            print "Setting NatLinkUserDir to %s"% v
            self.userregnl.set(key, v)
        elif os.path.isdir(v):
            print 'set NatLinkUserDir to %s'% v
            self.userregnl.set(key, v)
        else:
            print 'no a valid directory: %s'% v
            
        
    def clearUserDirectory(self):
        key = 'UserDirectory'
        Keys = self.userregnl.keys()
        if key in Keys:
            print 'clearing NatLink user directory...'
            self.userregnl.delete(key)
        else:
            print 'NatLink user directory key was not set...'
            
    def alwaysIncludeUnimacroDirectoryInPath(self):
        """set variable so natlinkstatus knows to include Unimacro in path
        
        This is only used when userDirectory is set to another directory as Unimacro.
        Unimacro is expected at ../../Unimacro relative to the Core directory
        """
        key = 'IncludeUnimacroInPythonPath'
        Keys = self.userregnl.keys()
        print 'set %s'% key
        self.userregnl.set(key, 1)

    def ignoreUnimacroDirectoryInPathIfNotUserDirectory(self):
        """clear variable so natlinkstatus knows to not include Unimacro in path
        
        This is only used when userDirectory is set to
        another directory as Unimacro.
        Unimacro is expected at ../../Unimacro relative to the Core directory
        """
        key = 'IncludeUnimacroInPythonPath'
        Keys = self.userregnl.keys()

        if key in Keys:
            print 'clearing variable %s'% key
            self.userregnl.delete(key)
        else:
            print 'was not set %s'% key
        
      
    def enableNatlink(self, silent=None):
        """register natlink.pyd and set settings in nssystem.INI and nsapps.ini

        """
        self.registerNatlinkPyd(silent=1)
        nssystemini = self.getNSSYSTEMIni()
        section1 = self.section1
        key1 = self.key1
        value1 = self.value1
        try:
            win32api.WriteProfileVal(section1, key1, value1, nssystemini)
        except pywintypes.error, details:
            if details[0] == 5:
                print 'cannot enable NatLink (1), you probably need administrator rights'
            else:
                print 'unexpected error at enable NatLink (1)'
                raise
            
        result = self.NatlinkIsEnabled(silent=1)
        if result == None:
            nsappsini = self.getNSAPPSIni()
            section2 = self.section2
            key2 = self.key2
            value2 = self.value2
            try:
                win32api.WriteProfileVal(section2, key2, value2, nsappsini)
            except pywintypes.error, details:
                if details[0] == 5:
                    print 'cannot enable NatLink (2), you probably need administrator rights'
                else:
                    print 'unexpected error at enable NatLink (2)'
                    raise
            result = self.NatlinkIsEnabled(silent=1)
            if result == None:
                text = \
"""Cannot set the nsapps.ini setting in order to complete enableNatlink.

Probably you did not run this program in "elevated mode". Please try to do so.
"""
                self.warning(text)
                return                
        result = self.NatlinkIsEnabled(silent=1)
        if result:            
            if not silent:
                print 'NatLink enabled, restart %s'% self.DNSName
        else:
            if not silent:
                self.warning("failed to enable NatLink")
            

    def disableNatlink(self, silent=None):
        """only do the nssystem.ini setting
        """
        nssystemini = self.getNSSYSTEMIni()
        section1 = self.section1
        key1 = self.key1
        # trick with None, see testConfigureFunctions...
        # this one disables NatLink:
        try:
            win32api.WriteProfileVal(section1, key1, None, nssystemini)
        except pywintypes.error, details:
            if details[0] == 5:
                print 'cannot disable NatLink, you probably need administrator rights'
            else:
                print 'unexpected error at disable NatLink'
                raise
        result = self.NatlinkIsEnabled(silent=1)
        if result:            
            t = 'NatLink is NOT disabled, you probably need administrator rights, please restart the config program in "elevated mode"'
            print t
            self.warning(t)
        else:
            if not silent:
                print 'NatLink disabled, restart %s'% self.DNSName
                print 'Note natlink.pyd is NOT UNREGISTERED, but this is not necessary either'
        
    def getVocolaUserDir(self):
        key = 'VocolaUserDirectory'
        value = self.userregnl.get(key, None)
        return value

    def setVocolaUserDir(self, v):
        key = 'VocolaUserDirectory'
        if v.startswith("~") or v.find("%") >= 0:
            print "Setting Vocola user dir to %s"% v
            self.userregnl.set(key, v)
        elif os.path.isdir(v):
            print 'set Vocola user dir to %s'% v
            self.userregnl.set(key, v)
        else:
            print 'not a valid directory: %s'% v

    def clearVocolaUserDir(self):
        key = 'VocolaUserDirectory'
        self.userregnl.delete(key)

    ## autohotkey (January 2014)
    def getAhkExeDir(self):
        key = 'AhkExeDir'
        value = self.userregnl.get(key, None)
        return value

    def setAhkExeDir(self, v):
        key = 'AhkExeDir'
        if v.startswith("~") or v.find("%") >= 0:
            v = natlinkcorefunctions.expandEnvVariables(v)
            print "Setting AutoHotkey Exe expanded to %s"% v

        if os.path.isdir(v):
            exepath = os.path.join(v, 'autohotkey.exe')
            if os.path.isfile(exepath):
                print 'set AutoHotkey Exe dir to %s'% v
                self.userregnl.set(key, v)
            else:
                print 'path does not contain "autohotkey.exe"H: %s'% v
        else:
            print 'not a valid directory: %s'% v

    def clearAhkUserDir(self):
        key = 'AhkUserDir'
        self.userregnl.delete(key)

    def getAhkUserDir(self):
        key = 'AhkUserDir'
        value = self.userregnl.get(key, None)
        return value

    def setAhkUserDir(self, v):
        key = 'AhkUserDir'
        if v.startswith("~") or v.find("%") >= 0:
            print "Setting AutoHotkey User Directory to %s"% v
            self.userregnl.set(key, v)
        elif os.path.isdir(v):
            print 'set AutoHotkey User Directory to %s'% v
            self.userregnl.set(key, v)
        else:
            print 'not a valid directory: %s'% v

    def clearAhkExeDir(self):
        key = 'AhkExeDir'
        self.userregnl.delete(key)


    def getUnimacroUserDir(self):
        key = 'UnimacroUserDirectory'
        return self.userregnl.get(key, None)

    def setUnimacroUserDir(self, v):
        key = 'UnimacroUserDirectory'
        oldDir = self.getUnimacroUserDir() or self.getUserDirectory()
        if oldDir and os.path.isdir(oldDir):
            if os.path.normpath(v) != os.path.normpath(oldDir):
                print '\n-----------\nConsider copying inifile subdirectories (enx_inifiles or nld_inifiles)\n' \
                      'from old UnimacroUserDirectory (%s) to \n' \
                      'new UnimacroUserDirectory (%s)\n--------\n'% (oldDir, v)
            
        if os.path.isdir(v) or v.startswith("~") or v.find("%") >= 0:
            print 'set Unimacro user dir to %s'% v
            self.userregnl.set(key, v)
        else:
            print 'not a valid directory: %s'% v

    def clearUnimacroUserDir(self):
        key = 'UnimacroUserDirectory'
        self.userregnl.delete(key)

    def setUnimacroIniFilesEditor(self, v):
        key = "UnimacroIniFilesEditor"
        if v and os.path.isfile(v) and v.endswith(".exe"):
            self.userregnl.set(key, v)
        else:
            print 'invalid path, not a file or no .exe file: %s'% v
            
    def clearUnimacroIniFilesEditor(self):
        key = "UnimacroIniFilesEditor"
        self.userregnl.delete(key)
                
    def registerNatlinkPyd(self, silent=1):
        """register natlink.pyd

        if silent, do through win32api, and not report. This is done whenever NatLink is enabled.

        if NOT silent, go through os.system, and produce a message window.

        Also sets the pythonpath in the HKLM pythonpath section        
        """
        # give fatal error if Python is not OK...
        dummy, dummy = self.getHKLMPythonPathDict(flags=win32con.KEY_ALL_ACCESS)        
        pythonVersion = self.getPythonVersion()
        dragonVersion = self.getDNSVersion()
        if not (pythonVersion and len(pythonVersion) == 2):
            fatal_error('not a valid python version found: |%s|'% pythonVersion)
            
        # for safety unregister always:
        print 'first unregister, just to be sure...'
        self.unregisterNatlinkPyd(silent=1)    
            
        PydPath = os.path.join(coreDir, 'natlink.pyd')
        if not os.path.isfile(PydPath):
            fatal_error("Pyd file not found in core folder: %s"% PydPath)
    
        baseDir = os.path.join(coreDir, '..')
    
        newIniSetting = "%s;%s"% (pythonVersion, dragonVersion)
    
        if silent:
            try:
                import win32api
            except:
                fatal_error("cannot import win32api, please see if win32all of python is properly installed")
            
            try:

                result = win32api.WinExec('regsvr32 /s "%s"'% PydPath)
                if result:
                    fatal_error('failed to register %s (result: %s)\nPossibly exit Dragon and run this program in Elevated (admin) mode'% (PydPath, result))
                    self.config.set('NatlinkPydRegistered', 0)
                    return
                else:
                    self.userregnl.set('NatlinkPydRegistered', newIniSetting)
                    print 'Registring pyd file succesful: %s'% PydPath

    #                    print 'registered %s '% PydPath
                    
            except:
                self.userregnl.set('NatlinkPydRegistered', 0)
                fatal_error("cannot register |%s|"% PydPath)
                return
        else:
            # os.system:
            result = os.system('regsvr32 "%s"'% PydPath)
            if result:
                print 'failed to register %s (result: %s)'% (PydPath, result)
                self.userregnl.set('NatlinkPydRegistered', 0)
                return
            else:
                self.userregnl.set('NatlinkPydRegistered', newIniSetting)
                print 'Registring pyd file succesful: %s'% PydPath
                
        self.setNatlinkInPythonPathRegistry()

    def unregisterNatlinkPyd(self, silent=1):
        """unregister explicit, should not be done normally
        """
        dummy, dummy = self.getHKLMPythonPathDict(flags=win32con.KEY_ALL_ACCESS)        
        pythonVersion = self.getPythonVersion()
        if int(pythonVersion) >= 25:
            PydPath = os.path.join(coreDir, 'natlink.pyd')
        else:
            PydPath = os.path.join(coreDir, 'natlink.pyd')
        if not os.path.isfile(PydPath):
            return

        if silent:
            try:
                import win32api
            except:
                fatal_error("cannot import win32api, please see if win32all of Python is properly installed")
            
            try:
                result = win32api.WinExec('regsvr32 /s /u "%s"'% PydPath)
                if not result:
                    pass
                else:
                    #print 'failed to unregister %s, result %s'% (PydPath, result)
                    self.userregnl.set('NatlinkPydRegistered', 0)
            except:
                pass
        else:
            # os.system:
            os.system('regsvr32 /u "%s"'% PydPath)
            self.userregnl.set('NatlinkPydRegistered', 0)

        #self.clearNatlinkFromPythonPathRegistry()
        # and remove the natlink.pyd (there remain pythonversion ones 23, 24 and 25)
        #os.remove(PydPath)
        
    def enableDebugLoadOutput(self):
        """setting registry key so debug output of loading of natlinkmain is given

        """
        key = "NatlinkmainDebugLoad"
        self.userregnl.set(key, 1)
        

    def disableDebugLoadOutput(self):
        """disables the NatLink debug output of loading of natlinkmain is given
        """
        key = "NatlinkmainDebugLoad"
        self.userregnl.delete(key)

    def enableDebugCallbackOutput(self):
        """setting registry key so debug output of callback functions of natlinkmain is given

        """
        key = "NatlinkmainDebugCallback"
        self.userregnl.set(key, 1)
        

    def disableDebugCallbackOutput(self):
        """disables the NatLink debug output of callback functions of natlinkmain
        """
        key = "NatlinkmainDebugCallback"
        self.userregnl.delete(key)
        
    def enableDebugOutput(self):
        """setting registry key so debug output is in NatSpeak logfile

        not included in configure GUI, as NatSpeak/natlink.pyd seems not to respond
        to this option...
        """
        key = "NatlinkDebug"
        self.userregnl.set(key, 1)
        # double in registry, natlink.pyd takes this one:
        print 'Enable NatlinkDebug, this setting is obsolete)'% key
        #self.userregnlOld[key] = 1

    def disableDebugOutput(self):
        """disables the NatLink lengthy debug output to NatSpeak logfile
        """
        key = "NatlinkDebug"
        self.userregnl.delete(key)
        # double in registry, natlink.pyd takes this one:
        print 'Disable NatlinkDebug, this setting is obsolete'% key
        #self.userregnlOld[key] = 0

    def copyUnimacroIncludeFile(self):
        """copy Unimacro include file into Vocola user directory

        """
        uscFile = 'Unimacro.vch'
        oldUscFile = 'usc.vch'
        # also remove usc.vch from VocolaUserDirectory
        fromFolder = os.path.normpath(os.path.join(thisDir, '..', '..',
                                                   'Unimacro',
                                                   'Vocola_compatibility'))
        toFolder = self.getVocolaUserDir()
        if os.path.isdir(fromFolder):
            fromFile = os.path.join(fromFolder,uscFile)
            if os.path.isfile(fromFile):
                if os.path.isdir(toFolder):
                    
                    toFile = os.path.join(toFolder, uscFile)
                    if os.path.isfile(toFile):
                        print 'remove previous %s'% toFile
                        try:
                            os.remove(toFile)
                        except:
                            pass
                    print 'copy %s from %s to %s'%(uscFile, fromFolder, toFolder)
                    try:
                        shutil.copyfile(fromFile, toFile)
                    except:
                        pass
                    else:
                        oldUscFile = os.path.join(toFolder, oldUscFile)
                        if os.path.isfile(oldUscFile):
                            print 'remove old usc.vcl file: %s'% oldUscFile
                            os.remove(oldUscFile)
                        return
        mess = "could not copy file %s from %s to %s"%(uscFile, fromFolder, toFolder)
        print mess
        return mess
        

    def includeUnimacroVchLineInVocolaFiles(self, subDirectory=None):
        """include the Unimacro wrapper support line into all Vocola command files
        
        as a side effect, set the variable for Unimacro in Vocola support:
        VocolaTakesUnimacroActions...
        """
        uscFile = 'Unimacro.vch'
        oldUscFile = 'usc.vch'
##        reInclude = re.compile(r'^include\s+.*unimacro.vch;$', re.MULTILINE)
##        reOldInclude = re.compile(r'^include\s+.*usc.vch;$', re.MULTILINE)
        
        # also remove includes of usc.vch
        toFolder = self.getVocolaUserDir()
        if subDirectory:
            toFolder = os.path.join(toFolder, subDirectory)
            includeLine = 'include ..\\%s;\n'% uscFile
        else:
            includeLine = 'include %s;\n'%uscFile
        oldIncludeLines = ['include %s;'% oldUscFile,
                           'include ..\\%s;'% oldUscFile,
                           'include %s;'% uscFile.lower(),
                           'include ..\\%s;'% uscFile.lower(),
                           ]
            
        if not os.path.isdir(toFolder):
            mess = 'cannot find Vocola command files directory, not a valid path: %s'% toFolder
            print mess
            return mess
        nFiles = 0
        for f in os.listdir(toFolder):
            F = os.path.join(toFolder, f)
            if f.endswith(".vcl"):
                changed = 0
                correct = 0
                Output = []
                for line in open(F, 'r'):
                    if line.strip() == includeLine.strip():
                        correct = 1
                    for oldLine in oldIncludeLines:
                        if line.strip() == oldLine:
                            changed = 1
                            break
                    else:
                        Output.append(line)
                if changed or not correct:
                    # changes were made:
                    if not correct:
                        Output.insert(0, includeLine)
                    open(F, 'w').write(''.join(Output))
                    nFiles += 1
            elif len(f) == 3 and os.path.isdir(F):
                # subdirectory, recursive
                self.includeUnimacroVchLineInVocolaFiles(F)
        self.enableVocolaTakesUnimacroActions()
        mess = 'changed %s files in %s, and set the variable "%s"'% (nFiles, toFolder,
                                                                     "VocolaTakesUnimacroActions")
        
        print mess

    def removeUnimacroVchLineInVocolaFiles(self, subDirectory=None):
        """remove the Unimacro wrapper support line into all Vocola command files
        """
        uscFile = 'Unimacro.vch'
        oldUscFile = 'usc.vch'
##        reInclude = re.compile(r'^include\s+.*unimacro.vch;$', re.MULTILINE)
##        reOldInclude = re.compile(r'^include\s+.*usc.vch;$', re.MULTILINE)
        
        # also remove includes of usc.vch
        if subDirectory:
            # for recursive call language subfolders:
            toFolder = subDirectory
        else:
            toFolder = self.getVocolaUserDir()
            
        oldIncludeLines = ['include %s;'% oldUscFile,
                           'include ..\\%s;'% oldUscFile,
                           'include %s;'% uscFile,
                           'include ..\\%s;'% uscFile,
                           'include ../%s;'% oldUscFile,
                           'include ../%s;'% uscFile,
                           'include %s;'% uscFile.lower(),
                           'include ..\\%s;'% uscFile.lower(),
                           'include ../%s;'% uscFile.lower(),
                           ]

            
        if not os.path.isdir(toFolder):
            mess = 'cannot find Vocola command files directory, not a valid path: %s'% toFolder
            print mess
            return mess
        nFiles = 0
        for f in os.listdir(toFolder):
            F = os.path.join(toFolder, f)
            if f.endswith(".vcl"):
                changed = 0
                Output = []
                for line in open(F, 'r'):
                    for oldLine in oldIncludeLines:
                        if line.strip() == oldLine:
                            changed = 1
                            break
                    else:
                        Output.append(line)
                if changed:
                    # had break, so changes were made:
                    open(F, 'w').write(''.join(Output))
                    nFiles += 1
            elif len(f) == 3 and os.path.isdir(F):
                self.removeUnimacroVchLineInVocolaFiles(F)
        mess = 'removed include lines from %s files in %s'% (nFiles, toFolder)
        print mess


    def enableVocolaTakesLanguages(self):
        """setting registry  so Vocola can divide different languages

        """
        key = "VocolaTakesLanguages"
        self.userregnl.set(key, 1)
        

    def disableVocolaTakesLanguages(self):
        """disables so Vocola cannot take different languages
        """
        key = "VocolaTakesLanguages"
        self.userregnl.set(key, 0)

    def enableVocolaTakesUnimacroActions(self):
        """setting registry  so Vocola can divide different languages

        """
        key = "VocolaTakesUnimacroActions"
        self.userregnl.set(key, 1)
        

    def disableVocolaTakesUnimacroActions(self):
        """disables so Vocola does not take Unimacro Actions
        """
        key = "VocolaTakesUnimacroActions"
        self.userregnl.set(key, 0)
        
                



def _main(Options=None):
    """Catch the options and perform the resulting command line functions

    options: -i, --info: give status info

             -I, --reginfo: give the info in the registry about NatLink
             etc., usage above...

    """
    cli = CLI()
    shortOptions = "aAiIeEfFgGyYxXDCVbBNOPlmMrRzZuq"
    shortArgOptions = "d:c:v:n:o:p:"
    if Options:
        if type(Options) == types.StringType:
            Options = Options.split(" ", 1)
        Options = map(string.strip, Options)                
    else:
        Options = sys.argv[1:]

    try:
        options, args = getopt.getopt(Options, shortOptions+shortArgOptions)
    except getopt.GetoptError:
        print 'invalid option: %s'% `Options`
        cli.usage()
        return

    if args:
        print 'should not have extraneous arguments: %s'% `args`
    for o, v in options:
        o = o.lstrip('-')
        funcName = 'do_%s'% o
        func = getattr(cli, funcName, None)
        if not func:
            print 'option %s not found in cli functions: %s'% (o, funcName)
            cli.usage()
            continue
        if o in shortOptions:
            func(None) # dummy arg
        elif o in shortArgOptions:
            func(v)
        else:
            print 'options should not come here'
            cli.usage()


          
class CLI(cmd.Cmd):
    """provide interactive shell control for the different options.
    """
    def __init__(self, Config=None):
        cmd.Cmd.__init__(self)
        self.prompt = '\nNatLink/Vocola/Unimacro config> '
        self.info = "type 'u' for usage"
        if Config:
            self.config = Config   # initialized instance of NatlinkConfig
        else:
            self.config = NatlinkConfig()
        self.config.checkCoreDirectory()
        self.config.correctIniSettings()
        if self.config.configCheckNatlinkPydFile() is None:
            if __name__ == "__main__":
                print "Error starting NatlinkConfig, Type 'u' for a usage message"

            self.checkedConfig = self.config.checkedUrgent
            return

        self.config.checkPythonPathAndRegistry()
        self.config.checkIniFiles()
        self.checkedConfig = self.config.checkedUrgent
        for key in ObsoleteStatusKeys:
            # see at top of this file!
            if key in self.config.userregnl.keys():
                self.config.userregnl.delete(key)
        self.DNSName = self.config.getDNSName()
        if __name__ == "__main__":
            print "Type 'u' for a usage message"

    def getFatalErrors(self):
        """get the fatal errors from this module and clear them automatically
        """
        global hadFatalErrors
        if hadFatalErrors:
            text = '\n'.join(hadFatalErrors)
            hadFatalErrors = []
            return text

    def usage(self):
        """gives the usage of the command line options or options when
        the command line interface  (CLI) is used
        """
        print '-'*60
        print \
"""Use either from the command line like 'natlinkconfigfunctions.py -i'
or in an interactive session using the CLI (command line interface). 

[Status]

i       - info, print information about the NatLink status
I       - settings, print information about the natlinkstatus.ini settings
j       - print PythonPath variable

[NatLink]

e/E     - enable/disable NatLink

g/G     - enable/disable debug output, which is sent to the NatSpeak/Dragon log file
y/Y     - enable/disable debug callback output of natlinkmain 
x/X     - enable/disable debug load output     of natlinkmain

d/D     - set/clear DNSInstallDir, the directory where NatSpeak/Dragon is installed
c/C     - set/clear DNSINIDir, where NatSpeak/Dragon INI files are located

[Vocola]

v/V     - enable/disable Vocola by setting/clearing VocolaUserDir, the user
          directory for Vocola user files (~ or %HOME% allowed).

b/B     - enable/disable distinction between languages for Vocola user files
a/A     - enable/disable the possibility to use Unimacro actions in Vocola

[Unimacro]

n/N     - enable/disable Unimacro by setting/clearing UserDirectory, the
          directory where user NatLink grammar files are located (e.g.,
          ...\My Documents\NatLink)
f/F     - force Unimacro directory to be in the python path, even if
          the userDirectory is set to another path (-F: do not force this)
o/O     - set/clear UnimacroUserDir, where Unimacro user INI files are located
          (~ or %HOME% allowed)
p/P     - set/clear path for program that opens Unimacro INI files.
l       - copy header file Unimacro.vch into Vocola User Directory
m/M     - insert/remove an include line for Unimacro.vch in all Vocola
          command files

[Repair]
r/R     - register/unregister NatLink, the natlink.pyd (natlink.pyd) file
          (should not be needed)
z/Z     - silently enables NatLink and registers natlink.pyd / disables NatLink
          and unregisters natlink.pyd.
[AutoHotkey]
h/H     - set/clear the AutoHotkey exe directory.
k/K     - set/clear the User Directory for AutoHotkey scripts.
[Other]

u/usage - give this list
q       - quit

help <command>: give more explanation on <command>
        """
        print '='*60

    # info----------------------------------------------------------
    def do_i(self, arg):
        S = self.config.getNatlinkStatusString()
        S = S + '\n\nIf you changed things, you must restart %s'% self.DNSName
        print S
    def do_I(self, arg):
        # inifile natlinkstatus.ini settings:
        self.config.printInifileSettings()
    def do_j(self, arg):
        # print PythonPath:
        self.config.printPythonPath()

    def help_i(self):
        print '-'*60
        print \
"""The command info (i) gives an overview of the settings that are
currently set inside the NatLink system.

The command settings (I) gives all the NatLink settings, kept in
natlinkstatus.ini (overlap with (i))

The command (j) gives the PythonPath variable which should contain several
NatLink directories after the config GUI runs succesfully

Settings are set by either the NatLink/Vocola/Unimacro installer
or by functions that are called by the CLI (command line interface).

After you change settings, restart %s.
"""% self.DNSName
        print '='*60
    help_j = help_I = help_i

    # DNS install directory------------------------------------------
    def do_d(self, arg):
        if not arg:
            print 'also enter a valid folder'
            return
        arg = arg.strip()
        if os.path.isdir(arg):
##            if arg.find(' ') > 0:
##                arg = '"' + arg + '"'
            print "Change %s directory to: %s"% (self.DNSName, arg)
            return self.config.setDNSInstallDir(arg)
        else:
            print 'not a valid folder: %s'% arg
    

    def do_D(self, arg):
        print "Clear NatSpeak directory in registry"
        return self.config.clearDNSInstallDir()

    def help_d(self):
        print '-'*60
        print \
"""Set (d <path>) or clear (D) the directory where %s is installed.

Setting is only needed when %s is not found at one of the "normal" places.
So setting is often not needed.

When you have a pre-8 version of NatSpeak, setting this option might work.

After you clear this setting, NatLink will, at starting time, again
search for the %s install directory in the "normal" place(s).
"""% (self.DNSName, self.DNSName, self.DNSName)
        print '='*60
    help_D = help_d

    # DNS INI directory-----------------------------------------
    def do_c(self, arg):
        if not arg:
            print 'also enter a valid folder'
            return
        arg = arg.strip()
        if os.path.isdir(arg):
##            if arg.find(' ') > 0:
##                arg = '"' + arg + '"'
            print "Change %s INI files directory to: %s"% (self.DNSName, arg)
            return self.config.setDNSIniDir(arg)
        else:
            print 'not a valid folder: %s'% arg
    


    def do_C(self, arg):
            print "Clear %s INI files directory in registry"% self.DNSName
            return self.config.clearDNSIniDir()
    def help_c(self):
        print '-'*60
        print \
"""Set (c <path>) or clear (C) the directory where %s INI file locations
(nssystem.ini and nsapps.ini) are located.

Only needed if these cannot be found in the normal place(s):
-if you have an "alternative" place where you keep your speech profiles
-if you have a pre-8 version of NatSpeak.

After Clearing this registry entry NatLink will, when it is started by %s,
again search for its INI files in the "default/normal" place(s).
"""% (self.DNSName, self.DNSName)
        print '='*60
    help_C = help_c
    
    # User Directories -------------------------------------------------
    def do_n(self, arg):
        if not arg:
            print 'also enter a valid folder'
            return
        arg = arg.strip()
        self.config.setUserDirectory(arg)
    
    def do_N(self, arg):
        print "Clears NatLink User Directory"
        self.config.clearUserDirectory()
    def do_f(self, arg):
        print "Use Unimacro directory in PythonPath even if userDirectory is different"
        self.config.alwaysIncludeUnimacroDirectoryInPath()
    def do_F(self, arg):
        print "Do NOT use Unimacro directory in PythonPath even if userDirectory is different from it."
        self.config.ignoreUnimacroDirectoryInPathIfNotUserDirectory()
    
    def help_n(self):
        print '-'*60
        print \
"""Sets (n <path>) or clears (N) the user directory of NatLink.
This will often be the folder where Unimacro is located.

If you use a non-Unimacro directory for userDirectory
you can use the "f" option for including the Unimacro directory
to the PythonPath. So modules from Unimacro can be called.
The Unimacro directory is expected ../../Unimacro in relation to the
core directory.

When you clear this registry entry, you probably disable Unimacro, as
Unimacro is located in the NatLink user directory.

Vocola will still be on, BUT without the possibility to use
Unimacro shorthand commands and meta actions.
"""
        print '='*60
        
    help_N = help_n
    help_f = help_n
    help_F = help_n
    
    # Unimacro User directory and Editor for Unimacro INI files-----------------------------------
    def do_o(self, arg):
        self.config.setUnimacroUserDir(arg)
            
    def do_O(self, arg):
        print "Clearing Unimacro user directory, falling back to default: %s"% self.config.getUserDirectory()
        self.config.clearUnimacroUserDir()

    def help_o(self):
        print '-'*60
        userDir = self.config.getUserDirectory()
        print \
"""set/clear Unimacro user directory (o <path>/O)

If you specify this directory, your user INI files (and possibly other user
dependent files) will be put there.

You can use (if entered through the CLI) "~" (or %%HOME%%) for user home directory, or
another environment variable (%%...%%). (example: "o ~\NatLink\Unimacro")

If you clear this setting, the user INI files will be put in the
Unimacro directory itself: %s

"""% userDir
        print '='*60

    help_O = help_o

    # Unimacro Command Files Editor-----------------------------------------------
    def do_p(self, arg):
        if os.path.isfile(arg) and arg.endswith(".exe"):
            print "Setting (path to) Unimacro INI Files editor to %s"% arg
            self.config.setUnimacroIniFilesEditor(arg)
        else:
            print 'Please specify a valid path for the Unimacro INI files editor, not |%s|'% arg
            
    def do_P(self, arg):
        print "Clear Unimacro INI file editor, go back to default Notepad"
        self.config.clearUnimacroIniFilesEditor()

    def help_p(self):
        print '-'*60
        print \
"""set/clear path to Unimacro INI files editor (p <path>/P)

By default (when you clear this setting) "notepad" is used, but:

You can specify a program you like, for example,
TextPad, NotePad++, UltraEdit, or win32pad

You can even specify Wordpad, maybe Microsoft Word...

"""
        print '='*60

    help_P = help_p

    # Unimacro Vocola features-----------------------------------------------
    # managing the include file wrapper business.
    # can be called from the Vocola compatibility button in the config GUI.
    def do_l(self, arg):
        print "Copy include file Unimacro.vch into Vocola User Directory"
        self.config.copyUnimacroIncludeFile()

    def help_l(self):
        print '-'*60
        print \
"""Copy Unimacro.vch header file into Vocola User Files directory      (l)

Insert/remove 'include Unimacro.vch' lines into/from each Vocola 
command file                                                        (m/M)

Using Unimacro.vch, you can call Unimacro shorthand commands from a
Vocola command.
"""
        print '='*60

    def do_m(self, arg):
        print 'Insert "include Unimacro.vch" line in each Vocola Command File'
        self.config.includeUnimacroVchLineInVocolaFiles()
    def do_M(self, arg):
        print 'Remove "include Unimacro.vch" line from each Vocola Command File'
        self.config.removeUnimacroVchLineInVocolaFiles()
    help_m = help_M = help_l

        
    # enable/disable NatLink------------------------------------------------
    def do_e(self, arg):
        print "Enabling NatLink:"
        self.config.enableNatlink()
    def do_E(self, arg):
        print "Disabling NatLink:"
        self.config.disableNatlink()

    def help_e(self):
        print '-'*60
        print \
"""Enable NatLink (e) or disable NatLink (E):

When you enable NatLink, the necessary settings in nssystem.ini and nsapps.ini
are done.

After you restart %s, NatLink should start, opening a window entitled
'Messages from Python Macros'.

When you enable NatLink, the file natlink.pyd is (re)registered silently.  Use
the commands r/R to register/unregister natlink.pyd explicitly.
(see help r, but most often not needed)

When you disable NatLink, the necessary settings in nssystem.ini and nsapps.ini
are cleared. 
i
After you restart %s, NatLink should NOT START ANY MORE
so the window 'Messages from Python Macros' is NOT OPENED.

Note: when you disable NatLink, the natlink.pyd file is NOT unregistered.
It is not called any more by %s, as its declaration is removed from
the Global Clients section of nssystem.ini.
"""% (self.DNSName, self.DNSName, self.DNSName)
        print "="*60
        
        
    help_E = help_e
  
    
    # Vocola and Vocola User directory------------------------------------------------
    def do_v(self, arg):
        self.config.setVocolaUserDir(arg)
            
    def do_V(self, arg):
        print "Clearing Vocola user directory and (therefore) disabling Vocola:"
        self.config.clearVocolaUserDir()

    def help_v(self):
        print '-'*60
        print \
"""Enable/disable Vocola by setting/clearing the Vocola user directory
(v <path>/V).

Vocola is meant to be used with a Vocola user directory.  Therefore
natlinkmain will not enable Vocola if no Vocola user directory is set.

<path> must be an existing folder; NatLink\Vocola in My Documents is a
popular choice.  Thus, Sally under Windows XP might use:

  v C:\Documents and Settings\Sally\My Documents\NatLink\Vocola
  
You can also use (if entered through the CLI) "~" (or %HOME%) for user home directory, or
another %...% environment variable.
(so "v ~\NatLink\Vocola" or "v %HOME%\NatLink\Vocola" in above example)


You may have to manually create this folder first.
"""
        print '='*60

    help_V = help_v

    # Vocola Command Files Editor-----------------------------------------------
##    def do_w(self, arg):
##        if os.path.isfile(arg) and arg.endswith(".exe"):
##            print "Setting Setting Vocola Command Files editor to %s"% arg
##            self.config.setVocolaCommandFilesEditor(arg)
##        else:
##            print 'Please specify a valid path for Vocola command files editor: |%s|'% arg
##            
##    def do_W(self, arg):
##        print "Clear Vocola commands file editor, go back to default notepad"
##        self.config.clearVocolaCommandFilesEditor()
##
##    def help_w(self):
##        print '-'*60
##        print \
##"""set/clear Vocola  command files editor (w path/W)
##
##By default the editor "notepad" is used.
##
##You can specify a program you like, for example,
##TextPad, NotePad++, UltraEdit, or win32pad.
##
##"""
##    
##        print '='*60
##
##    help_W = help_w
    

    # enable/disable NatLink debug output...
    def do_g(self, arg):
        print "Enable NatLink debug output to %s logfile "% self.DNSName
        self.config.enableDebugOutput()
    def do_G(self, arg):
        print "Disable NatLink debug output to %s logfile"% self.DNSName
        self.config.disableDebugOutput()

    def help_g(self):
        print '-'*60
        print \
"""Enables (g)/disables (G) NatLink debug output (in the NatSpeak log file)
this can be a lot of lines, so preferably disable this one!

Currently it is not clear if this option does anything at all!
But the simplest thing is to keep it Disabled, so the setting
NatlinkDebug is kept to 0
"""
        print '='*60

    help_G = help_g
    # enable/disable NatLink debug output...
    def do_x(self, arg):
        print "Enable natlinkmain debug load output to messages of Python macros window"
        self.config.enableDebugLoadOutput()
    def do_X(self, arg):
        print "Disable natlinkmain debug load output to messages of Python macros window"
        self.config.disableDebugLoadOutput()
    # enable/disable NatLink debug output...
    def do_y(self, arg):
        print "Enable natlinkmain debug Callback output to messages of Python macros window"
        self.config.enableDebugCallbackOutput()
    def do_Y(self, arg):
        print "Disable natlinkmain debug Callback output to messages of Python macros window"
        self.config.disableDebugCallbackOutput()



    def help_x(self):
        print '-'*60
        print \
"""Enable (x)/disable (X) natlinkmain debug load output

Enable (y)/disable (Y) natlinkmain debug callback output

This sends sometimes lengthy debugging messages to the
"Messages from Python Macros" window.

Mainly used when you suspect problems with the working 
of NatLink, so keep off (X and Y) most of the time.
"""
        print '='*60

    help_y = help_x
    help_X = help_x
    help_Y = help_x
    
    # register natlink.pyd
    def do_r(self, arg):
        print "(Re) register and enable natlink.pyd"
        isRegistered = self.config.userregnl.get("NatlinkPydRegistered")
        #if isRegistered:
        #    print "If you have problems re-registering natlink.pyd, please try the following:"
        #    print "Un-register natlink.pyd first, then"
        #    print "If you want to try a new natlink.pyd, first exit this program,"
        #    print "Remove %s\\natlink.pyd"% coreDir
        #    print "and restart (in elevated mode) this program."
        #    print "The correct python version of natlink.pyd will be copied to natlink.pyd"
        #    print "and it will be registered again."
        #    return
        if not self.config.removeNatlinkPyd():
            return
        self.config.configCheckNatlinkPydFile()

        self.config.enableNatlink()
        
        #
        #
        #self.config.registerNatlinkPyd(silent=None)

    def do_R(self, arg):
        print "Unregister natlink.pyd and disable NatLink"
        self.config.disableNatlink(silent=1)
        self.config.unregisterNatlinkPyd(silent=None)
        
    def do_z(self, arg):
        """register silent and enable NatLink"""
        if not self.config.removeNatlinkPyd():
            return
        self.config.configCheckNatlinkPydFile()
        self.config.enableNatlink()
        
    def do_Z(self, arg):
        """(SILENT) Unregister natlink.pyd and disable NatLink"""
        self.config.disableNatlink(silent=1)
        self.config.unregisterNatlinkPyd(silent=1)

    def help_r(self):
        print '-'*60
        print \
"""Registers (r) / unregisters (R) natlink.pyd explicitly.

(Registering is also done (silently) when you start this program or the
configuration GUI, so is mostly NOT NEEDED!)

But if you do (-r or -R) a message dialog shows up to inform you what happened.
When you unregister, NatLink is also disabled.

When you want to try a new version of natlink.pyd, take the following steps:
-exit NaturallySpeaking
-unregister natlink.pyd (in elevated mode)
-remove natlink.pyd (in the MacroSystem/core directory of NatLink)
-rerun this program or the configure program in elevated mode.

The correct version of natlink.pyd (corresponding with your python version 2.6, 2.7 (2.5 for pre Dragon 12)
will be copied to this name and registered.

-finally Enable NatLink again.

If you want to (silently) enable NatLink and register silently use -z,
To disable NatLink and unregister (silently) use Z
"""
        print '='*60
    help_R = help_r
    help_z = help_r
    help_Z = help_r
    

    # different Vocola options
    def do_b(self, arg):
        print "Enable Vocola different user directory's for different languages"
        self.config.enableVocolaTakesLanguages()
    def do_B(self, arg):
        print "Disable Vocola different user directory's for different languages"
        self.config.disableVocolaTakesLanguages()

    def do_a(self, arg):
        print "Enable Vocola taking Unimacro actions"
        self.config.enableVocolaTakesUnimacroActions()
    def do_A(self, arg):
        print "Disable Vocola taking Unimacro actions"
        self.config.disableVocolaTakesUnimacroActions()

    def help_a(self):
        print '-'*60
        print \
"""----Enable (a)/disable (A) Vocola taking Unimacro actions.
        
These actions (Unimacro Shorthand Commands) and "meta actions" are processed by
the Unimacro actions module.

If Unimacro is NOT enabled, or a directory
different from the Unimacro directory is used as "UserDirectory", it will also
be necessary that the (original) Unimacro directory is put in the python path.
The special option for that is (f) (But often not needed).
"""
        print '='*60
        
    def help_b(self):
        print '-'*60
        print \
"""----Enable (b)/disable (B) different Vocola user directories

If enabled, Vocola will look into a subdirectory "xxx" of
VocolaUserDirectory IF the language code of the current user speech
profile is xxx and different from "enx".

So for English users this option will have no effect.

The first time a command file is opened in, for example, a
Dutch speech profile (language code "nld"), a subdirectory "nld" 
is made and all existing Vocola user files are copied into this folder.
"""
        print '='*60

    help_B = help_b
    help_A = help_a

    # autohotkey settings:
    def do_h(self, arg):
        print 'set directory of AutoHotkey.exe to: %s'% arg
        self.config.setAhkExeDir(arg)

    def do_H(self, arg):
        print 'clear directory of AutoHotkey.exe, return to default'
        self.config.clearAhkExeDir()

    def do_k(self, arg):
        print 'set user directory for AutoHotkey scripts to: %s'% arg
        self.config.setAhkUserDir(arg)

    def do_K(self, arg):
        print 'clear user directory of AutoHotkey scripts, return to default'
        self.config.clearAhkUserDir()
            
    def help_h(self):
        print '-'*60
        print \
"""----Set (h)/clear (return to default) (H) the AutoHotkey exe directory.
       Assume autohotkey.exe is found there (if not AutoHotkey support will not be there)
       If set to a invalid directory, AutoHotkey support will be switched off.
       
       Set (k)/clear (return to default) (K) the User Directory for AutoHotkey scripts.
"""
        print '='*60

    help_H = help_k = help_K = help_h

    # enable/disable NatLink debug output...

    def default(self, line):
        print 'no valid entry: %s, type u or usage for list of commands'% line
        print

    def do_quit(self, arg):
        sys.exit()
    do_q = do_quit
    def do_usage(self, arg):
        self.usage()
    do_u = do_usage
    def help_u(self):
        print '-'*60
        print \
"""u and usage give the list of commands
lowercase commands usually set/enable something
uppercase commands usually clear/disable something
Informational commands: i and I
"""
    help_usage = help_u
    
    
        
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
      cli = CLI()
      cli.info = "type u for usage"
      try:
          cli.cmdloop()
      except (KeyboardInterrupt, SystemExit):
          pass
    else:
      _main()

