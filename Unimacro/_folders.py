__version__ = "$Rev: 529 $ on $Date: 2014-01-09 13:51:39 +0100 (do, 09 jan 2014) $ by $Author: quintijn $"
# This file is part of a SourceForge project called "unimacro" see
# http://unimacro.SourceForge.net and http://qh.antenna.nl/unimacro
# (c) copyright 2003 see http://qh.antenna.nl/unimacro/aboutunimacro.html
#    or the file COPYRIGHT.txt in the natlink\natlink directory 
#
#  grammar: _folders.py
# Written by: Quintijn Hoogenboom (QH softwaretraining & advies)
# starting 2003, revised QH march 2011
#
"""with this grammar, you can reach folders, files and websites from any window.
From some windows (myu computer and most dialog windows) the folders and files
can be called directly by name if they are in the foreground.

If you are in a child window (often a file dialog window) the specified
folder is put into the filename text box, if you are in the Windows
Explorer or in the Internet Explorer file or drive is put in the
address text box, and otherwise a new window is opened with the
specified folder.

This grammar now makes use of ini files, to show and edit the contents
of the lists used.

Several "meta actions" are used, eg <<filenameenter>> and <<filename
exit>> when entering were exiting the file name text box in a file
dialog. These actions can be tailored for specific programs, like
some office programmes to behave different, or for WinZip. See examples
in actions.ini (call with "Edit Actions"/"Bewerk acties")

In the inifile also the commands for start this computer or start
windows explorer must be given. Correct these commands ("Edit
Folders"/"Bewerk folders") if they do not work correct.
New feature: if you want to use xxexplorer (can be used hands-free very
easy, look in http://www.netez.com/xxExplorer), in section [general]
you can put a variable

xxexplorer = path to exe or false ('')

This explorer is then taken if you are in or if Explorer is explicitly asked for.

The strategy for "New" and "Explorer" (when you say "new", "nieuw",
"explorer" in the folder command, are complicated, look below

The site part is only used if you enter a valid folder in siteRoot below.
With this command you can quickly enter a complicated set of there we go agains.

The subversion additional commands are only valid if you specify a valid subversion
client in the ini file general section.

"""            
import string, types, re, copy
import natlink
import os, sys, time, fnmatch
import win32gui, win32con
from win32com.client import Dispatch
import inivars  # for IniError
import messagefunctions as mess
#, win32com
import natlinkcorefunctions # getExtendedEnv
from actions import doAction as action
from actions import doKeystroke as keystroke
from utilsqh import *
from actions import do_YESNO as YesNo
import webbrowser
natut = __import__('natlinkutils')
natqh = __import__('natlinkutilsqh')
natbj = __import__('natlinkutilsbj')

# for substituting environment variable like %HOME% in a file path:
# and %DESKTOP% in a file path.
# %HOME% defaults to your my documents folder, but can be in the system environment variables.
reEnv = re.compile('%([A-Z_]+)%')
reOnlyLowerCase = re.compile(r'^[a-z]+$')
reLettersSpace = re.compile(r'^[a-zA-Z ]+$')
###########################################################

# classes for this computer and windows explorer:
Classes = ('ExploreWClass', 'CabinetWClass')

# extra for sites (QH)
siteRoot = 'D:\\projects\\sitegen'
if siteRoot and not os.path.isdir(siteRoot) :
##    print "grammar _folder: site commands skipped"
    siteRoot = ""
else:
    if not siteRoot in sys.path:
        #print 'append to sys.path: %s'% siteRoot
        sys.path.append(siteRoot)

# some child windows have to behave as top window (specified in ini file):
# note: title is converted to lowercase, only full title is recognised

