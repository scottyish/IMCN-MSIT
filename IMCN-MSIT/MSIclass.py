from exptools2.core import Session
from MSIstim import MSIstimulus, FixationCircle, FeedbackCorrect, FeedbackWrong, FeedbackSlow, FeedbackQuick, FeedbackVerySlow
from MSItrial import MSITRIAL, exp_instructions, OperatorScreen 
from psychopy import visual, data
from psychopy import core
import datetime
import glob
import pandas as pd
import numpy as np
import os
import os.path as op
from os.path import join as opj
import subprocess
import wave
from scipy.io import wavfile
import copy
import pickle as pkl
import time
import matplotlib.pyplot as plt

class MSITsession(Session):

    def __init__(self, output_str, output_dir, settings_file, subject_initials, tr, start_block,
                 gend, age, session_nr):
        super(MSITsession, self).__init__(output_str=output_str,
                                                output_dir=output_dir,
                                                settings_file=settings_file)
        
        self.settings_files = settings_file
        self.session_nr =session_nr
        self.gend = gend
        self.age = age
        self.subject_initials=subject_initials
        self.stimSize = self.settings['stimulus']['stimSize']
        self.design = None
        self.tr = tr
        self.start_block = int(start_block)  # allows for starting at a later block than 1
        self.ev_to_start = 0 
        self.operator_button = self.settings['input']['operator_skip_button']
        self.line_space = self.settings['stimulus']['line_space']

        self.response_button_signs = [self.settings['input']['response_button_1'],
                                      self.settings['input']['response_button_2'],
                                      self.settings['input']['response_button_3']]

		# define durations of each phase per trial 
        self.phase_durations = np.array([1000,        # phase 0: wait for scanner pulse
                                         1,        # phase 1: fixation cross 1
                                         1.6,      # phase 2: stimulus presentations time + fixation circle
                                         0.0,      # phase 3: correctness feedback (only for practice task) + fixation circle
                                         0.4,      # phase 4: timing feedback + fixation circle
                                         2])       # phase 5: fixation cross 3
                                         
        self.phase_names = ['fix_cross1',         # phase 0
                            'stimulus',           # phase 1
                            'correctness',        # phase 2
                            'timing_feedback',    # phase 3
                            'ITI']                # phase 4


    def load_design(self):
        """ Load trial designs """

        fn = 'sub-' + str(self.subject_initials).zfill(3) + '_ses-' + str(self.session_nr) + '_tr-' + str(self.tr) + '_design_task-MSIT'
        design = pd.read_csv(opj('designs_MSIT', fn + '.csv'), sep='\t', index_col=False, converters={'stimuli': lambda x: str(x)}) # removed sep='\t',
		# must add converter line above to preserve the leading zeros in the stimuli 

        print(fn)

        self.design = design

        self.design.block = self.design.block.apply(pd.to_numeric) # might not need this,
        self.design.jitter = self.design.jitter.apply(pd.to_numeric) # might not need this,

    def prepare_objects(self):

        self.fixation_circle = FixationCircle(win=self.win,
                                              circle_radius_degrees=self.settings['stimulus']['circle_radius_degrees'],
                                              line_width=self.settings['stimulus']['line_width'],
                                              line_color=self.settings['stimulus']['line_color'])

        self.correct_resp = FeedbackCorrect(self.win, self.settings['stimulus']['textSize'])
        self.wrong_resp = FeedbackWrong(self.win, self.settings['stimulus']['textSize'])
        self.quick_resp = FeedbackQuick(self.win, self.settings['stimulus']['textSize'])
        self.slow_resp = FeedbackSlow(self.win, self.settings['stimulus']['textSize'])
        self.veryslow_resp = FeedbackVerySlow(self.win, self.settings['stimulus']['textSize'])

    # new py3 savedata routine
    def save_data(self, block_nr=None):

        global_log = pd.DataFrame(self.global_log).set_index('trial_nr').copy()
        global_log['onset_abs'] = global_log['onset'] + self.exp_start

        # Only non-responses have a duration
        nonresp_idx = ~global_log.event_type.isin(['response', 'trigger', 'pulse', 'non_response_keypress'])
        last_phase_onset = global_log.loc[nonresp_idx, 'onset'].iloc[-1]

        if block_nr is None:
            dur_last_phase = self.exp_stop - last_phase_onset
        else:
            dur_last_phase = self.clock.getTime() - last_phase_onset
        durations = np.append(global_log.loc[nonresp_idx, 'onset'].diff().values[1:], dur_last_phase)
        global_log.loc[nonresp_idx, 'duration'] = durations

        # Same for nr frames
        nr_frames = np.append(global_log.loc[nonresp_idx, 'nr_frames'].values[1:], self.nr_frames)
        global_log.loc[nonresp_idx, 'nr_frames'] = nr_frames.astype(int)

        # Round for readability and save to disk
        global_log = global_log.round({'onset': 5, 'onset_abs': 5, 'duration': 5})

        global_log['gender'] = self.gend
        global_log['age'] = self.age
        global_log['session'] = self.session_nr

        if block_nr is None:
            f_out = op.join(self.output_dir, self.output_str + '_events.tsv')
        else:
            f_out = op.join(self.output_dir, self.output_str + '_block-' + str(block_nr) + '_events.tsv')

        global_log.to_csv(f_out, sep='\t', index=True)

        # Save frame intervals to file
        self.win.saveFrameIntervals(fileName=f_out.replace('_events.tsv', '_frameintervals.log'), clear=False)

    def create_trials(self, block_n):
        this_block_design = self.design.loc[self.design.block == block_n]
        self.trials = []

        for index, row in this_block_design.iterrows():

            this_trial_parameters = {'subject': row['subject'],
                                     'stimuli': row['stimuli'],
                                     'condition': row['condition'],
                                     'correct_response': row['unique'],
                                     'block_nr': block_n,
                                     'jitter': row['jitter'],
                                     'n_trs': row['n_trs'],
                                     'null_trial': row['null_trial']}

            phase_durations = [row['fix_circ_1'],
                               row['stimulus_dur'],
                               row['feedback_cor_dur'],
                               row['feedback_timing_dur'],
                               100] # show fixation circle 3 until scanner syncs

            self.trials.append(MSITRIAL(trial_nr=int(index),
                                             #ID=self.subject_initials,
                                             parameters=this_trial_parameters,
                                             phase_durations=phase_durations,
                                             phase_names=self.phase_names,
                                             session=self))
                
    def close(self):
        """ 'Closes' experiment. Should always be called, even when
        experiment is quit manually (saves onsets to file). """

        if self.closed:  # already closed!
            return None

        # self.win.saveMovieFrames(fileName='frames/DEMO2.png')

        self.win.callOnFlip(self._set_exp_stop)
        self.win.flip()
        self.win.recordFrameIntervals = False

        print(f"\nDuration experiment: {self.exp_stop:.3f}\n")

        if not op.isdir(self.output_dir):
            os.makedirs(self.output_dir)

        self.save_data()

        # Create figure with frametimes (to check for dropped frames)
        # fig, ax = plt.subplots(figsize=(15, 5))
        # ax.plot(self.win.frameIntervals)
        # ax.axhline(1. / self.actual_framerate, c='r')
        # ax.axhline(1. / self.actual_framerate + 1. / self.actual_framerate, c='r', ls='--')
        # ax.set(xlim=(0, len(self.win.frameIntervals) + 1), xlabel='Frame nr', ylabel='Interval (sec.)',
        #        ylim=(-0.1, 0.5))
        # fig.savefig(op.join(self.output_dir, self.output_str + '_frames.png'))

        if self.mri_simulator is not None:
            self.mri_simulator.stop()

        self.win.close()
        self.closed = True

    # new py3 run routine
    def run(self):
        """ Runs this MSIT """
        
        self.load_design()
        self.prepare_objects()
        trial_nr = None
        
        if self.exp_start is None:
            self.start_experiment()

        # Find out if its a practice session and show instructions accordingly
        if self.subject_initials.startswith('p'): # if practice task

            # show first set of instructions (this is practice task)
            instructions_ = exp_instructions(trial_nr, instruct_nr=1,  phase_durations=[10000], session=self, win=self.win)
            instructions_.run()
            
            # show second set of instructions (task description)
            instructions_ = exp_instructions(trial_nr, instruct_nr=2,  phase_durations=[10000], session=self, win=self.win)
            instructions_.run()

            # show second set of instructions (feedback instructions)
            instructions_ = exp_instructions(trial_nr, instruct_nr=3,  phase_durations=[10000], session=self, win=self.win)
            instructions_.run()

        else: # if main task

            # Dont show any instructions for now = straight to waiting for scanner screen
            print('waiting for operator screen')
            # show last set of instructions
            #instructions_ = exp_instructions(trial_nr, instruct_nr=4, phase_durations=[10000], session=self, win=self.win)
            #instructions_.run()

        # warn participant the task is about to task
        #instructions_ready = exp_instructions(trial_nr, instruct_nr=5,  phase_durations=[5], session=self, win=self.win)
        #instructions_ready.run()

        # find all blocks             
        all_blocks = np.unique(self.design.block)

        for block_nr in all_blocks:

            if block_nr < self.start_block:
                continue

            self.create_trials(block_nr)

            self.ev_to_start = 0

            instructions_operator = OperatorScreen(trial_nr, phase_durations=[10000], session=self, win=self.win)
            instructions_operator.run()

            print('waiting for scanner screen')

            instructions_wait = exp_instructions(trial_nr, instruct_nr=6,  phase_durations=[10000], session=self, win=self.win)
            instructions_wait.run()

            # loop over trials
            for trial in self.trials:

                print('phase durations: ' + str(trial.phase_durations))
                print(trial.parameters)

                trial.run()
                
            self.save_data(block_nr=block_nr)

        instructions_operator = OperatorScreen(trial_nr, phase_durations=[10000], session=self, win=self.win)
        instructions_operator.run()

        self.close()
        #self.quit()

# if __name__ == '__main__':

#     import datetime
#     import os
#     scanner = False
#     subject_initials = 1
#     gend = 'f'
#     age = 1
    
#     this_dir = os.getcwd()
#     timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
#     output_str = f'sub-{subject_initials}_ses-{session_nr}_task-MSIT_{timestamp}'
#     output_dir = os.path.join(this_dir, 'SST_MSIT_behavioural/dataMSIT')

#     if simulate == 'y':
#         #settings_file = '/Users/scotti/surfdrive/experiment_code/py3_SST_MSIT/IMCN-SST-MSIT/simulate_settings.yml'
#         settings_file = os.path.join(this_dir, 'simulate_settings.yml')
#     else:
#         #settings_file = '/Users/scotti/surfdrive/experiment_code/py3_SST_MSIT/IMCN-SST-MSIT/exp_settings.yml'
#         settings_file = os.path.join(this_dir, 'exp_settings.yml')
    
#     # Set-up session
#     Msess = MSITsession(output_str=output_str,
#                         output_dir=output_dir,
#                         settings_file=settings_file,
#                         subject_initials=subject_initials,
#                         gend=gend,
#                         age=age)

#     Msess.run()

