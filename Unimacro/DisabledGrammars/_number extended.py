__version__ = "$Revision: 356 $, $Date: 2011-02-08 11:14:12 +0100 (di, 08 feb 2011) $, $Author: quintijn $"
# (unimacro - natlink macro wrapper/extensions)
# (c) copyright 2003 Quintijn Hoogenboom (quintijn@users.sourceforge.net)
#                    Ben Staniford (ben_staniford@users.sourceforge.net)
#                    Bart Jan van Os (bjvo@users.sourceforge.net)
#
# This file is part of a SourceForge project called "unimacro" see
# http://unimacro.SourceForge.net).
#
# "unimacro" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, see:
# http://www.gnu.org/licenses/gpl.txt
#
# "unimacro" is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; See the GNU General Public License details.
#
# "unimacro" makes use of another SourceForge project "natlink",
# which has the following copyright notice:
#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# _number.py 
#  written by: Quintijn Hoogenboom (QH softwaretraining & advies)
#  August 2003
# 
"""smart and reliable number dictation

the number part of the grammar was initially provided by Joel Gould in
his grammar "winspch.py it is changed a bit, but essentially all sorts of numbers can be
dictated with his grammar.

For real use in other grammars, copy the things from his grammar into another grammar. See
for example "_lines.py" and "firefox browsing.py".
BUT: first try if the logic of _number simple.py is enough. If not, study this grammar.

BTW when dictating numbers in excel (doing my bookkeeping), I use this grammar  (or the "number simple") all the time!

QH september 2013: rewriting of the functions, ruling out optional command words. The optional word "and" has been removed
            (now say "three hundred twenty" instead of "three hundred and twenty")

QH211203: English numbers require more work: thirty three can be recognised as "33" or
as "30", "3".

QH050104: standardised things, and put functions in natlinkutilsbj, so that
other grammars can invoke the number grammar more easily.
"""
from actions import doKeystroke as keystroke

natut = __import__('natlinkutils')
natqh = __import__('natlinkutilsqh')
natbj = __import__('natlinkutilsbj')
import iban  # special module for banknumber (European mainly I think)
import types 

# Note: lists number1to99 and number1to9 and n1-9 and n20-90 etc. are taken from function getNumberList in natlinkutilsbj

ancestor = natbj.IniGrammar
class ThisGrammar(ancestor):

    language = natqh.getLanguage()
    #Step 1, choose one of next three grammar rules:
    # the <integer> rule comes from these grammar rules
    number_rules = natbj.numberGrammarTill999[language] # hundreds, really up to 99999 (99 hundred 99).
    #number_rules = natbj.numberGrammarTill999999[language] # including thousands
    #number_rules = natbj.numberGrammar[language] #  including millions
    name = "number extended"
    # do not use "To" instead of "Through", because "To" sounds the same as "2"
    gramSpec = ["""
<testnumber1> exported = (number <number>)+;
<testnumber2> exported = number <integer> Through <integer>;
<pair> exported = Pair <number> And <number>;  
<number> = <integer> | Minus <integer> | <float> | Minus <float>;
"""]
    gramSpec.append("<banknumber> exported = IBAN {n00-99} {bankheader} <integer>;")
    gramSpec.append(number_rules)

