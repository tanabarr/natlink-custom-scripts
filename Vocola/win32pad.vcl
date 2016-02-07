###
### Win32Pad voice commands, part I
###
### Version 0.2.1: word boundaries are Win32Pad's
###

include win32pad.vch;

$set MaximumCommands 4;  # allow up to four of these commands per utterance


##
## Commands that may optionally take modifiers like shift & control:
##
##     Many useful editing actions in Windows are just simple keyboard
## chords (e.g., {ctrl+shift+right}), possibly repeated some number of
## times.
##
## Often adding shift   to a key means extend/create selection,
##   and adding control to a key means move by a higher unit (e.g., by
##         words instead of characters).
##

<modifiers> := (
       shift           = shift+
     | control         = ctrl+
     | control shift   = ctrl+shift+
     | shift   control = ctrl+shift+
);

  # chords for which repetition doesn't make sense:
<unrepeatable_chord> := (
     # "end" misrecognized too frequently so use first/last instead:
       (first      |start-of-line) = home
     | (last       |end-of-line)   = end

     | (top-of-file|top-of-buffer) = ctrl+home
     | (end-of-file|end-of-buffer) = ctrl+end
);
            <unrepeatable_chord> = {  $1};
<modifiers> <unrepeatable_chord> = {$1$2};

<chord> := (
        # moving by single characters:
       soar = up          # "up" by itself sounds too much like noise
     | down | left | right

        # erasing by single characters:
     | back = backspace | erase = del

     | tab     # moving by fields (add shift for move back a field)
     | space   # moving by screenfuls
     | enter   # special case (e.g., pagers)

        # moving by screenfuls:
     | page up = PgUp | page down = PgDn

        # moving by words:
     | flee = ctrl+left | start-word = ctrl+right
);
            <chord>        = {  $1   };
            <chord> 1..100 = {  $1_$2};
<modifiers> <chord>        = {$1$2   };
<modifiers> <chord> 1..100 = {$1$2_$3};


##
## Simple cutting and copying actions:
##

(copy  that | copy region)    = {ctrl+c};
(cut   that | destroy region) = {ctrl+x};
(paste that | yank)           = {ctrl+v};


<kill_word> := ( kill = ctrl+shift+left | pull-word = ctrl+shift+right );

<kill_word>        = {$1   }{ctrl+x};
<kill_word> 1..100 = {$1_$2}{ctrl+x};


<direction> := ( start = {shift+home} | rest = {shift+end}{shift+left} );

copy      start       = {shift+home}            {ctrl+c} {right};
copy      rest        = {shift+end}{shift+left} {ctrl+c} {left};

highlight <direction> = $1;
destroy   <direction> = $1 {ctrl+x};


##
## Navigating by line numbers:
##

toggle line numbers = {ctrl+l};

<r> := 0..99;

# Move to start of on-screen line whose line number's last 2 digits are given #
#
# (only works if less than 50 lines fit per screen)
(go | row | line) <r> = LineMod($2);


##
## Moving by occurrences of text:
##

_Leap(direction, set_target, times) :=
        {shift+right}             # fake selecting our target at point
        {ctrl+f}                  # bring up find dialog box
        {alt+c}- {alt+w}-         # options: not whole words, case insensitive
        {alt+$direction}          # set direction to find
        {alt+n} $set_target       # set target for find
        Repeat($times,
          {enter}                 # do a find (may produce an error dialog box)
          {alt+w}{space} {alt+w}- # dismiss error dialog box if any
        )
        {esc}                     # dismiss find dialog box
        {left}                    # exit selection, leaving point at start of
        ;                         #   target or original if target not found

<leap>  := ( leap = "d" | retreat = "u" );
<count> := ( first = 1 | second = 2 | third = 3 | fourth = 4 );

<leap>               <printable> = _Leap($1, $2, 1 );
<leap> after         <printable> = _Leap($1, $2, 1 ) {right};
<leap>       <count> <printable> = _Leap($1, $3, $2);
<leap> after <count> <printable> = _Leap($1, $3, $2) {right};


