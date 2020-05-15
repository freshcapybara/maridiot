import argparse
import retro
import time
import numpy as np
import sys
import os
from pyglet.window import key as keycodes
from retro.examples.interactive import Interactive



class OurRetroInteractive(Interactive):
    """
    Interactive setup for retro games
    """
    def __init__(self, game, state, scenario):
        env = retro.make(game=game, state=state, scenario=scenario)
        self._buttons = env.buttons
        super().__init__(env=env, sync=False, tps=60, aspect_ratio=4/3)
        self.session_name = f"{scenario}-{time.time()}"
        self.session_data = []

    def get_image(self, _obs, env):
        return env.render(mode='rgb_array')

    def keys_to_act(self, keys):
        inputs = {
            None: False,

            'BUTTON': 'Z' in keys,
            'A': 'Z' in keys,
            'B': 'X' in keys,

            'C': 'C' in keys,
            'X': 'A' in keys,
            'Y': 'S' in keys,
            'Z': 'D' in keys,

            'L': 'Q' in keys,
            'R': 'W' in keys,

            'UP': 'UP' in keys,
            'DOWN': 'DOWN' in keys,
            'LEFT': 'LEFT' in keys,
            'RIGHT': 'RIGHT' in keys,

            'MODE': 'TAB' in keys,
            'SELECT': 'TAB' in keys,
            'RESET': 'ENTER' in keys,
            'START': 'ENTER' in keys,
        }
        return [inputs[b] for b in self._buttons]

    def run(self):
        prev_frame_time = time.time()
        while True:
            self._win.switch_to()
            self._win.dispatch_events()
            now = time.time()
            self._update(now - prev_frame_time)
            prev_frame_time = now
            self._draw()
            self._win.flip()

    def _on_close(self):
        #save collected data in file
        self.save_session()
        self._env.close()
        sys.exit(0)

    def _update(self, dt):
        # cap the number of frames rendered so we don't just spend forever trying to catch up on frames
        # if rendering is slow
        max_dt = self._max_sim_frames_per_update / self._tps
        if dt > max_dt:
            dt = max_dt

        # catch up the simulation to the current time
        self._current_time += dt
        while self._sim_time < self._current_time:
            self._sim_time += 1 / self._tps

            keys_clicked = set()
            keys_pressed = set()
            for key_code, pressed in self._key_handler.items():
                if pressed:
                    keys_pressed.add(key_code)

                if not self._key_previous_states.get(key_code, False) and pressed:
                    keys_clicked.add(key_code)
                self._key_previous_states[key_code] = pressed

            if keycodes.ESCAPE in keys_pressed:
                self._on_close()

            # assume that for async environments, we just want to repeat keys for as long as they are held
            inputs = keys_pressed
            if self._sync:
                inputs = keys_clicked

            keys = []
            for keycode in inputs:
                for name in dir(keycodes):
                    if getattr(keycodes, name) == keycode:
                        keys.append(name)

            act = self.keys_to_act(keys)

            if not self._sync or act is not None:
                #save the current ram state and the according actions of current frame
                self.save_frame(self._env.get_ram(), self._env.action_to_array(act))
                obs, rew, done, _info = self._env.step(act)    
                self._image = self.get_image(obs, self._env)
                self._episode_returns += rew
                self._steps += 1
                self._episode_steps += 1
                np.set_printoptions(precision=2)
                if self._sync:
                    done_int = int(done)  # shorter than printing True/False
                    mess = 'steps={self._steps} episode_steps={self._episode_steps} rew={rew} episode_returns={self._episode_returns} done={done_int}'.format(
                        **locals()
                    )
                    print(mess)
                elif self._steps % self._tps == 0 or done:
                    episode_returns_delta = self._episode_returns - self._prev_episode_returns
                    self._prev_episode_returns = self._episode_returns
                    mess = 'steps={self._steps} episode_steps={self._episode_steps} episode_returns_delta={episode_returns_delta} episode_returns={self._episode_returns}'.format(
                        **locals()
                    )
                    print(mess)

                if done:
                    self._env.reset()
                    self._episode_steps = 0
                    self._episode_returns = 0
                    self._prev_episode_returns = 0

    def save_frame(self, actions, ram):
        self.session_data.append(np.array([actions, ram]))

    def save_session(self):
        data = np.array(self.session_data)
        print(data)
        np.save(os.path.join("recordings", self.session_name), data)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--game', default='SuperMarioBros-Nes')
    parser.add_argument('--state', default=retro.State.DEFAULT)
    parser.add_argument('--scenario', default='scenario')
    args = parser.parse_args()

    ia = OurRetroInteractive(game=args.game, state=args.state, scenario=args.scenario)
    ia.run()


if __name__ == '__main__':
    main()