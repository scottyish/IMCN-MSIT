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





### OLD

# # Ask for subject number
# initials = input("Subject number (444 for 4 trs, 555 for 5 trs): ")
# #initials = '555'
# if initials == '444':
#     session_tr = 2.0
# elif initials == '555':
#     session_tr = 1.6
# #session_tr = 1.6
# start_block = input("What block do you want to start at? ")
# prac_task = 'n'
# simulate = 'n'
# scanner = 'n'
# gend = 'na'
# age = 'na'
# session_nr = 1
# #start_block = 1

# #prac_task = input('Is this the practice task?: (y or n)')

# if prac_task == 'y':
#     # run the practice task with simulated pulses
#     run_MSI_task.main(initials='p111', session_nr=session_nr, start_block=start_block, simulate='y', session_tr=session_tr, scanner=scanner, gend=gend, age=age)

# else:
#     # run normal SST session without simulated pulses
#     run_MSI_task.main(initials=str(initials).zfill(3), session_nr=session_nr, start_block=start_block, simulate=simulate, session_tr=session_tr, scanner=scanner, gend=gend, age=age)

# # win.close()
# core.quit()

### OLD

# # Ask for subject number
# initials = input('Your initials/subject number: ')

# # if practice session, just ask what task(s) to run
# if initials.startswith('p'):
#     start_block = 1
#     gend = 'na'
#     age = 'na'
#     task = ''
#     prac_task = 'y'

#     while task not in ['m','M','S','s','b','B']:
#         task = input('Which task(s) do you want? (b, m or s): ')
    
# # if youw ant to quickly test if all blocks run with only 5 trials each    
# elif initials == '666':
#     start_block = 1
#     task = ''
#     prac_task = ''
#     gend = 'na'
#     age = 1

#     while task not in ['m','M','S','s','b','B']:
#         task = input('Which task(s) do you want? (b, m or s): ')
    
#     while prac_task not in ['y','Y','n','N']:
#         prac_task = input('Do you want to run the practice tasks? (y or n): ')

# # If real session, ask for input 
# else:
#     task = ''
#     prac_task = ''
#     gend = ''
#     age = ''

#     start_block = int(input('At which block do you want to start? NB: 1 is the first block! '))
#     if start_block > 1:
#         # check if previous stairs exist
#         now = datetime.datetime.now()
#         opfn = now.strftime("%Y-%m-%d")
#         expected_filename = initials + '_' + str(session_tr) + '_' + opfn
#         fns = glob.glob('./data/' + expected_filename + '_*_staircases.pkl')
#         fns.sort()
#         if len(fns) == 0:
#             input('Could not find previous stairs for this subject today... Enter any key to verify you want '
#                     'to make new staircases. ')
#         elif len(fns) == 1:
#             print(('Found previous staircase file: %s' % fns[0]))
#         elif len(fns) > 1:
#             print('Found multiple staircase files. Please remove the unwanted ones, otherwise I cannot run.')
#             print(fns)
#             core.quit()
        
#     while task not in ['m','M','S','s','b','B']:
#         task = input('Which task(s) do you want? (b, m or s): ')

#     while prac_task not in ['y','Y','n','N']:
#         prac_task = input('Do you want to run the practice tasks? (y or n): ')

#     while gend not in ['m','f','na']:
#         gend = input('Gender: ')

#     age = input('Age of participant: ')

# # If participant number inputted, work out if odd or even, then choose task order
# # run practice session of the tasks first if prac_task == 'y'
# if task in ['b','B']:
#     try:
#         val = int(initials)              
#         if val%2 == 0:

#             if prac_task in ['y', 'Y']:
#                 # run practice stop-signal session first if required
#                 initials = 'p' + str(initials).zfill(3)
#                 run_stop_task.main(initials=initials, start_block=start_block, gend=gend, age=age)

#             # run normal stop-signal session
#             initials = str(val).zfill(3)
#             run_stop_task.main(initials=initials, start_block=start_block, gend=gend, age=age)

#             if prac_task in ['y', 'Y']:        
#                 # again, run practice MSIT session first if required
#                 initials = 'p' + str(initials).zfill(3)
#                 run_MSI_task.main(initials=initials, gend=gend, age=age)
        
#             # then run normal MSIT session
#             initials = str(val).zfill(3)
#             run_MSI_task.main(initials=initials, gend=gend, age=age)

#         elif val%2 == 1:

#             if prac_task in ['y', 'Y']:        
#                 # run practice MSIT session first
#                 initials = 'practice' + str(initials).zfill(3)
#                 run_MSI_task.main(initials=initials, gend=gend, age=age)
        
#             # then run normal MSIT session
#             initials = str(val).zfill(3)
#             run_MSI_task.main(initials=initials, gend=gend, age=age)

#             if prac_task in ['y', 'Y']:
#                 # again, run practice SST session first
#                 initials = 'practice' + str(initials).zfill(3)
#                 run_stop_task.main(initials=initials, start_block=start_block, gend=gend, age=age)

#             # run normal SST session
#             initials = str(val).zfill(3)
#             run_stop_task.main(initials=initials, start_block=start_block, gend=gend, age=age)

#     # if initials == e.g. 'p23', then just run practice sessions (MSIT first)
#     except ValueError:  

#         val = int(re.split('(\d+)',initials)[1]) # split 'p' from subject number

#         if val%2 == 0: # practice MSIT first
#             # run MSIT practice
#             run_MSI_task.main(initials=initials, gend=gend, age=age)
#             # Run SST practice
#             run_stop_task.main(initials=initials, scanner=scanner, gend=gend, age=age)
#         elif val%2 == 1: # practice SST first
#             # Run SST practice
#             run_stop_task.main(initials=initials, start_block=start_block, gend=gend, age=age)    
#             # run MSIT practice
#             run_MSI_task.main(initials=initials, gend=gend, age=age)

# elif task in ['m', 'M']:
    
#     if prac_task in ['y', 'Y']:
#         # run practice MSIT session first
#         prac_init = 'p' + str(initials).zfill(3)
#         run_MSI_task.main(initials=prac_init, gend=gend, age=age)

#     # then run normal MSIT session
#     run_MSI_task.main(initials=str(initials).zfill(3), gend=gend, age=age)
    
# elif task in ['s', 'S']:
    
#     if prac_task in ['y', 'Y']:
#         # run practice SST session first
#         prac_init = 'p' + str(initials).zfill(3)
#         run_stop_task.main(initials=prac_init, start_block=start_block, gend=gend, age=age)

#     # run normal SST session
#     run_stop_task.main(initials=str(initials).zfill(3), start_block=start_block, gend=gend, age=age)

# # win.close()
# core.quit()