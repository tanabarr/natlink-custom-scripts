# Voice commands for wlmail

include Unimacro.vch;

move to folder = {Alt+e}m;
move to junk folder = {Alt+Ctrl+j};
#Ctrl+Shift}v;
sort with date = {Alt}vb Wait(11) {Down}{Enter};
sort with flag = {Alt}vb Wait(11) {Down_6}{Enter};
flag = {Alt}aa;
Save Attachment [All] = {Alt+f}v Wait(100) {Tab_2}{Enter};
#Save Attachment All = {Alt+f}v{Up}{Enter};

add contact = {enter} WaitForWindow("") {Alt+t}"ds"{enter}{Alt+f4};