#failed to get this working:
#<listtupleargument> exported = (Tuple|List|Argument) (Number <number> | (Variable|String) <dgndictation> | None)+;


    def gotBegin(self,moduleInfo):
        if self.checkForChanges:
            self.checkInifile()
  
    def initialize(self):
        if not self.language:
            print "no valid language in grammar "+__name__+" grammar not initialized"
            return
        self.load(self.gramSpec)
        # if switching on fillInstanceVariables also fill numbers lists like {n1-9} or {number1to99}
        self.switchOnOrOff() 

    def gotResultsInit(self, words, fullResults):
        # Step 2:
        # initialise the variables you want to collect the numbers in:
        # defining them here makes testing in gotResults easier
        self.number = ''  # for all the rules
        self.through = '' # only for testnumber2
        self.pair = ''    # only for the pair rule...
        self.minus = False
        self.ibanHeader = None # for banknumber
        self.ibanCheck =  None # for banknumber
        #self.listtupleargument = ''
        #self.Items = [] # for listtupleargumenthallo
        #print 'number: %s'% fullResults
        
    def gotResults_testnumber1(self, words, fullResults):
        # step 3: setting the number to wait for
        # because more numbers can be collected, the previous ones be collected first
        # if you expect only one number, this function can be skipped (but it is safe to call):
        self.collectNumber()
        result = self.hasCommon(words, 'number')
        if self.hasCommon(words, 'number'):
            if self.number:
                # flush previous number
                self.number =self.doMinus('number', 'minus') # convert to int
                self.outputNumber(self.number)
            self.waitForNumber('number')
        else:
            raise ValueError('invalid user input in grammar %s: %s'%(__name__, words))

    def gotResults_testnumber2(self, words, fullResults):
        # step 4 also: if more numbers are expected,
        # you have to collect the previous number before asking for the new
        self.collectNumber()
        # self.minus is not relevant here, as this rule is about integers only...
        # can ask for 'number' or for 'through':
        if self.hasCommon(words, 'number'):
            self.waitForNumber('number')
        elif self.hasCommon(words, 'through'):
            self.waitForNumber('through')
        else:
            raise NumberError, 'invalid user input in grammar %s: %s'%(__name__, words)

    def gotResults_pair(self, words, fullResults):
        # here a bit different logic for the place to collect the previous number.
        #
        self.pair = 'pair'
        if self.hasCommon(words, 'and'):
            self.collectNumber()
            self.number = self.doMinus('number', 'minus')
            self.waitForNumber('pair')
        else:
            self.waitForNumber('number')

    def gotResults_banknumber(self,words,fullResults):
        """get first 8 characters from bank name (list), rest from numbers grammar
        """
        self.ibanHeader = self.getFromInifile(words[-1], 'bankheader')
        self.ibanCheck =  "%.2d"% self.getNumberFromSpoken(words[-2])
        self.waitForNumber('number')

    def gotResults_number(self, words, fullResults):
        # step: when in this rule, the word Minus (or synonym or translation) has been spoken..
        self.minus = True


    def gotResults(self, words, fullResults):
        # step 5, in got results collect the number:
        self.collectNumber()

        if self.through:
            # only print in Messages window:
            res = 'collected number: %s, through: %s'%(self.number, self.through)
            #keystroke(res+'\n')
            print(res+'\n')
            
        elif self.pair:
            self.pair = self.doMinus('pair', 'minus')
            print "(%s, %s) "% (self.number, self.pair)
            
          
        #elif self.listtupleargument:
        #    print 'self.listtupleargument in gotResults: %s'% self.listtupleargument
        #    if self.number:
        #        self.number = self.doMinus('number', 'minus')
        #        self.Items.append(self.number)                    
        #
        #    if self.dictated:
        #        self.Items.append(''.join(self.dictated))
        #        self.dictated = None
        #
        #    result = repr(self.Items)
        #    print 'result: %s'% self.Items
        #    if self.listtupleargument == 'list':
        #        print 'list: %s'% result
        #    elif self.listtupleargument == 'tuple':
        #        result = repr(tuple(self.Items))
        #        print 'tuple: %s'% result
        #    else:
        #        result = repr(tuple(self.Items)).replace(', ', ',')
        #        result = result.replace(', ',',')
        #        print 'argument: %s'% result
        #
        elif self.ibanCheck and self.ibanHeader:
            try:
                result = Iban = iban.create_iban(self.ibanHeader[:2], self.ibanHeader[2:], self.number)
            except iban.IBANError, err:
                print 'invalid iban %s, %s (%s)'% (self.ibanHeader, self.number, err)
                return
            if result[2:4] == str(self.ibanCheck):
                keystroke(result)
            else:
                print 'invalid check: %s (%s) '% (self.ibanCheck, result)

        elif self.number:
            # last part if all others failed:
            self.number = self.doMinus('number', 'minus')
            self.outputNumber(self.number)

                      
    def outputNumber(self, number):
        if type(number) in [types.IntType, types.FloatType]:
            number = str(number)

        keystroke(number)
        prog = natqh.getProgName()
        if prog in ['iexplore', 'firefox', 'chrome', 'safari']:
            keystroke('{tab}')
        elif prog in ['natspeak']:
            keystroke('{enter}')
        elif prog in ['excel']:
            keystroke('{tab}')



    def doMinus(self, number, minus):
        """return  the minus version of number, is self.minus is set

        pass in the names of the number variable and the name of the minus variable.
        return the wanted number.        
        """
        Nstring = getattr(self, number)
        Nstring = Nstring.strip()
        Minus = getattr(self, minus)
        if not Nstring:
            setattr(self, minus, False)
            return ''

        if Minus:
            if Nstring.startswith('-'):
                Nstring = Nstring[1:]
            else:
                Nstring = '-'+Nstring
            setattr(self, minus, False)
        return Nstring

# standard stuff Joel (adapted for possible empty gramSpec, QH, unimacro)
thisGrammar = ThisGrammar()
if thisGrammar.gramSpec:
    thisGrammar.initialize()
else:
    thisGrammar = None

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None 