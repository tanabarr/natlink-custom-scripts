# Voice commands for vpxclient

(start=b|stop=e|suspend=z|reset=t|shutdown guest=d|reset guest=r|focus=g|close=X|new=n) VM = {ctrl+$1};
search the sphere = {ctrl+F};
open VM settings = {alt+n}v{down_4}{enter}; 
open VM consul = {alt+n}v{down_3}{enter}; 
escape from consul = Keys.SendInput({ctrl+alt});
#_hold}) Wait(100) {alt} Wait(100) Keys.SendInput({ctrl_release});
