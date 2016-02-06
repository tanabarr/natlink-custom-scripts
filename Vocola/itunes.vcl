# Voice commands for itunes

include Unimacro.vch;

Pause = " ";
Play = " ";
<functions_arrow> := (Next=Right | Previous=Left | Increase=Up | Decrease=Down);
<functions_arrow> = {Ctrl+$1};
podcast view = {Esc}{Tab_7}{Enter}{Down_2}{Enter} Repeat(6,{Shift+Tab});
right side = {Tab_7}{Down};
left side =  Repeat(7,{Shift+Tab}){Down};
current podcast = {Ctrl+l};