ancestor = natbj.IniGrammar
class ThisGrammar(ancestor):
    """grammar for quickly going to folders, files and websites
    """    

    language = natqh.getLanguage()
    name = "folders"
    iniIgnoreGrammarLists = ['subfolders', 'subfiles'] # on the fly in CabinetWClass
    
    # commands with special status, must correspond to a right hand side
    # of a ini file entry (section foldercommands or filecommands)
    # remote, subversion, openwith have hardcoded details.
    optionalfoldercommands = ['new', 'explorer', 'paste', 'copy', 'remote', 'subversion']
    optionalfilecommands = ['copy', 'paste', 'edit', 'paste', 'remote', 'subversion', 'openwith']

    # only used if siteRoot is a valid folder:
    optionalsitecommands = ['input', 'output', 'local', 'online']
    
    gramSpec = """
<folder> exported = folder ({folders}|{subfolders}|{folders}<foldercommands>|{subfolders}<foldercommands>);
<disc> exported = drive ({letters} | {letters} <foldercommands>);  # add + later again
<thisfolder> exported = this folder <foldercommands>;
<foldercommands> = {foldercommands}| on {letters} |
                    (subversion) {subversionfoldercommands};
                   
<folderup> exported = folder up|folder up {n1-10};
<file> exported = file ({files}|{subfiles}|{files}<filecommands>|{subfiles}<filecommands>);  # add dot {extensions} later again
<thisfile> exported = this file  <filecommands>; 
<filecommands> = {filecommands}| (on {letters}) |
                ('open with') {fileopenprograms}|
                (subversion) {subversionfilecommands};
<website> exported = website ({websites} | {websites} <websitecommands>);
<thiswebsite> exported = (this website) <websitecommands>;
<websitecommands> = ('open with') {websiteopenprograms};

## set all environment variables into the folders list...
<setenvironmentfolders> exported =  set environment folders;
"""
    # specific part in use by Quintijn:
    if siteRoot:
        gramSpec = gramSpec + """
<site> exported = site ({sites}|{sites} <sitecommands>);
<siteshort> exported = site <sitecommands>;
<sitecommands> = {sitecommands} | {sitecommands} (<foldercommands>|<websitecommands>) |
                    <foldercommands> | <websitecommands>;
        """

    def initialize(self):
        if not self.language:
            print "no valid language in grammar "+__name__+" grammar not initialized"
            return
        
        self.load(self.gramSpec)
        self.lastSite = None
        self.switchOnOrOff() # initialises lists from inifile, and switches on
                             # if all goes well (and variable onOrOff == 1)
        self.envDict = natlinkcorefunctions.getAllFolderEnvironmentVariables()   # for (generalised) environment variables
        self.subfiles = self.subfiles = self.activeFolder = None  # for catching on the fly in explorer windows (CabinetClassW)
        self.className = None

    def gotBegin(self,moduleInfo):
        if self.checkForChanges:
            self.checkInifile() # refills grammar lists and instance variables
                                # if something changed.
        if self.mayBeSwitchedOn == 'exclusive':
            print "exclusive (_folders), do switchOnOrOff"
            self.switchOnOrOff()
        hndle = moduleInfo[2]
        if hndle and (self.trackAutoFiles or self.trackAutoFolders):

            className = win32gui.GetClassName(hndle)
            activefolder = self.getActiveFolder(hndle, className)
            #print 'activefolder: %s'% activefolder
            if activefolder and os.path.isdir(activefolder) and activefolder != self.activeFolder:
                self.fillListsForActiveFolder(activefolder, className)
                print 'set %s (sub)files and %s subfolders'% (len(self.subfilesDict), len(self.subfoldersDict))
            else:
                if self.activeFolder:
                    self.emptyListsForActiveFolder()
        elif self.activeFolder:
            self.emptyListsForActiveFolder()

    def gotResultsInit(self,words,fullResults):
        if self.mayBeSwitchedOn == 'exclusive':
            print 'recog folders, switch off mic'
            natbj.SetMic('off')
        self.wantedFolder = self.wantedFile = self.wantedWebsite = None

    def fillList(self, listName):
        """fill a list in the grammar from the data of the inifile

        overload, because the list sites is special:reversed
        the section [site] must exist,on the right side is to spoken form.
        """
        #print 'fill list', listName
        if listName == 'sites':
            if not siteRoot:
                print 'sites rules ignored'
                self.emptyList(listName)
                return #  skip the site part
            self.sitesDict = self.getListOfSites(siteRoot)
            items = self.sitesDict.keys()
            self.setList(listName, items)
            self.ini.writeIfChanged()
            self.sitesInstances = {}  # to be filled with instance of a site
            return items
            
        elif listName == 'folders':
            if self.foldersDict:
                items = self.foldersDict.keys()
                self.setList('folders', items)
                return items
            else:
                print 'no folders to set list to'
                self.emptyList('folders')

        elif listName == 'files':
            if self.filesDict:
                items = self.filesDict.keys()
                self.setList('files', items)
                return items
            else:
                print 'no files to set list to, edit _folders.ini if you wish to call individual files...'
                self.emptyList('files')
        elif listName in ['subversionfilecommands', 'subversionfoldercommands']:
            if self.doSubversion:
                return ancestor.fillList(self, listName)
            else:
                self.emptyList(listName)
        else:
            return ancestor.fillList(self, listName)

    def fillInstanceVariables(self):
        """fills the necessary instance variables
  
        take the lists of folders, virtualdrives (optional) and remotedrives (optional).
        
        """
        self.xxExplorer = self.ini.get('general', '2xexplorer')
        
        # extract special variables from ini file:
        self.virtualDriveList = self.ini.get('virtualdrives')
        #checking the paths of virtualDriveList:
        for dr in self.virtualDriveList[:]:
            folder1 = self.ini.get('virtualdrives', dr)
            folder = self.substituteFolder(folder1)
            if not os.path.isdir(folder):
                print 'warning _folders, virtualdrive "%s" does not exist: %s'% (dr, folder)
                self.virtualDriveList.remove(dr)
                self.ini.delete('virtualdrives', dr)
                self.ini.set('obsolete virtualdrives', dr, folder1)

        #  checking the passes of all folders:
        foldersList = self.ini.get('folders')
        self.foldersDict = {}
        for f in foldersList:
            folder = self.substituteFolder(self.ini.get('folders', f))
            if not os.path.isdir(folder):
                print 'warning _folders,  folder "%s" does not exist (move away): "%s"'% (f, folder)
                self.ini.delete('folders', f)
                self.ini.set('obsolete folders', f, folder)
                continue
            self.foldersDict[f] = folder
        
        # track virtual drives if in ini file:
        self.trackFolders = self.ini.getList('general', 'track folders virtualdrives')
        self.trackFiles = self.ini.getList('general', 'track files virtualdrives')

        # in order to accept .py but it should be (for fnmatch) *.py etc.:
        self.acceptFileExtensions = self.ini.getList('general', 'track file extensions')
        self.ignoreFilePatterns = self.ini.getList('general', 'ignore file patterns')
        
        # these are for automatic tracking the current folder:
        self.trackAutoFolders = self.ini.getBool('general', 'automatic track folders')
        self.trackAutoFiles = self.ini.getBool('general', 'automatic track files')
        windowsVersion = natqh.getWindowsVersion()
        if (self.trackAutoFiles or self.trackAutoFolders) and  windowsVersion in ('XP', '2000', 'NT4', 'NT351', '98'):
            print '_folders: the options for "automatic track files" and "automatic track folders" of a directory probably do not work for this Windows version: %s'% windowsVersion
            
        self.doSubversion = self.ini.get('general', 'subversion executable')
        if self.doSubversion:
            if not os.path.isfile(self.doSubversion):
                print 'not a valid path to subversion executable: %s, ignore'% self.doSubversion
                self.doSubversion = None
                
        self.foldersSections = ['folders']
        # track folders:
        for trf in self.trackFolders:
            if not trf:
                continue
            trf2 = self.substituteFolder(trf)
            if not os.path.isdir(trf2):
                print 'warning, no valid folder associated with: %s (%s) (skip for track virtualdrives)'% (trf, trf2)
                continue
            subf = [f for f in os.listdir(trf2) if os.path.isdir(os.path.join(trf2, f))]
            self.trackFoldersSection = 'folders %s'% trf
            self.foldersSections.append(self.trackFoldersSection)
            self.acceptVirtualDrivesFolder(trf, trf2) # without f, take virtualdrive itself...
            for f in subf:
                self.acceptVirtualDrivesFolder(trf, trf2, f)
            self.cleanupIniFoldersSection(self.trackFoldersSection, trf)
        self.removeObsoleteIniSections(prefix="folders ", validPostfixes=self.trackFolders)
 
        # do the files:
        self.filesDict = {}
        self.trackFiles = self.ini.getList('general', 'track files virtualdrives')
        # in order to accept .py but it should be (for fnmatch) *.py etc.:
        self.acceptFileExtensions = self.ini.getList('general', 'track file extensions')
        self.ignoreFilePatterns = self.ini.getList('general', 'ignore file patterns')
        self.filesSections = ['files']
        # from section files (manual):
        filesList = self.ini.get('files')
        for f in filesList[:]:
            filename = self.substituteFilename(self.ini.get('files', f))
            if not os.path.isfile(filename):
                print 'warning _folders, file "%s" does not exist: "%s"'% (f, filename)
                self.ini.delete('files', f)
                self.ini.set('obsolete files', f, filename)
                continue
            self.filesDict[f] = filename

        for trf in self.trackFiles:
            if not trf:
                continue
            trf2 = self.substituteFolder(trf)
            if not os.path.isdir(trf2):
                print 'warning, no valid folder associated with: %s (%s) (skip for track files)'% (trf, trf2)
                continue
            filesList = [f for f in os.listdir(trf2) if os.path.isfile(os.path.join(trf2, f))]
            self.trackFilesSection = 'files %s'% trf
            self.filesSections.append(self.trackFilesSection)
            for f in filesList:
                self.acceptFileInFilesDict(trf, trf2, f)
            self.cleanupIniFilesSection(self.trackFilesSection, trf)
        self.removeObsoleteIniSections(prefix="files ", validPostfixes=self.trackFiles)

        self.childBehaveLikeTop = self.ini.getDict('general', 'child behaves like top')
                
        # save changes if there were any:
        self.ini.writeIfChanged()        

    def acceptVirtualDrivesFolder(self, vd, realfolder, foldername=None):
        """check validity of virtualdrive subfolder and put or remove from inifile
    
        add to foldersDict if applicable
        
        """
        if foldername is None:
            #print 'virtual drive: %s, %s'% (vd, realfolder)
            f = vd
        else:
            f = foldername
        if not reLettersSpace.match(f):  # take only readable/speakable, only those are accepted by inivars
            #print 'skipping: %s'% f
            return  # nothing to do
        section = self.trackFoldersSection
        spoken = self.ini.getList(section, f, ['xpqzyx'])
        spoken = filter(None, spoken)
        if spoken == ['xpqzyx'] or not spoken:
            if foldername:
                spoken = [f]
            else:
                spoken = [vd,  os.path.split(realfolder)[-1]]
                if spoken[0] == spoken[1]:
                    spoken = spoken[:1]
                #print 'spoken for virtual drive: %s'% spoken
            self.ini.set(section, f, spoken)
        #else:
        if not spoken:
            return
        for sp in spoken:
            if foldername:
                self.foldersDict[sp] = vd + ':/' +  foldername
            else:
                self.foldersDict[sp] = vd 

    def getActiveFolder(self, hndle=None, className=None):
        """get active folder (only explorer and dialog #32770)
        """
        if hndle is None:
            hndle = natlink.getCurrentModule()[2]
        if not hndle:
            return
        if className is None:
            className = win32gui.GetClassName(hndle)
        if className == "CabinetWClass":
            return mess.getFolderFromCabinetWClass(hndle)
        elif className == '#32770':
            return mess.getFolderFromDialog(hndle, className)

    def fillListsForActiveFolder(self, activefolder, className):
        """fill list of files and subfolders
        also set activefolder and className
        
        this is for the automatic filling of the active window (either explorer, CabinetWClass,
        or child #32770.
        
        Seems to fail in windows XP and before.
        
        """
        subs = os.listdir(activefolder)
        subfolders = [s for s in subs if os.path.isdir(os.path.join(activefolder, s))]
        subfiles = [s for s in subs if os.path.isfile(os.path.join(activefolder, s))]
        self.subfoldersDict = self.getSpokenFormsDict(subfolders)
        self.subfilesDict = self.getSpokenFormsDict(subfiles, extensions=1)
        if self.trackAutoFiles:
            self.setList('subfiles', self.subfilesDict.keys())
        if self.trackAutoFolders:
            self.setList('subfolders', self.subfoldersDict.keys())
        self.activeFolder = activefolder
        self.className = className

    def emptyListsForActiveFolder(self):
        """no sublists, empty
        """
        if self.trackAutoFiles:
            self.emptyList('subfiles')
            self.subfilesDict.clear()
        if self.trackAutoFolders:
            self.emptyList('subfolders')
            self.subfoldersDict.clear()
        self.className = None
        self.activeFolder = None


    def cleanupIniFoldersSection(self, section, vd):
        """cleanup the current ini folder ... section (for non existing folders)
        """
        section = self.trackFoldersSection
        for f in self.ini.get(section):
            if f == vd:
                continue
            folder = self.substituteFolder(vd + ':/' + f)
            if not os.path.isdir(folder):
                print 'remove entry from ini folders section %s: %s (%s)'% (section, f, folder)
                self.ini.delete(section, f)
            elif not self.acceptFileName(f):
                print 'remove entry from ini folders section %s: %s (%s)(invalid folder name)'% (section, f, folder)
                self.ini.delete(section, f)
        self.ini.writeIfChanged()

    def cleanupIniFilesSection(self, section, vd):
        """cleanup the current ini files ... section (for non existing files)
        """
        for f in self.ini.get(section):
            filename = self.substituteFolder(vd + ':/' + f)
            trunk, ext = os.path.splitext(f)
            if not self.acceptExtension(ext):
                print 'remove entry from ini files section %s: %s (%s)(invalid extension)'% (section, f, filename)
                self.ini.delete(section, f)
            elif not self.acceptFileName(trunk):
                print 'remove entry from ini files section %s: %s (%s)(invalid filename)'% (section, f, filename)
                self.ini.delete(section, f)
            elif not os.path.isfile(filename):
                print 'remove entry from ini files section %s: %s (%s)'% (section, f, filename)
                self.ini.delete(section, f)
        self.ini.writeIfChanged()

    def removeObsoleteIniSections(self, prefix, validPostfixes):
        """remove sections that do NOT conform to prefix+ one of the postfixes
        (these were in "track files virtualdrives" or in "track folders virtualdrives"
        but have been removed in the inifile definition)
        """
        prefix = prefix.strip() + " "
        for section in self.ini.get():
            if not section.startswith(prefix):
                continue
            for postfix in validPostfixes:
                if section == prefix + postfix:
                    break
            else:
                print '_folders grammar, deleting ini file section: %s'% section
                self.ini.delete(section)
        self.ini.writeIfChanged()

    def acceptFileInFilesDict(self, vd, realfolder, filename):
        """check validity of filename in subfolder and put/remove in/from inifile
    
        add to filesDict if applicable
        
        """
        f = filename
        trunk, ext = os.path.splitext(f)
        if not self.acceptExtension(ext):
            return
        if not self.acceptFileName(trunk):
            return
                
        section = self.trackFilesSection
        spoken = self.ini.getList(section, f, ['xpqzyx'])
        spoken = filter(None, spoken)
        if spoken == ['xpqzyx'] or not spoken:
            spoken = [trunk]
            # skip if error in inivars:
            try:
                self.ini.set(section, f, spoken)
            except inivars.IniError:
                return

        if not spoken: return
        
        for sp in spoken:
            self.filesDict[sp] = vd + ':/' +  f
       
    def gotResults_siteshort(self,words,fullResults):
        """switch to last mentioned site in the list
        mainly for private use, a lot of folders reside in the root folder,
        siteRoot.  They all have an input folder and a output folder.


        """
        if self.lastSite:
            words.insert(1, self.lastSite)
            print 'lastSite: %s'% words
            self.gotResults_site(words, fullResults)
        else:
            self.DisplayMessage('no "lastSite" available yet')


    def gotResults_setenvironmentfolders(self,words,fullResults):
        """switch to last mentioned site in the list
        mainly for private use, a lot of folders reside in the root folder,
        siteRoot.  They all have an input folder and a output folder.


        """
        reverseOldValues = {'ignore': []}
        for k in self.ini.get('folders'):
            val = self.ini.get('folders', k)
            if val:
                reverseOldValues.setdefault(val, []).append(k)
            else:
                reverseOldValues['ignore'].append(k)
        reverseVirtualDrives = {}
        for k in self.ini.get('virtualdrives'):
            val = self.ini.get('virtualdrives', k)
            reverseVirtualDrives.setdefault(val, []).append(k)
            
