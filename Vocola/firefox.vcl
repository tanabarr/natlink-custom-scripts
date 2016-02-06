# Voice commands for firefox
## Note: intuitive navigation and volume control for HTML 5 videos using arrow keys
# e.g.
(mute=down|unmute=up) = {ctrl+$1};

$set numbers 0;

close = {ctrl+w};
reload = {ctrl+f5};
(tools|options) = {Alt+t} Wait(100){o};
add-ons = {Alt+t} Wait(100){a};
firebug = {f12};
#debugging
(continue=8|step=11) = {f$1};
Caret browsing = {f7};

remove [all] cookies = {ctrl+shift+o};
private = {ctrl+shift+p};
history sidebar = {ctrl+alt+h};
history search = {alt+s}{down}{enter};
bookmark sidebar = {ctrl+b};

<n> := 0..9;
zoom (in=plus | out=minus) [<n>] = 
    When($2, Repeat($2, {Ctrl+$1} Wait(100)), Repeat(1, {Ctrl+$1} Wait(100)));
save = {Ctrl+s};
new tab = {Ctrl+t};
last = {Ctrl+T};
new window = {Ctrl+n};
next <n> = Repeat($1,  {Ctrl+tab});
previous <n> = Repeat($1,  {Ctrl+Shift+tab});
close = {Ctrl+w};
bookmark = {Ctrl+d};
reload={f5};
back page={backspace};
(Copy={Ctrl+c} | Paste={Ctrl+v} | Go="") (Address|URL) = {Alt+d} Wait(20) $1;
clear cash = {ctrl+shift+del};
developer (inspect=c|console=k|debug=s|network=q|browser=j|design=m) = {ctrl+shift+$1};
#mlb
links = {ctrl+'/'};
# macro to restart and resume session to Jenkins
restart Jenkins sessions = {alt+f4} Wait(100) {enter} Wait(200)
                           SendSystemKeys({win+r}) Wait(100) "firefox.exe" {enter}
                           Wait(1200) SendSystemKeys({win+t}) Wait(100) {up} {enter} 
                           Wait(5000) "26" Wait(1500) {enter} Wait(1000)
                           {alt+s} {down_2} {enter};
                           
resume previous session = Wait(100) {alt+s} {down_2} {enter};
                           
