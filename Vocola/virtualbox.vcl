# Voice commands for virtualbox
include vim.vch;
include vim_plugins.vch;
include screen.vch;
include UNIX_shell.vch;

# Ubuntu specific commands
package (manager=|install|remove|update|upgrade) = "sudo apt-get $1 ";
find package = "sudo apt-cache search ";

(add=a|pause=p|reset=t|log=l|save=v|clone=o|remove=r|stop=f|suspend=v|shutdown=h|new=n) VM = {ctrl+$1};
open VM settings = {ctrl+s};
(start|show|open) VM = {alt+m}{down_6}{enter}; 
start headless = {alt+m}{down_6}{right}{down}{enter}; 
select [a] VM = {alt+m}{esc}{esc}{tab}{down}; 
VM dialogue (settings=s|shutdown=q) = {alt+$1};
new snapshot = {ctrl+shift+s};

ubuntu (minimise=f9|maximise=f10) = {alt+$1};
#escape from consul = Keys.SendInput({ctrl+alt});
#_hold}) Wait(100) {alt} Wait(100) Keys.SendInput({ctrl_release});

