# Voice commands for OUTLOOK

#switchToFolder(folder) := {Ctrl+y}{Up_40}{Left}  # close "Archive Folders"
#                          Inbox{Right}           # open "Inbox"
#                          {Up_40} $folder {Enter};

#########Folder <folder> = switchToFolder($1);
#Move To <folder> = {Ctrl+x} switchToFolder($1) {Ctrl+v};

Mark [as] junk = {alt+h} Wait(100) "j" Wait(100) "b";

# just collapse subfolders of current account, navigate to given subfolder
(work=1|personal=5) inbox = {Ctrl+y} Wait(100) Repeat(6, {Left}{left}{up} Wait(100)) {Down_$1} {Right}{Down}{Right}{enter};
(Chris=1|review=2) inbox = {Ctrl+y} Wait(100) Repeat(6, {Left}{left}{up} Wait(100)) {Down_1} {Right}{Down} "M" {Right}{down_$1}{enter};

Flag That = {Ctrl+G}{Enter}; #{Ctrl+t(200) {Enter};
Clear Flag = {Ctrl+G}{Alt+e};

<folder> := Inbox | Drafts | Sent | Calendar | Contacts | Tasks;

include utilities.vch;

Microsoft Outlook:
  # collapse current folder and other open folders, left left up repeat
  # go all the way to the top of the list, down to either the first or
  # the last folder, collapse that current folder if expanded, expand again to make sure we are at
  # the top, open the first subfolder which should be "inbox"
  #  switch To (personal={Down_10}|work={Down_1}) folder = 
  #    {Ctrl+y} Repeat(6, {Left}{left}{up}) $1 {Right}{Down}{Right}{enter};
  #{Ctrl+y}{Left_10}{Up_10}$1{Left}{Right}{Down}{Right}{enter};
  switch To <folder> = {Ctrl+y}{Left}$1{Enter};
  find related (conversation=|sender={Down}) = {shift+f10} f $1 {enter};
  search <_anything> = {ctrl+e} $1 {enter} {Tab_3};
  New Message = {Ctrl+n};
  New Message to Contact = {Alt+a}m;
  Reply to (Message={Ctrl+r} | All={Ctrl+Shift+r}) = $1;
  Forward Message = {Ctrl+f};
  Get Mail = {Alt+t}e{Enter};  
  sort by (date=d|sender=f|flag=g) = {alt+v} ab $1 {alt+h}{esc}{esc};
  #Sort by Date   = touchNearEdge(ne,-3,8) ButtonClick();
  #Sort by Sender = touchNearEdge(nw,23,8);
  Final Message = {End};
  Search Messages = {Ctrl+Shift+f};
  Mark All Read = {Alt+e}e;
  Kill Line = {Del};
  Save Attachment 1..10 = {Alt+f}n{Down_$1}{Up}{Enter};
  Save Attachment All = {Alt+f}n{Up}{Enter};

Message:
  Kill Message = {Alt+F4} n;
  save to quick parts = {Alt} Wait(200) n Wait(200) q Wait(200) s;
Message (Plain Text):
  Reply Here = {Home}{Shift+End}{Del}{Enter_3}{Left_2};
  Send That = {Alt+f}e{Enter};
Message (HTML):
  Plain Text = {Alt+o}ty;
  Fix Return = {End}{Del}{Shift+Enter}{Right};
Message (Rich Text):
  Plain Text = {Alt+o}ty;
Select Names:
  (To=o | See See=c | Be See See=b) That = {Alt+$1}{Down};

Personal Folders:
  Calendar = {Alt+v}gc;
Calendar:
  View (Month=m | Work Week=r) = {Alt+$1};
Overdue:
  Dismiss = {Alt+d};

Contacts:
  Edit That = {Enter};
  Print Preview = {Alt+f}v;
  (Design|Edit) View = {Alt+v}vc;
  Edit   Email Address = {Ctrl+o}{Tab_17};
  Update Email Address = {Ctrl+o}{Tab_17}{Ctrl+v}{Alt+s};
  Delete Email Address = {Ctrl+o}{Tab_17}{Del}{Alt+s};
  Copy   Email Address = {Ctrl+o}{Tab_17}{Ctrl+c}{Esc};
  New Contact = {Ctrl+n} HeardWord(Category, Main) {Tab_3};

- Contact:
  (Use That | Save and Close) = {Alt+s};
  # Jump to input field (numbered in reverse order from big text box)
  #field(n) := touchNearEdge(sw,5,-5) {Shift+Tab_$n};
  Field ( Categories=24 | File As=18 | Business=16 | Home=14 | Mobile=10
        | Address=8 | Email=4 ) = touchNearEdge(sw,5,-5) {Shift+Tab_$1};
  Home Address = HeardWord(Field, Address)
                 "{Tab} {Down_2}{Enter}{Tab} {Shift+Tab_2}";
  Swap E-mail 2..3 = "{Shift+Tab} {Down $1}{Enter}{Tab}{Ctrl+c}"
                    "{Shift+Tab} {Down}{Enter}{Tab}{Left}{Ctrl+v}{Backspace 2}"
                    {Shift+Right}{Ctrl+x}
                    "{Shift+Tab} {Down $1}{Enter}{Tab}{Ctrl+v}"
                    "{Shift+Tab} {Down}{Enter}{Tab}";
  Use E-mail 2..3 = "{Shift+Tab} {Down $1}{Enter}{Tab}{Ctrl+x}"
                    "{Shift+Tab} {Down}{Enter}{Tab}{Ctrl+v}";

Print Preview:
  Close [That] = {Alt+c};
