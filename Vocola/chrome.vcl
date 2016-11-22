# Voice commands for chrome
# chrome.vcl

include Unimacro.vch;
include keys.vch;

$set numbers 0;

<n> := 1..9;
zoom (in=plus | out=minus) [<n>] = 
    When($2, Repeat($2, {Ctrl+$1} Wait(100)), Repeat(1, {Ctrl+$1} Wait(100)));
save = {Ctrl+s};
new tab = {Ctrl+t};
restore last = {Ctrl+T};
new window = {Ctrl+n};
#(previous="+shift"|next="") 1 = {Ctrl$1+tab};
next <n> = Repeat($1,  {Ctrl+tab});
previous <n> = Repeat($1,  {Ctrl+Shift+tab});
switch tab <n> = {Ctrl + $1};
private = {Alt+e} Wait(10){i};
close = {Ctrl+w};
bookmark = {Ctrl+d};
tools = {Alt+e};
developer tools = {ctrl+shift+i};
reload={f5};
back page={backspace};
(Copy={Ctrl+c} | Paste={Ctrl+v} | Go="") (Address|URL) = {Alt+d} Wait(50) $1;
clear cash = {ctrl+shift+del};
tab to window = {shift+w};
Search <_anything>                          =  {Esc}"/" Wait(200) "\c$1";

# hppd atlassian wiki
insert wiki link = {ctrl+k};

# Vimium
text box = gi;
duplicate tab = yt;
search tabs = T;
next link = "]]";
previous link = "[[";
links = f;
visual mode = v;
visual line mode = V;
caret mode = c;
swap focus = o;
#address copy = y Wait(10){y};
#address go = {Alt+d};
copy links = yf;

# iml website navigation
<iml_urls> := (
 server="configure/server"|
 server one="configure/server/1"|
 server two="configure/server/2"|
 command="status"|
 volume="configure/volume"|
 management="configure/mgt"|
 filesystem="configure/filesystem"|
 filesystem one="configure/filesystem/detail/1"|
 filesystem create="configure/filesystem/create");

<iml_manager_addresses> := (
 local="127.0.0.1:8000"|
 cluster="10.14.81.222");

<iml_urls> <iml_manager_addresses> page = {alt+d} Wait(0) "https://$2/ui/$1" {enter};
<iml_urls> page = {alt+d} Wait(0) "https://127.0.0.1:8000/ui/$1" {enter};

format jason = "?format=json";

(server|
 volume|
 alert|
 command|
 host|
 filesystem|
 job) api = {alt+d} Wait(0)
    "https://127.0.0.1:8000/api/$1/?format=json" {enter}; 

# jenkins
login to Jenkins = {ctrl+t} Wait(200) {alt+d}
    "https://jenkins.lotus.hpdd.lab.intel.com:8080/login?from=/" Wait(200) {enter}
    Wait(12000) {enter};
#    Wait(14000) "tanabarr" {tab} Wait(200) "Chanch0306!" Wait(200) {enter};
Jenkins login = "f" Wait(200) "w" Wait(5000) "tanabarr" {tab} Wait(200) "Chanch0306!" Wait(200) {enter};
[view] full console = {alt+d} Wait(200) {right} "/consoleFull" {enter};

# gerrit login
login to get it = {tab} Wait(200) "f" Wait(200) "j";

