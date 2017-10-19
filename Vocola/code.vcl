# Voice commands for code
include vim.vch;
include UNIX_shell.vch;
include keys.vch;

window close = {ctrl+f4};
open interactive = {alt+enter};
command prompt =  {ctrl+"'"};
project view = {ctrl+shift+e};
search all commands = {ctrl+shift+p};
search all = {ctrl+p};
go to file = {ctrl+p};
next highlighted error = {f8};

replace normal = {ctrl+h};
find next = {f3};
comment line = {ctrl+k};

# Rich languages editing
Trigger suggestion = {Ctrl+Space};
Trigger parameter hints = {Ctrl+Shift+Space};
Format document = {Shift+Alt+F};
Format selection = {Ctrl+K}{Ctrl+F};
Go to Definition = {F12};
Peek Definition = {Alt+F12};
Open Definition to the side = {Ctrl+K}{F12};
Quick Fix = "{Ctrl+.}";
(Show References|goto usages) = {Shift+F12};
Rename Symbol = {F2};
Replace with next value = "{Ctrl+Shift+.}";
Replace with previous value = "{Ctrl+Shift+,}";
Trim trailing whitespace = {Ctrl+K}{Ctrl+X};

# Misc
open to the side = {ctrl+enter};
zoom (in="+"|out="-") = {ctrl+$1};
switch split (1|2|3) = {ctrl+$1};
close sidebar = {ctrl+b};
toggle problems = {ctrl+shift+m};
next 1..9 = Repeat($1, {ctrl+shift+tab} Wait(200));
previous 1 = {ctrl+tab};
