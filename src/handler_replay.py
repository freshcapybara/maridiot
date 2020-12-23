from src.handler import Handler
from src.recording_loader import RecordingLoader

class HandlerReplay(Handler):
    def __init__(self, path):
        super().__init__()

        self.actions = RecordingLoader(path).get_actions()
        self.actions_length = self.actions.shape[0]
    
    def make_choice(self, observation, frame_number):
        # if we for some reason achieve a higher frame number then we recorded just repeat the last frame
        if frame_number >= self.actions_length:
            print(f"Tried to access replay frame {frame_number+1} of {self.actions_length}")
            frame_number = self.actions_length - 1

        return self.actions[frame_number]