/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 DragCode.h
 	CDragonCode is a class which encapusulates the main interface for
	communicating with NatSpeak.  This class also defined the functions
	which implement the export Python natlink functions.
*/

/*
 Modifications/Additions starting December 2011
	Marked up as "RW Added" or something similar throughout the code
	(c) Copyright by R�diger Wilke
*/

struct CGramObj;
struct CResObj;
struct CDictObj;
class CDgnSRNotifySink;
class CDgnAppSupport;
class CSecondThread;
class CMessageStack;

typedef const char * PCCHAR;

#ifdef INHOUSE
#include "inhouse.h"
#endif

//---------------------------------------------------------------------------

class CDragonCode
{
 public:
	
	CDragonCode() {
		m_hMsgWnd = NULL;
		m_dwKey = 0;
		m_pBeginCallback = NULL;
		m_pChangeCallback = NULL;
		m_pFirstGramObj = NULL;
		m_pFirstResObj = NULL;
		m_pFirstDictObj = NULL;
		m_pSecdThrd = NULL;
		m_bDuringInit = FALSE;
		m_bDuringPaused = FALSE;
		m_nCallbackDepth = 0;
		m_dwPendingCallback = 0;
		m_nPauseRecog = 0;
		m_deferredCookie = 0;
		m_pThreadState = NULL;
		m_pTimerCallback = NULL;
		m_nTimer = 0;
		m_bSetTraining = FALSE;
		m_pszLogFile = NULL;
		m_bHasTrayIcon = FALSE;
		m_pTrayIconCallback = NULL;
		m_pMessageStack = NULL;
		//
		// RW Added:
		//
		m_bWriteToDragonLog = FALSE;
		m_bRememberWindowPosition = FALSE;
		m_pszINIFile = NULL;
		m_defHeight = 280;
		m_defWidth = 395;
		m_initTop = 0;
		m_initLeft = 0;
		m_initRight = 0;
		m_initBottom = 0;
		m_xSize = 0;
		m_ySize = 0;
	}
	
	~CDragonCode() {
		natDisconnect();
	}

	// Each of these represents a function called from Python through
	// wrapper code in PythWrap.cpp.  If there is no return value, we
	// return TRUE on success or FALSE on error.  Otherwise, we return
	// a Python object on success or NULL on error.
	BOOL natConnect( IServiceProvider * pIDgnSite, BOOL bUseThreads = FALSE );
	BOOL natDisconnect();
	BOOL setBeginCallback( PyObject *pCallback );
	BOOL setChangeCallback( PyObject *pCallback );
	BOOL playString( const char * pszKeys, DWORD dwFlags );
	BOOL displayText( const char * pszText, BOOL bError = TRUE, BOOL blogText = TRUE );
	BOOL setMicState( const char * pszState );
	BOOL recognitionMimic( PCCHAR * ppWords );
	BOOL execScript(
		const char * pszScript, PCCHAR * ppWords, const char * pszComment );
	BOOL playEvents( DWORD dwCount, HOOK_EVENTMSG * pEvents );
	BOOL waitForSpeech( int nTimeout );
	BOOL inputFromFile(
		const char * pszFileName, BOOL bRealTime,
		DWORD dwPlayList, DWORD * adwPlayList, int nUttDetect );
	BOOL setTimerCallback( PyObject * pCallback, int nMilliseconds = 0 );
	BOOL startTraining( char * pMode );
	BOOL finishTraining( BOOL bNoCancel );
	BOOL createUser(
		char * pszUserName, char * pszBaseModel, char * pszBaseTopic );
	BOOL openUser( char * pszUserName );
	BOOL saveUser();
	BOOL deleteWord( char * wordName );
	BOOL setWordInfo( char * wordName, DWORD wordInfo );
	BOOL setTrayIcon( char * iconName, char * toolTip, PyObject * pCallback );
		
	PyObject * getCurrentModule();
	PyObject * getCurrentUser();
	PyObject * getMicState();
	PyObject * getCallbackDepth();
	PyObject * getCursorPos();
	PyObject * getScreenSize();
	PyObject * getTrainingMode();
	PyObject * getUserTraining();
	PyObject * getClipboard();
	PyObject * getAllUsers();
	PyObject * getWordInfo( char * wordName, int flags );
	PyObject * addWord( char * wordName, DWORD wordInfo, PCCHAR * ppProns );
	PyObject * getWordProns( char * wordName );

