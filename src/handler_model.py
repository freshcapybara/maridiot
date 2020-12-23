import numpy as np
#from tensorflow.keras.models import load_model

from src.handler import Handler

class HandlerModel(Handler):
    def __init__(self):
        super().__init__()
    
    def make_choice(self, observation, frame_number):
        prediction = model.predict(observation)
        prediction = prediction[0]

        # apply threshold
        prediction = (prediction > 0.5).astype(np.uint8)
        print(prediction)

        # TODO figure out what ram values are exactly, bits? bytes? weird number of values
        return prediction
