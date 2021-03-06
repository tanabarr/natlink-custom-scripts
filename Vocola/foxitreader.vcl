## Voice commands for foxit reader
#
#include Unimacro.vch;
<n> := 0..9;
recent files = {Alt+f}r;
zoom in [<n>] = When($1, Repeat($1, {Ctrl+"="}),  Repeat(1, {Ctrl+"="}));
zoom out [<n>] = When($1, Repeat($1, {Ctrl+minus}),  Repeat(1, {Ctrl+minus}));
#zoom [one] hundred = {Ctrl+1};
#zoom [whole | full] page = {Ctrl+2};
#zoom [page] width = {Ctrl+3};
#;
#"find <text>":              Key("{Ctrl+f}") + Text("%(text)s");
#+ Key("f3"),;
#find next = f3;
#;
go to page [<n> [<n> [<n>]]] = {Ctrl+g} Wait(100) When($1,$1$2$3{enter}); #When($1, "$1$2$3"{enter}, ""));
#;
#print file = {Ctrl+p};
#print setup = a-f, r;
(two page=4|reading=o) mode = {esc}{esc}{alt}{v}{$1};
#reading mode = {alt}{v}; #{$1};
#two page mode = {alt+v}; #{$1};
#reading mode = {Ctrl+H};
previous page = {Ctrl+pgup};
## awkward method of switching between bookmark view and reading;
## pane. creates new bookmark, delete it,then can navigate to;
## bookmark.when wanting to return to Reading window, create and/or;
## focuses start tab. Then switch to tab next (assume is only one tab;
navigation window = {Ctrl+b}{enter}{del};
reading window = Repeat(2, {Ctrl+Alt+s});
close navigation window = {f4};
next = {Ctrl+tab};
previous = {ctrl+shift+tab};
close = {Ctrl+w};
