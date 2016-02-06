/*
 Python Macro Language for Dragon NaturallySpeaking
	(c) Copyright 1999 by Joel Gould
	Portions (c) Copyright 1999 by Dragon Systems, Inc.

 secdthrd.cpp
	This file contains the code which handles the second thread used in the
	natlink module.  The second thread provised a dialog in which we display
	Python error messages

 April 25, 1999
	- packaged for external release

 March 3, 1999
	- initial version
*/


/*
 Modifications/Additions starting December 2011
	Marked up as "RW Added" or something similar throughout the code
	(c) Copyright by R�diger Wilke
*/


#include "stdafx.h"
#include "resource.h"
#include "SecdThrd.h"
#include <richedit.h>

// This is the message we send to the other thread to add text to the output
// window.  wParam = TRUE for error text, FALSE for normal text.  lParam is
// the pointer to a string to display.  The thread should delete the string
// when finished.
#define WM_SHOWTEXT (WM_USER+362)

// Send this message to the other thread to destroy the window and exit the
// thread.
#define WM_EXITTHREAD (WM_USER+363)

// The color for error messages
#define DARKRED RGB( 128, 0, 0 )

// RW Added: suppress deprecation warnings
//
#pragma warning( disable : 4996 )
//


//---------------------------------------------------------------------------
// Called when a message is sent to the dialog box.  Return FALSE to tell
// the dialog box default window message handler to process the message.

BOOL CALLBACK dialogProc( 
	HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam )
{
	// This is the threads copy of the CSecondThread class pointer. I
	// supposed that this should not really be global but stored in some
	// thread or windows storage instead. Oh, well.
	static CSecondThread * s_pSecdThrd = NULL;

	switch( msg )
	{
	 case WM_INITDIALOG:
		s_pSecdThrd = (CSecondThread *)lParam;
		ShowWindow( hWnd, SW_HIDE );
		return TRUE;

	 case WM_EXITTHREAD:
		DestroyWindow( hWnd );
		return TRUE;
		
	 case WM_DESTROY:
		 {
			// 
			// RW Added: get the INI file path, but keep local here
			//
			LPTSTR  strDLLPath1 = new TCHAR[_MAX_PATH];
			::GetModuleFileName((HINSTANCE)&__ImageBase, strDLLPath1, _MAX_PATH);
			TCHAR m_pszDLLPath[MAX_PATH];
			if ( strDLLPath1 )
			{
				int n = strlen(strDLLPath1);
				strncpy(m_pszDLLPath, strDLLPath1, n-11);
				m_pszDLLPath[n-11]='\0';
				strcat(m_pszDLLPath, "natlinkstatus.ini");
			}
			
			// get the current message window parameters and save to INI file

			RECT rc;
			char szValue[256];
			GetWindowRect(hWnd, &rc);
			LONG lBottom = rc.bottom;
			sprintf(szValue, "%i", lBottom);
			WritePrivateProfileString("WindowSettings", "Bottom", szValue, m_pszDLLPath);
			sprintf(szValue, "%i", rc.left);
			WritePrivateProfileString("WindowSettings", "Left", szValue, m_pszDLLPath);
			sprintf(szValue, "%i", rc.right);
			WritePrivateProfileString("WindowSettings", "Right", szValue, m_pszDLLPath);
			sprintf(szValue, "%i", rc.top);
			WritePrivateProfileString("WindowSettings", "Top", szValue, m_pszDLLPath);

			// End RW Added

			PostQuitMessage( 0 );
		 }

		return FALSE;

	 case WM_CLOSE:
		// do not really close, hide instead
		ShowWindow( hWnd, SW_HIDE );
		// also clear out the contents of the window
		SetDlgItemText( hWnd, IDC_RICHEDIT, "" );
		return TRUE;

	 case WM_COMMAND:
		if( s_pSecdThrd && s_pSecdThrd->getMsgWnd() )
		{
			PostMessage( s_pSecdThrd->getMsgWnd(), msg, wParam, lParam );
		}
		return TRUE;

	 case WM_SHOWTEXT:
		{
			char * pszText = (char *)lParam;

			ShowWindow( hWnd, SW_SHOW );
			
			CHARFORMAT chForm;
			chForm.cbSize = sizeof(chForm);
			chForm.dwMask = CFM_COLOR;
			chForm.crTextColor =
				wParam ? DARKRED : GetSysColor( COLOR_WINDOWTEXT );
			chForm.dwEffects = 0;
						
			HWND hEdit = GetDlgItem( hWnd, IDC_RICHEDIT );
			SendMessage( hEdit, EM_SETSEL, 0x7FFF, 0x7FFF );
			SendMessage( hEdit, EM_SETCHARFORMAT, SCF_SELECTION, (LPARAM) &chForm );
			SendMessage( hEdit, EM_REPLACESEL, FALSE, (LPARAM)pszText );
			SendMessage( hEdit, EM_SETSEL, 0x7FFF, 0x7FFF );
			SendMessage( hEdit, EM_SCROLLCARET, 0, 0 );
			
			delete pszText;
		}
		return TRUE;

	 // RW Added: track resizing of the window and call repaint
	 //
	 case WM_SIZE:
		 {
			 HWND hEdit = GetDlgItem( hWnd, IDC_RICHEDIT );
			 MoveWindow(hEdit, 0, 0,
				 LOWORD(lParam),        // width of client area 
				 HIWORD(lParam),        // height of client area 
				 TRUE);					// repaint window
		 }
		 return TRUE;
	 // End RW Added
		
	 default:
		return FALSE;
	}
}

