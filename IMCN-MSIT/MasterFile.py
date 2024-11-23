""" master file to run MSIT and stop signal tasks

initials = 'practice' = run practice tasks only
initials = 666 = run in debug mode
initials = odd number = run MSIT first
initials = even number = run SST first
task = b = run both tasks
task = m = run msit only
task = s = run sst only 
"""

from psychopy import core
import run_MSI_task
import glob
import os, sys
import numpy as np
import datetime
import re

# Kill all background processes (macOS only)
try:
    import appnope
    appnope.nope()
except:
    pass

# Set nice to -20: extremely high PID priority
# new_nice = -20
# sysErr = os.system("sudo renice -n %s %s" % (new_nice, os.getpid()))
# if sysErr:
#     print('Warning: Failed to renice, probably you arent authorized as superuser')
    
# Ask for subject number
initials = input("Subject number: ")

# if initials == '444':
#     session_tr = 2.0
# elif initials == '555':
#     session_tr = 1.6
# elif initials == '666': # 
#     session_tr = 1.4
# elif initials == '888': # 
#     session_tr = 1.4
# elif initials == '999': # 
#     session_tr = 1.4
session_tr = 1.4

prac_task = start_block = simulate = ''
while prac_task not in ['y','n']:
    prac_task = input("Do you want to run the practice task only? ('y' or 'n') ")

if prac_task == 'y':
    start_block = 1
    simulate = 'y'

elif prac_task == 'n':
    while start_block not in ['1','2']:
        start_block = input("What block do you want to start at? (1, or 2) ")

    simulate = 'n'
    #while simulate not in ['y','n']:
    #    simulate = input("Would you like to simulate scanner pulses? ('y' or 'n') ")

if simulate == 'y':
    scanner = 'n'
elif simulate == 'n':
    scanner = 'y'

session_nr = 1
gend = 'na'
age = 'na'
#prac_task = 'n'
#start_block = 1
#simulate = 'n'
#scanner = 'n'
#prac_task = input('Is this the practice task?: (y or n)')

if prac_task == 'y':
    # run the practice task with simulated pulses
    run_MSI_task.main(initials='p'+str(initials).zfill(3), session_nr=session_nr, start_block=start_block, simulate='y', session_tr=session_tr, scanner=scanner, gend=gend, age=age)

else:
    # run normal SST session without simulated pulses
    run_MSI_task.main(initials=str(initials).zfill(3), session_nr=session_nr, start_block=start_block, simulate=simulate, session_tr=session_tr, scanner=scanner, gend=gend, age=age)

# win.close()
core.quit()