##        print reverseOldValues
        allFolders = self.envDict()  #  natlinkcorefunctions.getAllFolderEnvironmentVariables()  
        kandidates = {}
        ignore = reverseOldValues['ignore']
        for (k,v) in allFolders.items():
            kSpeakable = k.replace("_", " ")
            if k in ignore or kSpeakable in ignore:
                continue
            oldV = self.ini.get('folders', k, "") or self.ini.get('folders', kSpeakable)
            if oldV:
                vPercented = "%" + k + "%"
                if oldV == v:
                    continue
                elif oldV == vPercented:
                    kPrevious = reverseOldValues[vPercented]
##                    print 'vPercented: %s, kPrevious: %s'% (vPercented, kPrevious)
                    if  vPercented in reverseOldValues:
                        if k in kPrevious or kSpeakable in kPrevious:
                            continue
                        else:
                            print 'already in there: %s (%s), but spoken form changed to %s'% \
                              (k, v, kPrevious)
                            continue
                else:
                    print 'different for %s: old: %s, new: %s'% (k, oldV, v)
            kandidates[k] = v
        count = len(kandidates)
        
        if not kandidates:
            self.DisplayMessage("no new environment variables to put into the folders section")
            return
        mes = ["%s new environment variables for your folders section of the grammar _folders"% count]
        
        Keys = kandidates.keys()
        Keys.sort()
        for k in Keys:
            mes.append("%s\t\t%s"% (k, kandidates[k]))

        mes.append('\n\nDo you want these new environment variables in your folders section?')
                       
                

        if YesNo('\n'.join(mes)):
            for (k,v) in kandidates.items():
                if k.find('_') > 0:
                    kSpeakable = k.replace("_", " ")
                    if self.ini.get('folders', k):
                        self.ini.delete('folders', k)
                else:
                    kSpeakable = k
                self.ini.set('folders', kSpeakable, "%" + k + "%")
            self.ini.write()
            self.DisplayMessage('added %s entries, say "Show|Edit folders" to browse'% count)
        else:
            self.DisplayMessage('nothing added, command canceled')
            

    def gotResults_website(self,words,fullResults):
        """start webbrowser, websites in inifile unders [websites]
        
        if www. is not given insert, if http:// is not given insert it.

        so if you have https:// or eg qh.antenna.nl you MUST insert https:// or http://

        """
        site = self.getFromInifile(words, 'websites')
        if site.startswith("http:") or site.startswith("https:"):
            pass
        else:
            if not site.startswith("www."):
                site = "http://www." + site
            else:
                site = "http://"+site
        if ((site.startswith('http:') or site.startswith('https:')) and 
                    site.find('\\') > 0):
            site = site.replace('\\', '/')
        
        if self.nextRule == 'websitecommands':
            self.wantedWebsite = site
        else:
            self.openWebsiteDefault(site)
            self.wantedWebsite = None
            
    def gotResults_thiswebsite(self,words,fullResults):
        """get current website and open with websitecommands rule
        
        """
        natqh.saveClipboard()
        action('SSK {alt+d}{extend}{shift+exthome}{ctrl+c}')
        action("VW")
        self.wantedWebsite = natqh.getClipboard()
        print 'this website: %s'% self.wantedWebsite
        natqh.restoreClipboard()
            
    def gotResults_websitecommands(self,words,fullResults):
        """start webbrowser, specified
        
        expect self.wantedWebsite to be filled.
        
        open with list in inifile, expected right hand sides to be browsers
        """
        if not self.wantedWebsite:
            print 'websitecommands, no valid self.wantedWebsite: %s'% self.wantedWebsite
        openWith, owIndex = self.hasCommon(words, ['open with'], withIndex=1)
        if openWith:
            openWith = self.getFromInifile(words[owIndex+1], 'websiteopenprograms', noWarning=1)
        self.openWebsiteDefault(self.wantedWebsite, openWith=openWith)

    def gotResults_folder(self, words, fullResults):
        """collects the given command words and try to find the given folder

        """
