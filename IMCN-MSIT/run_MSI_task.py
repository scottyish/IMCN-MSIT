from MSIclass import *
import datetime
import sys
import os
from os.path import join as opj

# define main function to call to run experiment
def main(initials, gend, age, session_nr, start_block, session_tr, simulate, scanner):

    this_dir = os.getcwd()
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    output_str = f'sub-{initials}_ses-{session_nr}_tr-{session_tr}_task-MSIT_{timestamp}'
    output_dir = opj(this_dir, 'data_MSIT')

    if simulate == 'y':
        settings_file = opj(this_dir, 'simulate_settings.yml')
    else: 
        settings_file = opj(this_dir, 'exp_settings.yml')

    # calls MSITsession from MSIclass script
    Msess = MSITsession(output_str=output_str, output_dir=output_dir, settings_file=settings_file,
                        subject_initials=initials, tr=session_tr, start_block=start_block,
                        gend=gend, age=age, session_nr=session_nr)
    
    # run MSITsession function from MSIclass, this runs the experiment 
    Msess.run()

if __name__ == '__main__':
    main()

    # Force python to quit (so scanner emulator also stops)
    core.quit()