	// Also called from PythWrap.cpp but it never returns an error.  Instead
	// it returns TRUE or FALSE which is then needs to be converted into a
	// Python object.  We do this so this same routine can be called
	// internally in natConnect.
	BOOL isNatSpeakRunning();
	
	// this is called from CDgnAppSupport at initialization time
	void setAppClass( CDgnAppSupport * pAppClass ) { m_pAppClass = pAppClass; }
	void setDuringInit( BOOL bState ) { m_bDuringInit = bState; }
	
	// RW Added:
	//
	void setWriteToDragonLog( BOOL bState ) { m_bWriteToDragonLog = bState; }
	void setRememberWindowPosition( BOOL bState ) { m_bRememberWindowPosition = bState; }
	// End RW Added

	// these functions are called from CGramObj
	ISRCentral * pISRCentral() { return m_pISRCentral; }
	void addGramObj( CGramObj * pGramObj );
	void removeGramObj( CGramObj * pGramObj );

	// these functions are called from CResObj
	void addResObj( CResObj * pResObj );
	void removeResObj( CResObj * pResObj );

	// these functions are called from CDictObj
	void addDictObj( CDictObj * pDictObj );
	void removeDictObj( CDictObj * pDictObj );

	// when we need to post a message from a COM notify sink to the message
	// window, make this call
	void postMessage( UINT wMsg, WPARAM wParam, LPARAM lParam ) {
		PostMessage( m_hMsgWnd, wMsg, wParam, lParam );
	}
	
	// these functions are called when a message is posted to our message
	// window 
	void onMenuCommand( WPARAM wParam );
	void onPaused( WPARAM wParam );
	void onAttribChanged( WPARAM wParam );
	void onSendResults( WPARAM wParam, LPARAM lParam );
	void onTimer();
	void onTrayIcon( WPARAM wParam, LPARAM lParam );

	// these functions are called when we get a window message
	void onSendResultsCallback( PyObject *pFunc, PyObject *pArgs );

	// when the grammar object wants to make a results callback from a
	// PhraseFinish notification it calls this function.  We then post
	// ourself a message to make the actual callback.  The third argument
	// is the type of callback
	void makeResultsCallback( PyObject *pFunc, PyObject *pArgs );

	// this is what we call to reset m_nPauseRecog and process any deferred
	// pause request
	void resetPauseRecog();

	// access to the thread state
	PyThreadState * getThreadState() { return m_pThreadState; }

	// used in DictObj so we can create a VoiceDictation object
	IServiceProvider * getSiteObj() { return m_pIServiceProvider; }

	// use this to make a callback, this will catch any unhandled exceptions
	// and report them
	void makeCallback( PyObject *pFunc, PyObject *pArgs );

 protected:

	// these are our SAPI interface pointers.  We use ATL smart pointers to
	// avoid having to call AddRef and Release
	ISRCentralPtr m_pISRCentral;
	IDgnSREngineControlPtr m_pIDgnSREngineControl;
	IDgnSSvcOutputEventPtr m_pIDgnSSvcOutputEvent;
	IServiceProviderPtr m_pIServiceProvider;
	IDgnExtModSupStringsPtr m_pIDgnExtModSupStrings;
	IDgnSSvcInterpreterPtr m_pIDgnSSvcInterpreter;
	IDgnSRTrainingPtr m_pIDgnSRTraining;

	// the key for unregistering our engine sink (a SAPI thing)
	DWORD m_dwKey;

	// the name of the log file (or en empty string if not known).  We
	// assume that this will be less than the maximum path and file name
	// under Windows.
	char * m_pszLogFile;

	// this is a pointer to the function set with setBeginCallback; it is
	// NULL to avoid any callback
	PyObject *m_pBeginCallback;

	// this is a pointer to the function set with setChangeCallback; it is
	// NULL to avoid any callback
	PyObject *m_pChangeCallback;

	// we keep a hidden window in this thread to which we can send windows
	// messages 
	HWND m_hMsgWnd;