##        print '-------folder words: %s'% words
        if self.activeFolder and words[1] in self.subfoldersDict:
            subfolder = self.subfoldersDict[words[1]]
            folder = os.path.join(self.activeFolder, subfolder)
            print 'subfolder: %s'% folder
        else:
            subfolder = None
            folder1 = self.foldersDict[words[1]]
            folder = self.substituteFolder(folder1)
            
        # if no next rule, simply go:
        if not self.nextRule:
            # do action straight away:
            self.gotoFolder(folder)
            self.wantedFolder = None
        else:
            self.wantedFolder = folder

    def gotResults_site(self,words,fullResults):
        """switch to one of the sites in the list
        mainly for private use, a lot of folders reside in the root folder,
        siteRoot.  They all have an input folder and a output folder.

        """
        print 'site: %s'% words
        siteSpoken = words[1]
        self.lastSite = None # name of site
        if siteSpoken in self.sitesDict:
            siteName = self.sitesDict[siteSpoken]
            self.lastSite = siteName
        else:
            raise ValueError("no siteName for %s"% siteSpoken)
        
        self.site = self.getSiteInstance(siteName) 
            
        if siteName in self.sitesInstances:
            self.site = self.sitesInstances[siteName]
        else:
            site = self.getSiteInstance(siteName)
            if site:
                self.sitesInstances[siteName] = site
                self.lastSite = siteName
                self.site = site
            else:
                self.site = None
                print 'could not get site: %s'% siteName
        #
        #if site is None:
        #    print 'invalid site: %s, marking in ini file'% site
        #    self.ini.set('sites', siteName, '')
        #    self.ini.write()
        #    return
        if not self.nextRule:
            if self.site:
                rootDir = self.site.rootDir
                self.gotoFolder(rootDir)
            return
        elif self.nextRule == "sitecommands":
            print 'site, waiting for sitecommands'
        else:
            self.wantedFolder = self.site.rootDir
    
    def gotResults_sitecommands(self, words, fullResults):
        """do the various options for sites (QH special).
        Assume lastSite is set
        """
        if not self.site:
            print "sitecommands, no last or current site set"
            return
        print 'sitecommands for "%s": %s (site: %s)'% (self.lastSite, words, self.site)
        site = self.site
        website, folder = None, None
        for command in words:
            command = self.getFromInifile(words[0], 'sitecommands')
    
            if command == 'input':
                print 'input: %s'% words
                folder = str(site.sAbs)
            elif command == 'output':
                folder = str(site.hAbs)
            elif command == 'local':
                website = os.path.join(str(site.hAbs), 'index.html')
            elif command == 'online':
                sitePrefix = site.sitePrefix
                if type(sitePrefix) == types.DictType:
                    for k, v in sitePrefix.iteritems():
                        sitePrefix = v
                        break
                    
                website = os.path.join(str(sitePrefix), 'index.html')
            elif command == 'testsite':
                if 'sg' in self.sitesInstances:
                    testsite = self.sitesInstances['sg']
                else:
                    testsite = self.getSiteInstance('sg')
                    if testsite:
                        self.sitesInstances['sg'] = testsite

                if testsite:
                    # site at sitegen site:
                    website = os.path.join(str(testsite.sitePrefix['nl']), self.lastSite, 'index.html')

        if self.nextRule:
            if folder:
                self.wantedFolder = folder
                return
            elif website:
                self.wantedWebsite = website
                return
            else:
                print 'no valid folder or website for nextRule'
                return
        elif folder:
            self.gotoFolder(folder)
            self.wantedFolder = None
        elif website:
            self.openWebsiteDefault(website)
            self.wantedWebsite = None

    def getSiteInstance(self, siteName):
        """return pageopen function of site instance, or None
        """
        try:
            site = __import__(siteName)
        except ImportError:
            import traceback
            print 'cannot import module %s'% siteName
            print traceback.print_exc()
            print 'sys.path: %s'% sys.path 
            return
        if 'pagesopen' in dir(site):
            try:
                po = site.pagesopen()
                return po
            except:
                print '"pagesopen" failed for site %s'% siteName
                return
        else:
            print 'no function "pagesopen" in module: %s'% siteName
            return
        
    def findFolderWithIndex(self, root, allowed, ignore=None):
        """get the first folder with a file index.html"""

        for i in allowed:
            tryF = os.path.join(root, i)
            if os.path.isdir(tryF) and (
                os.path.isfile(os.path.join(tryF, 'index.html')) or \
                os.path.isfile(os.path.join(tryF, 'index.txt'))):
                return tryF
        if ignore and type(ignore) == types.ListType:
            # look in listdir and take first that is not to be ignored:
            try:
                List = os.listdir(root)
            except:
                return
            for d in List:
                if d in ignore:
                    continue
                tryF = os.path.join(root, d)
                if os.path.isdir(tryF) and os.path.isfile(os.path.join(tryF, 'index.html')):
                    return tryF

    def gotResults_folder(self, words, fullResults):
        """collects the given command words and try to find the given folder

        """
##        print '-------folder words: %s'% words
        if self.activeFolder and words[1] in self.subfoldersDict:
            subfolder = self.subfoldersDict[words[1]]
            folder = os.path.join(self.activeFolder, subfolder)
            print 'subfolder: %s'% folder
        else:
            subfolder = None
            folder1 = self.foldersDict[words[1]]
            folder = self.substituteFolder(folder1)
        if self.nextRule == "foldercommands":
            self.wantedFolder = folder
        else:
            self.gotoFolder(folder)
            self.wantedFolder = None

    def gotResults_foldercommands(self, words, fullResults):
        """open the folder and do additional actions
        
        the optionalfoldercommands (like new or paste) must appear in the
        right hand side of the inifile section (ie the value) (so spoken may be
        different)
        """
        if not self.wantedFolder:
            print 'rule foldercommands, no wantedFolder, return'
            return
        kw = {}
        for w in words: 
            opt = self.getFromInifile(w, 'foldercommands')
            if opt:
                if opt in self.optionalfoldercommands:
                    kw[opt] = opt
                elif opt.startswith('subversion '):
                    opt = opt[11:]
                    kw['subversion'] = opt
                else:
                    kw[w] = opt
        
        #print 'folderoptions: %s'% folderoptions
        #for opt in folderoptions:
        #    kw[opt.capitalize()] = opt
        Remote, remoteIndex = self.hasCommon(words, ['on'], withIndex=1)
        #print 'paste: %s, remote: %s, remoteIndex: %s'% (Paste, Remote, remoteIndex)
        if Remote:
            remoteLetter = self.getFromInifile(words[remoteIndex+1], 'letters')
            print 'remoteLetter: %s'% remoteLetter
            kw['remote'] = remoteLetter
        
        Subversion, svnIndex = self.hasCommon(words, ['subversion'], withIndex=1)
        if Subversion:
            svnCommand = self.getFromInifile(words[svnIndex+1], 'subversionfoldercommands')
            kw['subversion'] = svnCommand
        
        self.gotoFolder(self.wantedFolder, **kw)

    def get_active_explorer(self):
        handle = win32gui.GetForegroundWindow()
        shell = Dispatch("Shell.Application")

        for window in shell.Windows():
            if int(window.HWND) == int(handle):
                return window
        print "_folders: no active explorer."
        return None        
    
    def get_current_directory(self):
        window = self.get_active_explorer()
        if window is None:
            return
        path = urllib.unquote(window.LocationURL)
        
        for prefix in ["file:///", "http://"]:
            if path.startswith(prefix):
                lenprefix = len(prefix)
                path = path[lenprefix:]
        return path

    def get_selected_paths(self):
        window = self.get_active_explorer()
        if window is None:
            print 'get_selected_paths, cannot find application'
            return
        items = window.Document.SelectedItems()
        paths = []
        for item in collection_iter(items):
            paths.append(item.Path)
        return paths

    def get_selected_filenames(self):
        paths = self.get_selected_paths()
        if paths is None:
            return
        return [os.path.basename(p) for p in paths]

    def gotResults_thisfile(self, words, fullResults):
        print 'filenames: %s'% self.get_selected_filenames()
        paths = self.get_selected_paths()
        if paths:
            self.wantedFile = paths[0]
        else:
            print 'cannot find "thisfile"'
            return
        print 'wantedFile: %s'% self.wantedFile
        #self.wantedFile = self.getActiveFile()
        if not (self.wantedFile and os.path.isfile(self.wantedFile)):
            print 'cannot get thisfile for further processing: %s'% self.wantedFile
        #self.gotoFile(self.get_selected_paths()[0], False, False, False, False, False, False,
        #                  OpenWith=openWithProgram)

   # deze regel print de naam van de huidige module in het debug-venster
    def gotResults_disc(self,words,fullResults):
