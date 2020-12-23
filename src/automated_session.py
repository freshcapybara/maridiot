import os
import sys
import retro
import numpy as np
import signal

from src.viewer import ImageViewer


class AutomaticSession():
    """
    Automated session, controlled by the AI
    """
    instance = None
    
    def __init__(self, game, handler, use_ram=False, skip_frames=0):
        """
        arguments:
        handler --
        use_ram -- use the ram for observations instead of the screen
        skip_frames -- how many frames will be skipped before doing a prediction call
        """
        AutomaticSession.instance = self

        observation_type = retro.Observations.IMAGE
        if use_ram:
            observation_type = retro.Observations.RAM
        
        self.game = game
        self.handler = handler
        self.skip_frames = skip_frames

        # instantiate retro environment
        self.env = retro.make(game=self.game, obs_type=observation_type)    
        # override default viewer so we get a bigger screen size and realtime-output
        self.env.viewer = ImageViewer(maxwidth=1080)
        # initialize environment
        self.env.reset()

        signal.signal(signal.SIGINT, receive_signal)
    

    def play(self):
        """
        Main function
        """

        frame_num = 0
        prediction_num = 0
        prediction = [0,0,0,0,0,0,0,0,0]

        # main loop
        while True:
            # make environment step
            # info - {'levelLo': 0, 'xscrollHi': 0, 'levelHi': 0, 'coins': 0, 'xscrollLo': 0, 'time': 400, 'scrolling': 16, 'lives': 2, 'score': 0}
            observation, reward, done, info = self.env.step(prediction)
            frame_num += 1

            if done:
                observation = self.env.reset()
                continue

            if self.skip_frames > 0 and frame_num % self.skip_frames != 0:
                continue

            #ram = env.get_ram().reshape(1, 10240)
            # print(observation.shape, observation.dtype)
            prediction = self.handler.make_choice(observation, frame_num)
            prediction_num += 1

            #obs, rew, done, info = env.step(env.action_space.sample())
            # try-except the renderer to handle the closing window error
            try:
                self.env.render(mode="human")
            except:
                break


    def close(self):
        AutomaticSession.instance = None
        self.env.close()


    def __del__(self):
        self.close()


# handle interrupts
def receive_signal(signal_number, frame):
    print("interrupt")
    if AutomaticSession.instance is not None:
        try:
            AutomaticSession.instance.close()
        except:
            pass