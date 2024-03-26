from exptools2.core import Session
from exptools2.core import Trial
from psychopy import event, visual
from MSIstim import MSIstimulus
import pandas as pd
import numpy as np

class MSITRIAL(Trial): # pass default exptools2 trial class to MSITRIAL

    def __init__(self, trial_nr, parameters, phase_durations, session=None, phase_names=None): # overwrite default init class to add task-specfic parameters
        super(MSITRIAL, self).__init__(trial_nr=trial_nr,
                                              parameters=parameters,
                                              phase_names=phase_names,
                                              phase_durations=phase_durations,
                                              session=session)

        # Define whether trial should run as practice session
        self.practicing = None
        if self.session.subject_initials.startswith('p'):
            self.practicing = True
        else:
            self.practicing = False

        # Setup other important variables
        self.trial_nr = trial_nr
        self.trs_recorded = 0
        self.response_measured = False  # Has the pp responded yet?
        self.response = {}
        self.response['choice_key'] = None
        self.response['rt'] = None
        self.parameters = parameters
        self.null_trial = parameters['null_trial']

        if parameters['stimuli'] in ['NaN','nan','nan.'] or pd.isna(parameters['stimuli']):
            self.stim = None
        else: 
            self.stim = MSIstimulus(win=self.session.win, trial_stim=str(parameters['stimuli']), stimSize=self.session.stimSize)
        
        self.fb_object_cor = None
        self.fb_object_timing = None

        if 'n_trs' in parameters.keys():
           self.stop_on_tr = parameters['n_trs']
        else:
           self.stop_on_tr = None

    def get_events(self):
        """ evs, times can but used to let a child object pass on the evs and times """

        evs = event.getKeys(timeStamped=self.session.clock)

        for ev, time in evs:
            if len(ev) > 0:
                if ev == 'q':
                    print('q button pressed (session will quit)')
                    self.session.close()
                    self.session.quit()
                elif ev == 'equal' or ev == '+':
                    self.stop_trial()

                idx = self.session.global_log.shape[0]

                # TR pulse
                #print(ev)
                #print(self.session.mri_trigger)
                if ev == self.session.mri_trigger:
                    event_type = 'pulse'
                    self.trs_recorded += 1

                    if self.stop_on_tr is not None:
                        # Trial ends whenever trs_recorded >= preset number of trs
                        if self.trs_recorded >= self.stop_on_tr:
                            self.stop_trial()

                elif ev in self.session.response_button_signs:
                    event_type = 'response'
                    if self.phase == 1:
                        if not self.response_measured:
                            self.response_measured = True
                            self.process_response(ev, time, idx)

                            # Not in the MR scanner? End phase upon keypress
                            # if not self.session.in_scanner and self.phase == 3:
                            #     self.stop_phase()
                else:
                    event_type = 'non_response_keypress'
                    #print('no valid response button pressed')

                # global response handling
                self.session.global_log.loc[idx, 'trial_nr'] = self.trial_nr
                self.session.global_log.loc[idx, 'block_nr'] = self.parameters['block_nr']
                self.session.global_log.loc[idx, 'onset'] = time
                self.session.global_log.loc[idx, 'event_type'] = event_type
                self.session.global_log.loc[idx, 'phase'] = self.phase
                self.session.global_log.loc[idx, 'response'] = ev

                for param, val in self.parameters.items():
                    self.session.global_log.loc[idx, param] = val

                if self.eyetracker_on:  # send msg to eyetracker
                    msg = f'start_type-{event_type}_trial-{self.trial_nr}_phase-{self.phase}_key-{ev}_time-{time}'
                    self.session.tracker.sendMessage(msg)

                if ev != self.session.mri_trigger:
                    self.last_resp = ev
                    self.last_resp_onset = time
    
    def process_response(self, ev, time, idx):
        """ Processes a response:
        - checks if the keypress is correct/incorrect;
        - checks if the keypress was in time;
        - Prepares feedback accordingly """
        
        self.response['choice_key'] = ev

        # to calculate response time, look up stimulus onset time
        log = self.session.global_log
        stim_onset_time = log.loc[(log.trial_nr == self.trial_nr) & (log.event_type == 'stimulus'), 'onset'].values[0]

        self.response['rt'] = time - stim_onset_time

        # if they respond with an acceptable button
        if ev in self.session.response_button_signs:
        
            print('button pressed')

            # Show correct/incorrect and timing feedback on practice trials
            if self.practicing==True: # if practice task 
                if ((ev == str(self.session.response_button_signs[0]) and str(self.parameters['correct_response']) == '1')
                        or (ev == str(self.session.response_button_signs[1]) and str(self.parameters['correct_response']) == '2')
                            or (ev == str(self.session.response_button_signs[2]) and str(self.parameters['correct_response']) == '3')): # if answer was correct
                    self.fb_object_cor = self.session.correct_resp
                    print('correct')
                    if self.response['rt'] <= 0.6:
                        self.fb_object_timing = self.session.quick_resp
                        print('response in time')
                    elif self.response['rt'] > 0.6 and self.response['rt'] <= 0.9:
                        self.fb_object_timing = self.session.slow_resp
                        print('response too slow')
                    else:
                        self.fb_object_timing = self.session.veryslow_resp
                        print('response very slow')                    
                else: # if answer was incorrect
                    self.fb_object_cor = self.session.wrong_resp
                    print('incorrect')
                    if self.response['rt'] <= 0.6:
                        self.fb_object_timing = self.session.quick_resp
                        print('response in time')
                    elif self.response['rt'] > 0.6 and self.response['rt'] <= 0.9:
                        self.fb_object_timing = self.session.slow_resp
                        print('response too slow')
                    else:
                        self.fb_object_timing = self.session.veryslow_resp
                        print('response very slow')    

            else: # if not practice task
                if self.response['rt'] <= 0.6:
                    self.fb_object_timing = self.session.quick_resp
                    print('response in time')
                elif self.response['rt'] > 0.6 and self.response['rt'] <= 0.9:
                    self.fb_object_timing = self.session.slow_resp
                    print('response too slow')
                else:
                    self.fb_object_timing = self.session.veryslow_resp
                    print('response very slow')
                    
        # chceck this statement below, i dont think it runs
        else: # if they did not press a button
            print('no valid response button pressed')
            if self.practicing == True: # if practice task
                self.fb_object = self.session.wrong_resp            
            else:
                self.fb_object = self.session.slow_resp
        
        # self.make_feedback_screen() # do i need this? 

        self.session.global_log.loc[idx, 'rt'] = self.response['rt']
        self.session.global_log.loc[idx, 'choice_key'] = self.response['choice_key']                       
            
    def draw(self):
        """
        Phases:
        0 = fixation cross 1
        1 = stimulus
        2 = correctness feedback (pracatice only)
        3 = timing feedback
        4 = ITI (blank screen)
        """
        
        if self.phase in [0, 1, 2, 3]:
            if not self.null_trial:
                self.session.fixation_circle.draw()
        if self.phase == 1: # stimulus
            if self.stim is not None:
                self.stim.draw() 
        if self.phase == 2: # correctness feedback
            if self.fb_object_cor is not None:
                self.fb_object_cor.draw()
        if self.phase == 3: # timing feedback
            if self.fb_object_timing is not None:
                self.fb_object_timing.draw()