##        print '-------drive words: %s'% words
        letter = self.getFromInifile(words, 'letters')
        if letter:
            f = letter + ":\\"
        else:
            print '_folders, ruls disc, no letter provided: %s'% words
            return
        
        if self.nextRule == 'foldercommands':
            self.wantedFolder = f
        else:
            self.gotoFolder(f)
            self.wantedFolder = None

    def gotResults_file(self,words,fullResults):
        """collects the given command words and try to find the given file

        """
        File = None
        if self.activeFolder and words[1] in self.subfilesDict:
            print "given file dictation " + words[1]
            File = self.subfilesDict[words[1]]
            print "actual filename " + File
            extension =self.getFromInifile(words, 'extensions', noWarning=1)
            if extension:
                File, old_extension =os.path.splitext (File)
                File = File +'.' + extension
            File = os.path.join(self.activeFolder, File)
            if not os.path.isfile(File):
                File = None
            print 'file from subfileslist: %s'% file
        if not File:
            File = self.filesDict[words[1]]
            File = self.substituteFolder(File)
            print "actual filename (fixed fileslist)" + File
            extension =self.getFromInifile(words, 'extensions', noWarning=1)
            if extension:
                File, old_extension =os.path.splitext (File)
                File = File +'.' + extension
            if not os.path.isfile(File):
                print 'invalid file: %s'% File
                return
        if self.nextRule == "filecommands":
            self.wantedFile = File
        else:
            self.gotoFile(File)
            self.wantedFile = None

    def gotResults_filecommands(self, words, fullResults):
        
        if not self.wantedFile:
            print 'rule filecommands, no wantedFile, return'
            return
        print 'filecommands: %s'% words
        kw = {}
        for w in words:
            opt = self.getFromInifile(w, 'filecommands')
            if opt:
                if opt in self.optionalfoldercommands:
                    kw[opt] = opt
                elif opt.startswith('subversion '):
                    opt = opt[11:]
                    kw['subversion'] = opt
                    
                else:
                    kw[w] = opt
        
        #print 'folderoptions: %s'% folderoptions
        #for opt in folderoptions:
        #    kw[opt.capitalize()] = opt
        Remote, remoteIndex = self.hasCommon(words, ['on'], withIndex=1)
        #print 'paste: %s, remote: %s, remoteIndex: %s'% (Paste, Remote, remoteIndex)
        if Remote:
            remoteLetter = self.getFromInifile(words[remoteIndex+1], 'letters')
            print 'remoteLetter: %s'% remoteLetter
            kw['remote'] = remoteLetter
        
        OpenWith, owIndex = self.hasCommon(words, ['open with'], withIndex=1)
        if OpenWith:
            OpenWith = self.getFromInifile(words[owIndex+1], 'fileopenprograms')
            print 'openwith: %s'% OpenWith
            kw["openwith"] = OpenWith
        
        Subversion, svnIndex = self.hasCommon(words, ['subversion'], withIndex=1)
        if Subversion:
            svnCommand = self.getFromInifile(words[svnIndex+1], 'subversionfilecommands')
            print 'subversion file command: %s'% svnCommand
            kw['subversion'] = svnCommand
        self.gotoFile(self.wantedFile, **kw)
        
    # methods gotResults_info and gotResults_onoroff are
    # provided in IniGrammar
    def gotResults_thisfolder(self,words,fullResults):
        """do additional commands for current folder

        assume foldercommands follow, so         
        """
        #prog, title, topchild, windowHandle = natqh.getProgInfo()
        #hndle = natlink.getCurrentModule()[2]
        #istop = topchild, windowHandle == 'top'
        #if not istop:
        #    keystroke('{Shift+Tab}')
        #if self.activeFolder:
        other_active_folder = self.get_current_directory()
        if self.activeFolder:
            self.wantedFolder = self.activeFolder
        else:
            self.wantedFolder = self.getActiveFolder()
        if self.wantedFolder is None and other_active_folder:
            self.wantedFolder = other_active_folder
        if not self.wantedFolder:
            print 'did not find active (current) folder'
            return
        if not os.path.isdir(self.wantedFolder):
            print 'not a valid active (current) folder: "%s"'% self.wantedFolder
            return
        print 'wantedFolder: %s (get_current_directory: %s)'% (self.wantedFolder, other_active_folder)
        
    def gotResults_folderup(self,words,fullResults):
        """ go up in hierarchy"""
        upn = self.getNumberFromSpoken(words[-1])
        #print 'folderup: %s'% upn
        m = natlink.getCurrentModule()
        prog, title, topchild, windowHandle = natqh.getProgInfo(modInfo=m)
        hndle = m[2]
        Iam2x = prog == '2xexplorer'
        IamExplorer = prog == 'explorer'
        IamChild32770 = topchild, windowHandle == 'child' and win32gui.GetClassName(hndle) == '#32770'
        if IamChild32770:
            self.className = '#32770'
        browser = prog in ['iexplore', 'firefox','opera', 'netscp']
        istop = topchild == 'top'
        if IamChild32770:
            if not self.activeFolder:
                self.activeFolder = mess.getFolderFromDialog(hndle, self.className)
            if self.activeFolder:
                newfolder = self.goUpInPath(self.activeFolder, upn)
                #print 'newfolder (up %s): %s'% (upn, newfolder)
                self.gotoInThisDialog(newfolder, hndle, self.className)
            else:
                print 'method not working (any more) for #32770: %s'% title
            
        elif not (istop or self.checkChildBehaveLikeTop(prog, title)):   # child window actions
            
            action("RMP 1, 0.02, 0.05, 0")
            action("<<filenameenter>>; {shift+tab}")
            action("{backspace %s}"% upn)
        elif browser:
            natqh.saveClipboard()
            keystroke('{alt+d}{extend}{shift+exthome}{ctrl+c}')
            t = natqh.getClipboard()
            prefix, path = t.split('://')
            T = path.split('/')
            if len(T) > upn:
                T = T[:-upn]
            else:
                T = T[0]
            
            keystroke(prefix + '://' + '/'.join(T))
            keystroke('{enter}')
            natqh.restoreClipboard()
        elif IamExplorer:
            if not self.activeFolder:
                self.activeFolder = mess.getFolderFromCabinetWClass(hndle)
            if self.activeFolder:
                newfolder = self.goUpInPath(self.activeFolder, upn)
                print 'newfolder (up %s): %s'% (upn, newfolder)
                self.gotoInThisComputer(newfolder)
            else:
                print 'method not working any more, going folder up'
                action("MP 1, 50, 10, 0")
                for i in range(upn):
                    action("{backspace} VW")
            
        else:            
            print 'yet to implement, folder up for  %s'% prog
            
        #print 'had folder up: %s'% words
        
    
    def substituteFolder(self, folder):
        """substitute virtual drive into for  into folder name

        If a virtual drive is not in folder name, simply
        the name is returned, otherwise the contents of
        this virtual drive are inserted.
          
        """
        folder = folder.replace('/', '\\')
        folder = self.substituteEnvVariable(folder)
        
        if not self.virtualDriveList:
            return folder
        if folder.find(':\\') > 0:
            drive, rest = folder.split(":\\", 1)
        elif folder.find(":") == -1 and folder.find('\\') == 2:
            drive, rest = folder.split("\\", 1)
        elif folder.find(':') > 0:
            drive, rest = folder.split(":", 1)
        else:
            drive, rest = folder, ''

        if drive in self.virtualDriveList:
            vd = self.ini.get('virtualdrives', drive)
            vd = self.substituteFolder(vd)
            if rest:
                return os.path.join(vd, rest)
            else:
                return vd
        else:
            return folder

    def substituteEnvVariable(self,folder):
        """honor environment variables like %HOME%, %PROGRAMFILES%

        %HOME% is also recognised by ~ (at front of name)
        """

        # find possible envvar, ~ or something else...        
        if folder.startswith('~'):
            envVar = '~'
        else:
            m = reEnv.match(folder)
            if not m:
                return folder
            envVar = m.group(1)
        # get the envVar...
        try:
            substitute = natlinkcorefunctions.getExtendedEnv(envVar)
        except ValueError:
            print "_folders: cannot get substitute for %%%s%%"% envVar
            return folder

        # found substitute, so substitute:
        if envVar == '~':
            folder = folder[1:]
        else:
            folder = folder[len(envVar)+2:]
        folder = folder.lstrip('\\/')
        folder = os.path.join(substitute, folder)
        return folder

    def substituteFilename(self, filename):
        """substitute virtual drive into for  into filename,and possibly the spoken form

        If a virtual drive is not in folder name, simply
        the name is returned, otherwise the contents of
        this virtual drive are inserted.
          
        """
        filename = filename.replace('/', '\\')
        filename = self.substituteEnvVariable(filename)
        if filename.find(':\\') > 0:
            drive, rest = filename.split(":\\", 1)
            if drive in self.virtualDriveList:
                drive1 = self.substituteFolder(drive)
