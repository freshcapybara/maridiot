
import os
import sys
import retro
import time
import numpy as np
from pathlib import Path
from pyglet.window import key as keycodes

from retro.examples.interactive import RetroInteractive

class RecordingSession(RetroInteractive):
    """
    High-level class for human controlled game interaction. Allows saving state information.
    """
    def __init__(self, game, scenario, save_directory, state=None, record_session=False):
        self.session_name = f"{game.lower()}-{int(time.time())}"
        
        # recording data
        self.record_session = record_session
        self.save_directory = save_directory
        self.session_screen_data = []
        self.session_ram_data = []
        self.session_action_data = []

        # create directories if necessary
        if self.record_session:
            Path(os.path.join(self.save_directory, "ram")).mkdir(parents=True, exist_ok=True)
            Path(os.path.join(self.save_directory, "input")).mkdir(parents=True, exist_ok=True)
        
        self.action_buffer = None
        self.start_time = time.time()
        if state is None:
            state = retro.State.DEFAULT
        super().__init__(game=game, state=state, scenario=scenario)


    # override
    def run(self):
        """
        Override of the parents run script for additional state and action saving.
        """
        prev_frame_time = time.time()
        while True:
            self._win.switch_to()
            self._win.dispatch_events()
            now = time.time()
            self._update(now - prev_frame_time)

            # save updated state if recording is set and we did a time step
            if self.record_session and self.action_buffer:
                self._save_frame(self._env.get_screen() , self._env.get_ram(), self._env.action_to_array(self.action_buffer)[0])
                print(self._env.action_to_array(self.action_buffer)[0])

            prev_frame_time = now
            self._draw()
            self._win.flip()


    def save_session(self):
        """
        Saves session states.
        """
        assert len(self.session_screen_data) == len(self.session_ram_data) == len(self.session_action_data)
        print(f"Recording lasted for {time.time()-self.start_time}s")
        print(f"Generated {len(self.session_action_data)} data points for {self._steps} frames of play time.")

        # convert the recordings to numpy arrays
        # uint8, (frames, 9), values are 0 or 1
        action_array = np.array(np.array(self.session_action_data, dtype=np.uint8))
        # uint8, (frames, 224, 240, 3), rgb values
        screen_array = np.array(np.array(self.session_screen_data, dtype=np.uint8))
        # uint8, (frames, 10240,)
        ram_array = np.array(np.array(self.session_ram_data, dtype=np.uint8))
        
        output_name = os.path.join(self.save_directory, self.session_name)
        np.savez_compressed(output_name, actions=action_array, screens=screen_array, ram=ram_array)
        print(f"Saved to {output_name}.npz")


    def _on_close(self):
        # save collected data once session closes
        if self.record_session:
            self.save_session()

        super()._on_close()


    def _save_frame(self, screen, ram, actions):
        self.session_screen_data.append(screen)
        self.session_ram_data.append(ram)
        self.session_action_data.append(actions)


    def _update(self, dt):
        # modified version of the _update of interactive.py
        # https://github.com/openai/retro/blob/master/retro/examples/interactive.py

        self.action_buffer = None
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
                obs, rew, done, _info = self._env.step(act)

                # save last action
                self.action_buffer = act

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