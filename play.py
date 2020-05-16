import os
import sys
import retro
import numpy as np
from tensorflow.keras.models import load_model

from viewer import ImageViewer


# SCALE = 2
# WIDTH = SCALE * 256
# HEIGHT = SCALE * 224



def main():
    env = retro.make(game='SuperMarioBros-Nes')

    env.viewer = ImageViewer(maxwidth=1000)
    # env.viewer.window = pyglet.window.Window(width=WIDTH, height=HEIGHT, display=None, vsync=True, resizable=True)


    model = load_model(os.path.join('models', 'simple_model'))
    prediction = [0,0,0,0,0,0,0,0,0]

    frame = 0
    skip_frames = 1

    obs = env.reset()
    while True:
        #obs, rew, done, info = env.step(env.action_space.sample())
        
        # if frame % skip_frames == 0:
        ram = env.get_ram().reshape(1, 10240)
        prediction = model.predict(ram)
        prediction = (prediction[0] > 0.5).astype(np.uint8)
            # print(prediction)

        obs, rew, done, info = env.step(prediction)
        frame += 1

        #obs, rew, done, info = env.step(env.action_space.sample())

        #



        #sys.exit()
        
        # sample = env.action_space.sample()

        # print(env.get_action_meaning(sample))
        # print(env.action_to_array(sample))
        # print(info)
        env.render(mode="human")
        # if first:
        #     first = False
        #     env.viewer.on_resize(WIDTH, HEIGHT)

        if done:
            obs = env.reset()
    env.close()



    def close(self):
        if self.isopen and sys.meta_path:
            # ^^^ check sys.meta_path to avoid 'ImportError: sys.meta_path is None, Python is likely shutting down'
            self.window.close()
            self.isopen = False

    def __del__(self):
        self.close()

if __name__ == "__main__":
    main()