//---------------------------------------------------------------------------
// This is the main routine which the thread runs.  It contains a windows
// message loop and will not return until the thread returns.

DWORD CALLBACK threadMain( void * pArg )
{
	CSecondThread * pThis = (CSecondThread *)pArg;

	// create a dialog box to display the messages

	HINSTANCE hInstance = _Module.GetModuleInstance();

	HWND hWnd = CreateDialogParam(
		hInstance,						// instance handle
		MAKEINTRESOURCE( IDD_STDOUT ), 	// dialog box template
		NULL,							// parent window
		dialogProc,						// dialog box window proc
		(LPARAM)pThis );				// parameter to pass
	assert( hWnd );

	pThis->setOutWnd( hWnd );
	pThis->signalEvent();
	
	if( hWnd == NULL )
	{
		return 1;
	}
	
	// enter a Windows message loop

	MSG msg;
	while( GetMessage( &msg, NULL, NULL, NULL ) )
	{
		if( !IsDialogMessage( hWnd, &msg ) )
		{
			TranslateMessage( &msg );
			DispatchMessage( &msg );
		}
	}

	return 0;
}

//---------------------------------------------------------------------------

CSecondThread::CSecondThread()
{
	// create the thread we use to display messages; we use an event to make
	// sure that the thread has started before continuing

	m_hEvent = CreateEvent(
		NULL,	// security options
		TRUE,	// manual reset
		FALSE,	// not signaled
		NULL );	// name

	DWORD dwId;
	m_hThread = CreateThread(
		NULL,			// security (use default)
		0, 				// stack size (use default)
		threadMain,		// thread function
		(void *)this,	// argument for thread
		0,				// creation flags
		&dwId );		// address for returned thread ID
	assert( m_hThread != NULL );

	WaitForSingleObject( m_hEvent, 1000 );
	CloseHandle( m_hEvent );
	m_hEvent = NULL;
}

//---------------------------------------------------------------------------

CSecondThread::~CSecondThread()
{
	// terminate the output window then wait for the thread to terminate

	if( m_hOutWnd )
	{
		PostMessage( m_hOutWnd, WM_EXITTHREAD, 0, 0 );
		m_hOutWnd = NULL;
	}
	if( m_hThread != NULL )
	{
		WaitForSingleObject( m_hThread, 1000 /*ms*/ );
		m_hThread = NULL;
	}
}

//---------------------------------------------------------------------------

void CSecondThread::displayText( const char * pszText, BOOL bError )
{
	if( m_hOutWnd )
	{
		char * pszCopy = _strdup( pszText );
		PostMessage( m_hOutWnd, WM_SHOWTEXT, bError, (LPARAM)pszCopy );
	}
}