##                print 'drive for: |%s|: |%s|'% (drive, drive1)
                return os.path.join(drive1, rest)
        elif filename.find(':') == -1 and filename.find('\\') == 2:
            drive, rest = filename.split("\\", 1)
            drive1 = self.substituteFolder(drive)
            return os.path.join(drive1, rest)
        elif filename.find('\\') > 0:
            start, rest = filename.split("\\", 1)
            F = self.getFromInifile(start, 'folders')
            if F:
                start = self.substituteFolder(F)
                return os.path.join(start, rest)
        return filename  

    def getSpokenFormsDict(self, List, extensions=None):
        """make speakable forms, leave out extensions if extensions = 1
        
        files: set extensions to 1, and 
            take only extensions from the list self.acceptFileExtensions
            (to be set in ini file
        
        """
        D = {}
        for item in List:
            if extensions:
                spoken, ext = os.path.splitext(item)
                if not self.acceptExtension(ext):
                    continue
                if not self.acceptFileName(spoken):
                    continue
            else:
                if not self.acceptFileName(item):
                    continue
                spoken = item
            spokenList = self.spokenforms.generateMixedListOfSpokenForms(spoken)
            #if spoken.startswith('.'):
            #    spoken = 'dot ' + spoken[1:]
            #    spoken = 'underscore ' + spoken[1:]
            for spoken in spokenList:
                D[spoken] = item
        #print '----D:\n%s\n----'% D
        return D      

    def getSpokenDetail(self, detail):
        """if numeric, get number else return same
        """
        try:
            n = int(detail)
        except ValueError:
            return detail
        if n in self.spokenforms.n2s:
            return self.spokenforms.n2s[n][0]
        return detail
    
    def acceptExtension(self, ext):
        """accept file extension according to settings
        
        acceptFileExtensions
        """
        if ext.lower() in self.acceptFileExtensions:
            return 1

    def acceptFileName(self, item, extensions=None):
        """return 1 if filename ok, only filename expected here
        """
        for pat in self.ignoreFilePatterns:
            if fnmatch.fnmatch(item, pat):
                return
        return 1
    
    def gotoFile(self, f, **kw):
        """goto the file f"""
        if not os.path.isfile(f):
            self.DisplayMessage('file does not exist: %s'% f)
            return
        m = natlink.getCurrentModule()
        prog, title, topchild, windowHandle = natqh.getProgInfo(modInfo=m)
        mode = openWith = None
        istop = topchild == 'top'

        for opt in self.optionalfilecommands:
            exec("%s = None"% opt.capitalize())
        additionalOptions = []
        for k, v in kw.items():
            if k in self.optionalfilecommands:
                print 'setting option %s to %s'% (k, v)
                exec("%s = '%s'"% (k.capitalize(), v))
            else:
                additionalOptions.append(v)
        print 'additional options: %s'% additionalOptions
        
        if Remote:
            print 'Remote: %s'% Remote
            driveIndex = f.find(":")
            if driveIndex > 0:
                drMinus = driveIndex - 1
            f = f[:drMinus] + Remote + f[driveIndex:]
            if not os.path.isfile(f):
                self.DisplayMessage('remote file %s (on drive %s) does not exist'%\
                                   (f,Remote))
                return

        if Subversion:
            print 'subversion command "%s" for file "%s"'% (Subversion, f)
            self.doSubversionCommand(Subversion, f)
            return
        if Edit:
            mode = 'edit'        
        else:
            mode = 'open'

        if Copy:
            natqh.setClipboard(f)
            return
        if Paste:
            keystroke(f)
            return
 
        print 'additional options: %s'% additionalOptions


        if not (istop or self.checkChildBehaveLikeTop(prog, title)):   # child window actions
            # put the mouse in the left top corner of the window:
            print "Open file from child window: %s"% f
            action("RMP 1, 0.02, 0.05, 0")
            action('<<filenameenter>>')
            natqh.saveClipboard()
            keystroke('{Ctrl+x}')
            keystroke(f)
            action('<<filenameexit>>')
            keystroke('{Ctrl+v}')
            natqh.restoreClipboard()
            keystroke('{Shift+Tab}')
        else:
            # top or top behaviourthis
            kw = dict(mode=mode, openWith=Openwith)
            self.openFileDefault(f, mode=mode, openWith=Openwith, addOpts=additionalOptions)
        
    def openFileDefault(self, filename, mode=None, openWith=None, addOpts=None):
        """open the file in the default window and perform additional options"""
##        action('CW')
        if not os.path.isfile(filename):
            print 'file does not exist, cannot open: %s'% filename
            return
        if not ancestor.openFileDefault(self, filename, mode=mode, openWith=openWith):
            print 'could not open %s (mode: %s, openWith: %s)'% (filename, mode, openWith)
            return
        if addOpts:
            for opt in addOpts:
                action(opt)

    def openFolderDefault(self, foldername, *args):
        """open the folder in the default window
        
        if succeed, perform optional additional options.
        
        """
