# Voice commands for vlc

include Unimacro.vch;
<forward_back> := (forward="Right" | back="Left");
<adjust_amount> := (tiny="Shift" | small="Alt" | medium="Ctrl" | large="Ctrl+Alt");

<forward_back> <adjust_amount> = When($2, {$2+$1}, {Ctrl+$1});
fullscreen = {Alt+v}f;
toggle subtitles = V;
toggle sound = M;
restart video = P;
change zoom = Z;
show the time = T;
GOTO time = {Ctrl+T};
(play | pause) =  " ";
volume (Up | Down) = {Ctrl+$1};
