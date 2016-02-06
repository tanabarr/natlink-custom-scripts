# Voice commands for skype
(contacts=1|recent=2) = {alt+$1};
(messages=3|add person=4|call person=5) = Repeat($1, {shift+tab});
text = Repeat(3, {tab});
login reset = {alt+s} Wait(200) "s" Wait(500) {tab} "cideric306" Wait(200) {enter};