	// The CGramObj instances are in a linked list and the head of that list
	// is stored in the CDragonCode object.  This allows us to unload all
	// grammars when we call natDisconnect
	CGramObj * m_pFirstGramObj;

	// The CResObj instances are also in a linked list for the same reason.
	CResObj * m_pFirstResObj;

	// And also the CDictObj instances
	CDictObj * m_pFirstDictObj;

	// this is a pointer to the second thread where we can display messages
	CSecondThread * m_pSecdThrd;

	// we remember a pointer to the CDgnAppSupport class so we can handle
	// the reinitialization function
	CDgnAppSupport * m_pAppClass;

	// during initialization we restrict some function calls to avoid
	// deadlock
	BOOL m_bDuringInit;



	// during paused callback we restrict some function calls to avoid
	// deadlock
	BOOL m_bDuringPaused;

	// this is incremented everytime we enter a callback and decremented
	// when the callback returns
	BOOL m_nCallbackDepth;

	// we are not allowed to make a change callback when we are processing
	// another callback.  To get around this, we set a flag if there should
	// be a pending change callback
	DWORD m_dwPendingCallback;

	// in order to delay recognition while we process other results, we set
	// a flag (m_nPauseRecog).  If this flag is set when a new recognition
	// starts then we delay until that flag is cleared, remembering the
	// cookie we need to resume
	int m_nPauseRecog;
	QWORD m_deferredCookie;

	// this is a pointer to the Python thread state which we create so we
	// can restore the thread state during callbacks; will be nULL if we are
	// not supporting Python Thread safety
	PyThreadState * m_pThreadState;

	// this is a pointer to the function set with setTimerCallback; it is
	// NULL to avoid any callback
	PyObject * m_pTimerCallback;

	// when we have installed a window timer, this is the timer number.
	// Otherwise this will be 0
	int m_nTimer;

	// if the user set a training mode, we set this flag so we can turn off
	// the training mode when we exit
	int m_bSetTraining;

	// set when we have installed a tray icon
	BOOL m_bHasTrayIcon;
	PyObject *m_pTrayIconCallback;

	// This is what we call when we are ready to recume recognition
	void doPausedProcessing( QWORD dwCookie );
	
	// this is called when we shutdown or when we reload Python to release
	// all COM pointer which may be lost
	void releaseObjects();

	// used to test a wave file
	DWORD testFileName( const char * pszFileName );

	// this is the standard windows message loop except that we look for
	// a special exit message
	LPARAM messageLoop( UINT message, WPARAM wParam );

	// writes one line to the dragon.log file
 public:
	void logMessage( const char * pszText );
	void logCookie( const char * pszText, QWORD qCookie );


 protected:

	// subroutines of natConnect
	BOOL initGetSiteObject( IServiceProvider * & pIDgnSite );
	BOOL initSecondWindow();
	//
	// RW Added:
	//
	BOOL getINIFlags();
	BOOL setINIFlags();
	BOOL m_bWriteToDragonLog;
	BOOL m_bRememberWindowPosition;
	// the name of the INI config file (or en empty string if not known). 
	char * m_pszINIFile;
	// message window parameters
	int m_defWidth;
	int m_defHeight;
	int m_initTop;
	int m_initLeft;
	int m_initRight;
	int m_initBottom;
	int m_xSize;
	int m_ySize;
	//
	// End RW Added


	// this is a stack of the things we are looking for in a message loop
	CMessageStack * m_pMessageStack;
	void TriggerMessage( UINT message, WPARAM wParam, LPARAM lParam );
	BOOL IsMessageTriggered( UINT message, WPARAM wParam, LPARAM & lParam );

#ifdef INHOUSE
	INH_DRAGCODE_CLASS
#endif
};

#ifndef INIREADER_H
#define INIREADER_H
class CIniReader
{
public:
 CIniReader(char* szFileName); 
 int ReadInteger(char* szSection, char* szKey, int iDefaultValue);
 float ReadFloat(char* szSection, char* szKey, float fltDefaultValue);
 bool ReadBoolean(char* szSection, char* szKey, bool bolDefaultValue);
 char* ReadString(char* szSection, char* szKey, const char* szDefaultValue);
private:
  char m_szFileName[255];
};
#endif//INIREADER_H