advance  <_anything> = _Leap(d, $1, 1);
fallback <_anything> = _Leap(u, $1, 1);


##
## Inserting text:
##

key     <printable> = $1;  # any printable character
dictate <_anything> = $1;  # arbitrary text (unformatted)


##
## Changing words:
##

ChangeWord(action, count) :=
    {ctrl+shift+right_$count} {ctrl+c}
    Clipboard.Set( EvalTemplate("%s.$action()", Clipboard.Get()) ) {ctrl+v};

<change> := ( lower-a-word = lower
            | upper-a-word = upper
            | cap-a-word   = title
            );

<change>       = ChangeWord($1, 1 );
<change> 2..20 = ChangeWord($1, $2);


##
## Miscellaneous:
##

escape      = {esc};

undo [that] = {ctrl+z};
redo [that] = {ctrl+shift+z};


##
## Menu accelerators | Emacs name:
##

(file open     |find file)     = {ctrl+o} WaitForWindow("Open")
                                 {tab}{alt+down}{end}{tab}{alt+n}; # all files


([file] save as|write file)    = {ctrl+shift+s};
(file save     |save file)     = {ctrl+s};


new file                       = {ctrl+n};
new instance                   = {ctrl+shift+n};
please (reload |revert buffer) = {ctrl+r};

insert file                    = {ctrl+i};
search and replace             = {ctrl+h};

word wrap mode                 = {ctrl+w};



##
## All printable characters in ASCII order with optional short names:
##

<printable> := (
       space             = " "
     |  !  | bang        =  !
     | '"' | quote       = '"'
     | "#" | pound       = "#"
     | "$" | dollar      = "\$"
     |  %  | percent     =  %
     |  &
     | "'" | apostrophe  = "'" | single = "'"
     | "(" | paren       = "("
     | ")" | close paren = ")"
     |  *  | asterisk    =  *  | star = *
     |  +  | plus        =  +
     | ","
     |  -  | minus       =  -
     |  .  | dot         =  .
     |  /

          # digits, spelled-out to work around DNS 11 bug with <_anything>:
     | zero=0 | one=1   | two=2   | three=3 | four=4 | five=5
     | six=6  | seven=7 | eight=8 | nine=9

     | ":"
     | ";" | semi       = ";"
     | "<" | bend       = "<"
     | "=" | equal      = "=" | equals = "="
     | ">" | close bend = ">"
     |  ?  | question   =  ?
     |  @

     | big Alpha    = A
     | big Bravo    = B
     | big Charlie  = C
     | big Delta    = D
     | big echo     = E
     | big foxtrot  = F
     | big golf     = G
     | big Hotel    = H
     | big India    = I
     | big Juliett  = J
     | big kilo     = K
     | big Lima     = L
     | big Mike     = M
     | big November = N
     | big Oscar    = O
     | big Papa     = P
     | big Quebec   = Q
     | big Romeo    = R
     | big Sierra   = S
     | big tango    = T
     | big uniform  = U
     | big Victor   = V
     | big whiskey  = W
     | big x-ray    = X
     | big Yankee   = Y
     | big Zulu     = Z

     | "[" | bracket       = "["
     |       backslash     = "\"
     | "]" | close bracket = "]"
     |  ^
     |  _
     |  `

     | Alpha    = a
     | Bravo    = b
     | Charlie  = c
     | Delta    = d
     | echo     = e
     | foxtrot  = f
     | golf     = g
     | Hotel    = h
     | India    = i
     | Juliett  = j
     | kilo     = k
     | Lima     = l
     | Mike     = m
     | November = n
     | Oscar    = o
     | Papa     = p
     | Quebec   = q
     | Romeo    = r
     | Sierra   = s
     | tango    = t
     | uniform  = u
     | Victor   = v
     | whiskey  = w
     | x-ray    = x
     | Yankee   = y
     | Zulu     = z

     | "{" = "{{}" | brace        = "{{}"  # SendDragonKeys syntax for {
     | "|"         | vertical bar = "|" | bar = "|"
     | "}"         | close brace  = "}"
     | "~"
);