##        action('CW')
        #print 'going to open folder: %s'% foldername
        if not ancestor.openFolderDefault(self, foldername):
            print 'failed to open folder: %s'% foldername
            return
        for opt in args:
            action(opt)
            
    #  This is the function which does the real work, depending on the
    #    window you are in
    def gotoFolder(self, f, **kw):
        """go to the specified folder

        f = the (local) folder to go to
        options to be set in dict kw:
        --New = true if a new window is asked for
        --Explorer = true is an explorer window (possibly 2xExplorer) is wanted (obsolete)
        --Remote = the remote drive letter if the folder is wanted on another drive

        this is the central routine, with complicated strategy for getting it,
        in pseudocode:
        
        If QuickMode, we are in CabinetWClass and probably want a subfolder
        
        if New:
            if Explorer:
                start start new Explorer
                (xxExplorer or Windows Explorer)
            elif isTop and in xxExplorer:
                go to other pane
            else:
                get new folder
        else:
            if Explorer:
                search for Explorer or start new
                (mainly for cases: in child or if xxExplorer is switched on)
            elif isChild:
                get the folder
            else: # isTop!
                if in xxExplorer:
                    get the folder
                else:
                    look for all for the Windows with titles
                    if exact:
                        go to that folder window
                    elif overList: (titles are longer than folder asked for)
                        get folder in this window
                        (if you are already there, switch to the folder you want)
                    elif underList: (titles are shorter than folder you asked for)
                        take longest of the windows, if you are in goto exact
                    else:
                        if part of path is common, switch to that and goto folder

                        
        """
        f = os.path.normpath(f)
        if not os.path.isdir(f):
            self.DisplayMessage('folder does not exist: %s'% f)
            return
        QuickMode = None
        for opt in self.optionalfoldercommands:
            exec("%s = None"% opt.capitalize())
        additionalOptions = []
        for k, v in kw.items():
            if k in self.optionalfoldercommands:
                # special options, not handled in foldercommands in inifile:
                exec("%s = '%s'"% (k.capitalize(), v))
            else:
                additionalOptions.append(v)
        addOpts = tuple(additionalOptions)
        
        if Subversion:
            print 'do subversion command "%s" on "%s"'% (Subversion, f)
            self.doSubversionCommand(Subversion, f)
            return
        
        xx = self.xxExplorer
        if Remote:
            print 'Remote: %s'% Remote
            driveIndex = f.find(":")
            if driveIndex > 0:
                drMinus = driveIndex - 1
            f = f[:drMinus] + Remote + f[driveIndex:]
            if not os.path.isdir(f):
                self.DisplayMessage('folder %s (on drive %s) does not exist'%\
                                   (f,Remote))
                return
        if Paste:
            keystroke(f)
            return
        if Copy:
            print 'put path on clipboard: "%s"'% f
            natqh.setClipboard(f)
            return
        m = natlink.getCurrentModule()
        prog, title, topchild, windowHandle = natqh.getProgInfo(modInfo=m)
        Iam2x = prog == '2xexplorer'
        IamExplorer = prog == 'explorer'
        browser = prog in ['iexplore', 'firefox','opera', 'netscp']
        istop = topchild == 'top'
##        print 'iambrowser:', browser
##        print 'xx: %s, Iam2x: %s, IamExplorer: %s'% (xx, Iam2x, IamExplorer)
        if New:
            if Explorer:
                if xx:
                    self.doStart2xExplorer()
                    self.gotoIn2xExplorer(f)
                    return
                else:
                    self.openFolderDefault(f, *addOpts)
                    
##
####                    print 'starting windows explorer'
##                    self.doStartWindowsExplorer()
##                    self.gotoInThisComputer(f)
                    return
            elif istop and Iam2x:
                keystroke('{tab}')
                # and go on in the next section!
            else:
                self.openFolderDefault(f, *addOpts)
##
####                print 'starting this computer'
##                self.doStartThisComputer()
##                self.gotoInThisComputer(f)
                return
        # now ready for a go:
        m = natlink.getCurrentModule()
        hndle = thisHandle = m[2]
        prog, title, topchild, windowHandle = natqh.getProgInfo(modInfo=m)
        Iam2x = prog == '2xexplorer'
        IamExplorer = prog == 'explorer'
        istop = topchild == 'top'
        IamChild32770 = topchild == 'child' and win32gui.GetClassName(hndle) == '#32770'
        if IamChild32770:
            self.className = '#32770'
        istop = topchild == 'top'
        if IamChild32770:
            self.gotoInThisDialog(f, hndle, self.className)
            return
        elif QuickMode and self.className == 'CabinetWClass':
            self.gotoInThisComputer(f)
            return

        #print 'no dialog 32770 or QuickMode, finding good window for %s'% f
        if Explorer:
            if xx:
                self.doStart2xExplorer()
                self.gotoIn2xExplorer(f)
                return
            else:
                pass # simply look for a window outside child
        elif not (istop or  self.checkChildBehaveLikeTop(prog,title)):   # child window actions
            # put the mouse in the left top corner of the window:
            action("RMP 1, 0.02, 0.05, 0")
            action('<<filenameenter>>')
            natqh.saveClipboard()
            keystroke('{Ctrl+x}')
            keystroke(f)
            action('<<filenameexit>>')
            keystroke('{Ctrl+v}')
            natqh.restoreClipboard()
            keystroke('{Shift+Tab}')
            return

        # rest, in top, look for right window:
        if Iam2x:
            self.gotoIn2xExplorer(f)
            return

        # search folder titles (with Class name: CabinetWClass)
        LIST = getExplorerTitles()
        if not LIST:
            self.openFolderDefault(f, *addOpts)

##            
##            print 'no lists, start this computer'
##            self.doStartThisComputer()
##            self.gotoInThisComputer(f)                
            return
        
        exactList = []
        overList = [] # windowtitle longer than wanted folder
        underList = [] # windowtitle shorter than wanted folder
        restList = []
##            print 'find appropriate window'
        for t, h in LIST:
            if t == f:
                exactList.append((t, h))
            elif t.find(f) == 0:
                overList.append((t, h))
            elif f.find(t) == 0:
                underList.append((t, h))
            else:
                restList.append((t,h))
        #print 'searching for: ', f
        #print 'exactList: ', exactList
        #print 'overList: ', overList
        #print 'underList: ', underList
        #print 'restList: ', restList
        if exactList:
##                print 'exactList %s' % (exactList)
            if len(exactList) > 1:
                print 'warning, 2 matching windows: %s'% exactList
            t, h = exactList[0]
            natqh.SetForegroundWindow(h)
        elif overList:
##            print 'over List %s' % (overList)
            # eg f = d:\\a\\b
            # and elements of overList are d:\\a\\b\\c and d:\\a\\b\\c\\d
            # goto shortest element
            # later make choice list of where to go
            if len(overList) == 1:
                t, h = overList[0]
                natqh.SetForegroundWindow(h)
            lenMin = 999
            for t, h in overList:
##                    print 'nearList: %s'% nearList
                if len(t) < lenMin:
                    take = h
                    lenMin = len(t)
                
##                print 'i: %s, take: %s'% (i, nearList[i])
            toHandle = take

            if thisHandle == toHandle:
                self.gotoInThisComputer(f)
            else:
                natqh.SetForegroundWindow(take)
        elif underList:
            # eg f = d:\\a\\b\\c
            # elementes of underList are d:\\a d:\\a\\b etc.
            # go to longest element and switch in that window to folder
            print 'under list, go to first folder'
            lenMax = 0
            
            for t, h in underList:
##                    print 'nearList: %s'% nearList
                if len(t) > lenMax:
                    take = h
                    lenMax = len(t)
            if natqh.SetForegroundWindow(take):
                self.gotoInThisComputer(f)

        elif restList:
##            print 'rest list, go to first folder'
            # get longest "intersection" of restList and f
            # being the most convenient window for displaying the folder
            take = getLongestCommon(restList, f) # tuple (title, handle)
##            print 'take: ', `take`
            if take:
                t, h = take
                if natqh.SetForegroundWindow(h):
                    self.gotoInThisComputer(f)
                else:
                    print 'could not set foregroundwindow: %s'% h
                    self.openFolderDefault(f, *addOpts)
                    
            else:
                #print 'no matching window at all, start new'
                self.openFolderDefault(f, *addOpts)
