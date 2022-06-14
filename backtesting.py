from ia import *
from lucroCalc import calc
import winsound
import os
from champs2 import Vitoriosos
from neural import ia, strategy, calc, calculation, delnone

win = Vitoriosos[-1]

grup = '10300'


df = blockx(grup)
#df = df[:-480]
#tecnicals(df)

log = open(doc, 'a')
log.write("{}\n".format(TRADE_SYMBOL))
log.close()

p = []

for i in range(2 , len(df.index)):
    new_df = df[:i]

    auxp = p
    
    if i == 2:
        auxp = [False]

    v = auxp[-1]
    
    cont = 0
    if not v:
        auxp = []
    if v:
        for k in p[::-1]:
            if not k:
                auxp = p[-cont :]
            cont = cont + 1
    
    out = strat(win,new_df,auxp)

    p.append(out)

print(df)

frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)



