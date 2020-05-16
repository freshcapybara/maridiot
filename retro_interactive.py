import os
import sys
import argparse
import retro
import time
import numpy as np
import datetime
from pathlib import Path
from pyglet.window import key as keycodes
from retro.examples.interactive import RetroInteractive

RECORD_DIRECTORY = "recordings"


class OurRetroInteractive(RetroInteractive):
    def __init__(self, game, state, scenario, skip_frames, no_saving=False):
        self.session_name = f"{scenario}-{datetime.datetime.date(datetime.datetime.now())}-{datetime.datetime.now().hour}-{str(datetime.datetime.now().minute).zfill(2)}-{str(datetime.datetime.now().second).zfill(2)}"
        self.session_ram_data = []
        self.session_action_data = []
        self.skip_frames = skip_frames
        self.no_saving = no_saving

        super().__init__(game=game, state=state, scenario=scenario)

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
                if self._steps % self.skip_frames == 0:
                    self.save_frame(self._env.get_ram(), self._env.action_to_array(act)[0])
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

    def save_frame(self, ram, actions):
        self.session_ram_data.append(ram)
        self.session_action_data.append(actions)

    def save_session(self):
        assert len(self.session_ram_data) == len(self.session_action_data)
        data_points = len(self.session_ram_data)

        print(f"Generated {data_points} data points for {self._steps} frames of play time.")
        
        ram_data_name = os.path.join(RECORD_DIRECTORY, "ram", self.session_name)
        action_data_name = os.path.join(RECORD_DIRECTORY, "input", self.session_name)

        ram_data = np.array(self.session_ram_data, dtype=np.uint8)
        print(ram_data.shape, ram_data.dtype)

        if not self.no_saving:
            np.save(ram_data_name, self.session_ram_data)
            np.save(action_data_name, self.session_action_data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip_frames', default=1, type=int)
    parser.add_argument('--game', default='SuperMarioBros-Nes')
    parser.add_argument('--state', default=retro.State.DEFAULT)
    parser.add_argument('--scenario', default='scenario')
    parser.add_argument('--no_saving', action='store_true')
    args = parser.parse_args()

    # check if recordings directories exist
    Path(os.path.join(RECORD_DIRECTORY, "ram")).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(RECORD_DIRECTORY, "input")).mkdir(parents=True, exist_ok=True)

    ia = OurRetroInteractive(game=args.game, state=args.state, scenario=args.scenario, skip_frames=args.skip_frames, no_saving=args.no_saving)
    ia.run()


if __name__ == '__main__':
    main()