##                self.doStartThisComputer()
##                self.gotoInThisComputer(f)                
        else:
            # no this computer windows (yet)
            print "grammar folders shouldn't be here!"  

    def getListOfSites(self, root):
        """return list of sitenames, to be found as python files in root
        
        """
        pyfiles = [f for f in os.listdir(root) if f.endswith('.py')]
        #print 'pyfiles for sites: %s'% pyfiles
        D = {}
        entries = self.ini.get('sites')
        for p in pyfiles:
            trunk = p[:-3]
            if not reOnlyLowerCase.match(trunk):
                continue   # only lowercase items can be a sites item, so __init__ and HTMLgen etc are skipped
            if trunk in entries:
                spokenList = self.ini.getList('sites', trunk)
                if not spokenList:
                    #print 'empty item in siteslist: %s'% trunk
                    continue
                else:
                    for spoken in spokenList:
                        spoken = self.spokenforms.correctLettersForDragonVersion(spoken)
                        D[spoken] = trunk
            else:
                # make new entry in sites section
                if len(trunk) <= 3:
                    spoken = '. '.join(list(trunk.upper()))+'.'
                else:
                    spoken = trunk
                spoken = self.spokenforms.correctLettersForDragonVersion(spoken)
                D[spoken] = trunk
                #print 'set in sites: %s -> %s'% (trunk, spoken)
                self.ini.set('sites', trunk, spoken)
        return D
        
    def doSubversionCommand(self, command, path):
        """launch subversion with command and path
        """
        args = '/command:%s /path:""%s""'% (command, path)
        
        # Construct arguments and spawn TortoiseSVN.
        name = "subversion %s %s"% (command, path)
        natqh.AppBringUp(name, self.doSubversion, args)
        

        
        
    def doStartThisComputer(self):
        """obsolet, openFileDefault works!!"""
        natqh.rememberWindow()
        startComputer = self.ini.get('general', 'start this computer')
        action(startComputer)
        
        try:
            natqh.waitForNewWindow(50, 0.05) # 2,5 seconds
        except natqh.NatlinkCommandTimeOut:
            print 'Error with action "start this computer" (%s) from command in grammar + "_folders".' % \
                  startComputer
            print 'Correct in ini file by using the command: ' +  {'enx': "Edit Folders",
                                               'nld': "Bewerk folders"}[self.language]
            return
        return 1

    def checkChildBehaveLikeTop(self, prog, title):
        """check if prog and title match with self.childBehaveLikeTop"""
        title = title.lower()
##        print 'self.childBehaveLikeTop: %s'% self.childBehaveLikeTop
        if prog in self.childBehaveLikeTop:
            wantedTitles = self.childBehaveLikeTop[prog]
##            print 'child behave like top?? title %s, wanted: %s'% (title, wantedTitles)
            if not wantedTitles:
                return 1   # found!
            if type(wantedTitles) != types.ListType:
                wantedTitles = [wantedTitles]

            for t in wantedTitles:
                t = t.lower()
                if title.find(t) >= 0:
                    print 'child window behaves like top: %s: %s'% (prog, title)
                    return 1
            
                

    def doStart2xExplorer(self):
        """starting the 2xExplorer

        """        
        command = 'AppBringUp "%s"'% self.xxExplorer
##                    print 'starting 2xExplorer: %s'% command
        natlink.execScript(command)
        natqh.Wait(1.0)
        keystroke("{alt+space}{extdown 4}{enter}")

    def gotoInThisComputer(self, f):
        """perform the keystrokes to go to a folder in this computer

        """
        keystroke('{alt+d}')
        action('W')
        keystroke(f)
        action('VW')
        if natqh.getWindowsVersion() == '7':
            keystroke('{enter}{shift+tab 3}')
        else:
            keystroke('{enter}{tab}')

    def gotoInThisDialog(self, f, hndle, className):
        """perform the keystrokes to go to a folder in a (#32770) Dialog

        """
        activefolder = self.activeFolder or mess.getFolderFromDialog(hndle, self.className)
        keystroke('{alt+d}')
        if os.path.isdir(f):
            folder, filename = f, None
        elif os.path.isfile(f):
            folder, filename = os.path.split(f)
        else:
            print 'invalid target for gotoInThisDialog: %s'% f
            return
        
        if folder != activefolder:
            keystroke(f)
            keystroke('{enter}')
        for i in range(4):
            action('W')
            keystroke('{shift+tab}')
        if filename:
            keystroke(filename)
            

    def goUpInPath(self, Path, nsteps):
        """return a new path, n steps up in hierarchy
        """
        if not nsteps:
            nsteps = 1
        for i in range(nsteps):
            Path = os.path.normpath(os.path.join(Path, '..'))        
        return Path

    def gotoIn2xExplorer(self, f):
        """perform the keystrokes to go to a folder in the 2xExplorer

        """
        keystroke('{alt+f}t')
        keystroke(f)
        keystroke('{enter}')

        
    def doStartWindowsExplorer(self):
        natqh.rememberWindow()
        startExplorer = self.ini.get('general', 'start windows explorer')
        action(startExplorer)
        try:
            natqh.waitForNewWindow(50, 0.05)  # 2,5 seconds max
        except natqh.NatlinkCommandTimeOut:
            print 'Error with action "start windows explorer" (%s) from command in grammar + "_folders".' % \
                  startExplorer
            print 'Correct in ini file by using the command: ' + {'enx': "Edit Folders",
                                              'nld': "Bewerk folders"}[self.language]
            return
        return 1        
                                

    def fillDefaultInifile(self, ini=None):
        """initialize as a starting example the ini file (obsolete)

        """       
        pass


def getLongestCommon(tupleList, f):
    """first part of tupleList must match most of f"""
    m = 0
    pToTake = ''
    hToTake = 0
    for (p,h) in tupleList:
        nCommon = getCommonLength(p, f)
##        print 'nCommon %s and %s: %s'% (p,f,nCommon)
            
        if nCommon > m and nCommon > 3:
            pToTake = p
            hToTake = h
            m = nCommon
    if hToTake:
        return pToTake, hToTake

def getCommonLength(a, b):
    i = 0
    la = len(a)
    lb = len(b)
    
    while i < la and i < lb and a[i] == b[i]:
        i += 1
    return i

def getExplorerTitles():
    """get all titles of top windows with class name in tuple below

    This class name belongs, as far as I know, to the window explorer window

    """
    TitlesHandles = []
    ## Classes come from global variable at top of this module
    ##print 'Classes:', Classes
##    Classes = None
    win32gui.EnumWindows(getExplWindowsWithText, (TitlesHandles, Classes))
    return TitlesHandles

def getExplWindowsWithText(hwnd, th):
    TH, Classes = th
    if win32gui.GetClassName(hwnd) in Classes:
        wTitle = win32gui.GetWindowText(hwnd).strip()
        TH.append((wTitle, hwnd))

# standard stuff Joel (adapted for possible empty gramSpec, QH, unimacro)
thisGrammar = ThisGrammar()
if thisGrammar.gramSpec:
    thisGrammar.initialize()
else:
    thisGrammar = None


def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None

def changeCallback(type, args):
    """special behaviour for martijn"""
    if ((type == 'mic') and (args=='on')):
        user = natqh.getUser()


## different functions#########################################3
outlookApp = None
outlookAppProgram = None
def connectOutlook():
    """connect to outlook"""
    global outlookApp, outlookAppProgram
    
    if outlookAppProgram != 'outlook' or not outlookApp:
        pass
        #outlookApp = win32com.client.Dispatch('Outlook.Application')
    if outlookApp:
        print 'outlook application collected'
        return outlookApp
    else:
        print 'outlook not connected'
        outlookApp = None
        outlookAppProgram = None
        return outlookApp
    

def collection_iter(collection):
    for index in xrange(collection.Count):
        yield collection.Item(index)
