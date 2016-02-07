
# Voice commands for EXPLORER

### View

Refresh [View] = {Alt+v}r;
#(Show|View) (Details=d | List=l) = {Alt+v} $2;
<view_mode> := (Extra Large=x | Large=r | Medium=m | List=l | Details=d);
View Mode <view_mode> = {Alt+v}$1;
Search = {Ctrl+e};
(Copy={Ctrl+c} | Paste={Ctrl+v} | Go="") Address = {Alt+d} Wait(20) $1;
#Left Side  = {Alt+d}{Tab_2}{Left};
#Right Side = {Alt+d}{Shift+Tab}{Left};
Go (Back=Left | Forward=Right) = SendSystemKeys({Alt+$1});
Go (Back=Left | Forward=Right) 1..10 = SendSystemKeys({Alt+$1_$2});
(Copy={Ctrl+c} | Paste={Ctrl+v} | Go="") (Address|URL) = {Alt+d} $1;

### Folders
#include folders.vch;

#Folder <folder> = {Alt+d} $1 {Enter}{Tab_2} SendSystemKeys({Alt+NumKey+});
#Search <folder> = {Ctrl+e}{Alt+l} $1 {Alt+m};

New Folder = {Alt+f}wf;
Folders = {Alt+v}eo;
Open Folder = {Alt+f}{Enter};  # after a search
Expand That   = SendSystemKeys({Alt+NumKey+});
Collapse That = SendSystemKeys({Alt+NumKey-});
Share That = {Alt+f}r Wait(1000) {Tab_5}{Right_2}{Alt+s}{Enter};

### Files

Copy Filename = {Alt+f}m{Ctrl+c}{Alt+d}{Right}\{Ctrl+v}
                {Home}{Shift+End}{Ctrl+c}{Esc};
Copy Folder Name = {Alt+d}{Ctrl+c}{Esc};
Copy Leaf Name = {Alt+f}m{Ctrl+c}{Esc};

new text Document = {Alt+f}wt;
Duplicate That = {Ctrl+c}{Left}{Ctrl+v}c;
Rename That = {F2};
Paste Here = ButtonClick(1,1) {Ctrl+v};

(Show|Edit) Properties = {Alt+f}r;
[Toggle] Read Only = {Alt+f}r Wait(2000) {Alt+r}{Enter};

### Misc extra

open with = {shift+f10} Wait(20) h;
(open|edit) with vim = {shift+f10} Wait(20) v;
file edit = {Alt+f}e;
file options = {Alt+f};
