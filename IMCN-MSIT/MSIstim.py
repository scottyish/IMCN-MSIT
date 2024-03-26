from psychopy import visual

# define stimulus for MSIT

# display stimulus
class MSIstimulus(object):

    def __init__(self, win, trial_stim, stimSize):
        self.win=win
        self.trial_stim=trial_stim
        self.stimSize = stimSize
        
        self.sequence_stim = visual.TextStim(win=self.win, text=trial_stim, 
                                            name='trial_stim_screen',
                                            units='deg',font='Helvetica Neue',
                                            pos=(0,0),height=self.stimSize,alignHoriz='center')
        
    def draw(self):
        self.sequence_stim.draw()

# define fixation circle around stimuli (same as circle from stop-signal task) 
class FixationCircle(object):
                                         
    def __init__(self, win, circle_radius_degrees=6, line_width=1.5, line_color='white'):          
                           # Have been enlarged (+3) to fit wider feedback
        self.win=win
        self.circle_size_degrees=circle_radius_degrees
        
        self.circle_stim = visual.Circle(win=self.win,
                                         radius=circle_radius_degrees, edges=100, lineWidth=line_width,
                                         lineColor=line_color, units='deg',
                                         lineColorSpace='rgb', fillColorSpace='rgb')
    def draw(self):
        self.circle_stim.draw()
        
class FeedbackCorrect(object): # --------------- feedback for correct answers
    def __init__(self, win, textSize=2):
        self.win = win
        
        self.correctness = visual.TextStim(
            win=self.win, text='correct',color='green',
            pos=(0,0),font='Helvetica Neue',height=textSize, units='deg')     
    
    def draw(self):
        self.correctness.draw()


class FeedbackWrong(object): # ---------------- Feedback for incorrect answers
    def __init__(self,win, textSize=2):
        self.win = win
        
        self.wrongness = visual.TextStim(
            win=self.win, text='wrong',color='red',
            pos=(0,0),font='Helvetica Neue',height=textSize, units='deg')

    def draw(self):
        self.wrongness.draw()

class FeedbackQuick(object): # -------- feedback for response that were on time
    def __init__(self,win, textSize=2):
        self.win = win
        
        self.quickness = visual.TextStim(
            win=self.win, text='in time',color='white',
            pos=(0,0),font='Helvetica Neue',height=textSize, units='deg')
    
    def draw(self):
        self.quickness.draw()

  
class FeedbackSlow(object):  # -------------------- Feedback for slow responses
    def __init__(self,win, textSize=2):
        self.win = win
        
        self.slowness = visual.TextStim(
            win=self.win, text='too slow',color='white',
            pos=(0,0),font='Helvetica Neue',height=textSize, units='deg')

    def draw(self):
        self.slowness.draw()

class FeedbackVerySlow(object): # ---------- Feedback for (very) slow responses
    def __init__(self,win, textSize=2):
        self.win = win
        
        self.slowness2 = visual.TextStim(
            win=self.win, text='very slow',color='white',
            pos=(0,0),font='Helvetica Neue',height=textSize, units='deg')

    def draw(self):
        self.slowness2.draw()