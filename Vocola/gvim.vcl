# Voice commands for gvim

#include Unimacro.vch;
#include keys.vch;
include vim.vch;

backspace = {backspace};

File Open = {Alt+f}{Down_3}{enter} Wait(100) {Shift+Tab} Wait(700) {Shift+Tab};
file save as = {Alt+f}{a}{enter};
file save = {Alt+f}{s};
#Directory View = {Shift+Tab};

