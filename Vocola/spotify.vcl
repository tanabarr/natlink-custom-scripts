# Voice commands for spotify

include Unimacro.vch;

Search bar		= {Ctrl+l};
Search for <_anything>	= {Ctrl+l} $1 {Enter};
#fullscreen = {Alt+v}f;
<next_back> := (next="Right" | back="Left");

<next_back> track = {Esc}{Ctrl+$1};
<next_back> browser = {Esc}{Alt+$1};
#When($1, {Ctrl+$1}, {Ctrl+Right});
(play | pause) =  " ";
volume (Up | Down | Mute=shift+Down) = {Ctrl+$1};
large artwork toggle = {alt+v}l;
close window = {alt+f4};