class exp_instructions(Trial):

    def __init__(self, trial_nr, instruct_nr, session =None, phase_durations=None, win=None): # overwrite default init class to add task-specfic parameters
        super(exp_instructions, self).__init__(trial_nr=trial_nr,
                                               session=session,
                                               phase_durations=phase_durations)
        
        self.win=win
        self.instruct_nr = instruct_nr

        nblocks = len(np.unique(self.session.design.block))
              
        if instruct_nr == 1:
        
            task_instructions = ["PRACTICE TASK","","","You will now start a practice session of the multi-source interference task.","","",
                                 "There will be " + str(len(self.session.design.block)//nblocks) + " practice trials.","","","Press < space > to continue to the instructions"]
            self.wait_screen = 'n'

        elif instruct_nr == 2:
            
            task_instructions = ["INSTRUCTIONS","","Every few seconds, a set of three numbers (1, 2, 3, or 0) will appear in the center of the screen.",
                                "One number will always be different from the other two.","Press the button corresponding to the identity, not the position, of the differing number.",
                                "The values corresponding to the buttons are: index finger = 1, middle finger = 2, and ring finger = 3",
                                "Please use the following keys to respond: 1 = red, 2 = green, 3 = yellow","You will only have 600ms to respond.","","",
                                "Press < space > to continue to further instructions"]
            self.wait_screen = 'n'
        
        elif instruct_nr == 3:

            task_instructions = ["In the practice task, you will receive the following feedback on your responses:","","Firstly, you will receive coloured feedback on the correctness of your response:","'correct' or 'incorrect'","",
                                 "Secondly, you will receive feedback on the speed of your response:","'in time', 'too slow' or 'very slow'","","Please try to be as accurate as possible, while trying to remain 'in time'","",
                                 "Press < space > to start the practice task"]
            self.wait_screen = 'n'

        elif instruct_nr == 4:
        
            if nblocks > 1:
                def_block = 'blocks'
            else:
                def_block = 'block'

            task_instructions = ["EXPERIMENTAL TASK","","","You will now start the experimental session of the multi-source interference task.","","",
                                "There will be " + str(nblocks) + " " + def_block + " of " + str(len(self.session.design.block)//nblocks) + " trials.",
                                "","","IMPORTANT:","You will no longer get feedback on correct or incorrect responses, you will only receive feedback on your timing.","","Please try to respond as quickly but as accurately as possible.",
                                "","","Press < space > to start the task"]
            self.wait_screen = 'n'

        elif instruct_nr == 5:

            task_instructions = ["The task is about to start,","please have your fingers ready", "on the response buttons"]
            self.wait_screen = 'n'

        elif instruct_nr == 6:

            task_instructions = ["Waiting for scanner"]
            self.wait_screen = 'y'

        self.instruction_text = self.gen_instructions(task_instructions, deg_per_line=self.session.line_space, bottom_pos=len(task_instructions))
                                                
    def get_events(self):

        evs = event.getKeys(timeStamped=self.session.clock)

        for ev, time in evs:
            if len(ev) > 0:

                idxs = self.session.global_log.shape[0]

                if ev == 'q': # quit
                    self.session.close()
                    self.session.quit()
                elif ev == 'equal' or ev == '+': # skip trial
                    self.stop_trial()

                # move to next phase
                if self.wait_screen == 'n':
                    if ev == 'space': # end trial
                        self.last_key = ev
                        self.stop_phase()
                # move to next phase if on waiting screen
                elif self.wait_screen == 'y':
                    if ev == self.session.mri_trigger:
                        self.session.ev_to_start += 1
                        self.last_key = ev
                        if self.session.ev_to_start == 4: # wait until 4th trigger to start task
                            self.stop_phase()

                # TR pulse
                if ev == self.session.mri_trigger:
                    event_type = 'pulse'
                elif ev in self.session.response_button_signs:
                    event_type = 'response'

                else:
                    event_type = 'non_response_keypress'

                # global response handling
                self.session.global_log.loc[idxs, 'trial_nr'] = self.trial_nr
                self.session.global_log.loc[idxs, 'onset'] = time
                self.session.global_log.loc[idxs, 'event_type'] = event_type
                self.session.global_log.loc[idxs, 'response'] = ev

    def draw(self):

        for ins in self.instruction_text:
            ins.draw()

        #super(exp_instructions, self).draw()                                                
    def gen_instructions(self, input_text, deg_per_line=2, bottom_pos=3, wrapWidth=100):

        text_objects = []

        if bottom_pos == 1:
            for i, text in enumerate(input_text):
                text_objects.append(visual.TextStim(win=self.win, text=text, units='deg', pos=(0,bottom_pos*0.5-i*deg_per_line), alignVert='bottom',wrapWidth=wrapWidth,height=self.session.settings['stimulus']['instructSize']))

        else:
            for i, text in enumerate(input_text):
                text_objects.append(visual.TextStim(win=self.win, text=text, units='deg', pos=(0,bottom_pos*0.5-i*deg_per_line), alignVert='bottom',wrapWidth=wrapWidth,height=self.session.settings['stimulus']['instructSize']))

        return text_objects

# MAKE ONE CLASS JUST TO DO WAITING FOR OPERATOR SCREEN BECAUSE IM LAZY
class OperatorScreen(Trial):

    def __init__(self, trial_nr, session =None, phase_durations=None, win=None): # overwrite default init class to add task-specfic parameters
        super(OperatorScreen, self).__init__(trial_nr=trial_nr,
                                               session=session,
                                               phase_durations=phase_durations)
        self.win = win

    def get_events(self):

        for ev, time in event.getKeys(timeStamped=self.session.clock):
            if len(ev) > 0:

                idxs = self.session.global_log.shape[0]

                if ev == 'q': # quit
                    print('q button pressed during operator screen (session will quit)')
                    self.session.close()
                    self.session.quit()

                # move to next phase if operator button pressed
                if ev == self.session.operator_button: # end phase
                        self.last_key = ev
                        self.stop_phase()

                # TR pulse
                if ev == self.session.mri_trigger:
                    event_type = 'pulse'
                elif ev in self.session.response_button_signs:
                    event_type = 'response'
                else:
                    event_type = 'non_response_keypress'

                # global response handling
                self.session.global_log.loc[idxs, 'trial_nr'] = self.trial_nr
                self.session.global_log.loc[idxs, 'onset'] = time
                self.session.global_log.loc[idxs, 'event_type'] = event_type
                self.session.global_log.loc[idxs, 'response'] = ev

    def draw(self):

        if self.phase == 0:   # waiting for scanner-time
            visual.TextStim(win=self.win, text='Waiting for operator', alignVert='bottom', pos=(0,0), 
                                wrapWidth=100,height=self.session.settings['stimulus']['instructSize']).draw()
