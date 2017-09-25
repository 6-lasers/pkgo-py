# pkgo-py
A set of Python Pokemon Go tools.

## ivcalc.py
Usage: ivcalc.py \<input.txt\>

Frontend for for the appraisal library, which is capable of estimating Pokemon level and IVs from the visible stats, similar to most IV calculators. Takes a text file containing lines matching the following format:

`<species> <cp> <hp> <power up cost (in 100s)> <overall appraisal> <highest stat appraisal> <highest stat type> <(optional) hatched/powered>`

## cpcalc.py
Usage: cpcalc.py \<input.txt\>

Frontend for the CP calculation library. Given a Pokemon species, target level, and IVs, calculates its potential CP. Similar to Gamepress' CP calculator, but does not calculate power-up cost (see calcCost.py). Takes a text file containing lines matching the following format:

`<level> <species> <STA IV> <ATK IV> <DEF IV>`

## calcCost.py
Usage: calcCost.py \<start level\> \<end level\>

Similar to Gamepress' CP calculator, calculates the stardust and candy cost associated with powering up a Pokemon from a given start level to a target level.

## catchCalc.py
Usage: catchCalc.py \<species name or catch rate\> \<Pokemon level\> \<throw bonus\> \<ball type\> \<berry type\> \<curve ball\> \<medal type\> \<ball count\> \<allow flee\>

Similar to Gamepress' catch calculator and raid catch calculator, determines the catch chances of a given Pokemon. If *allow flee* is True, behaves like the catch calculator--otherwise, behaves like the raid catch calculator.

## pinap.py
Usage: pinap.py \<species name or catch rate\> \<Pokemon level\> \<throw bonus\> \<curve ball\> \<medal type\> \<ball count\> \<will transfer\>

Given a raid scenario, determine on which ball you should switch to throwing Golden Razz in order to maximize your expected candy returns.
