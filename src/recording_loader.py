import numpy as np

class RecordingLoader:
    def __init__(self, path):
        recording = np.load(path)
        self.actions = recording['actions']
        self.screens = recording['screens']
        self.ram_states = recording['ram']

    def get_actions(self):
        return self.actions

    def get_screens(self, normalize=True):
        if not normalize:
            return self.screens
        
        screens = np.divide(self.screens, 255, dtype=np.float32)
        return screens

    def get_ram_states(self):
        return self.ram_states