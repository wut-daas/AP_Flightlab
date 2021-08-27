import numpy as np

import dictionary_keys as dk
from servo import Servo
from swashplate import Swashplate
from rod_solver import RodSolver
from rotorhub import Rotorhub


class Helicopter:
    """
    Container for configuration of all other objects, previously in main script
    """

    def __init__(self, config: dict):
        self.servos = [Servo(), Servo(), Servo()]  # Only for type hinting
        self.rod_lengths = np.zeros(3, dtype=np.float_)
        self.swashplate = Swashplate()
        self.rotorhub = Rotorhub()
        self.tail_pitch_gain = 0.0
        self.tail_pitch_trim = 0.0
        self.tail_pwm_trim = 0.0
        self.load_config(config)
        self.rodsolver = RodSolver(config, self.swashplate, self.rod_lengths)

    def load_config(self, config: dict):
        for servo_config in config[dk.servos]:
            srv = Servo()
            srv.load_config(servo_config)
            self.servos[dk.channel_order[servo_config[dk.channel]]] = srv
            self.rod_lengths[dk.channel_order[servo_config[dk.channel]]] = servo_config[dk.rod_length]

        self.swashplate.load_config(config[dk.swashplate])
        self.rotorhub.load_config(config)
        self.rodsolver = RodSolver(config, self.swashplate, self.rod_lengths)

        self.tail_pitch_gain = config[dk.tail][dk.pitch_gain]
        self.tail_pitch_trim = config[dk.tail][dk.pitch_trim]
        self.tail_pwm_trim = config[dk.tail][dk.pwm_trim]

    def calc_pitch(self, pwm: np.array):
        servo_snaps = np.concatenate((
            self.servos[0].snap_pos(pwm[0]),
            self.servos[1].snap_pos(pwm[1]),
            self.servos[2].snap_pos(pwm[2]),
        ), axis=1)
        sp_state = self.rodsolver.solve_for_sp_state(servo_snaps)

        return self.rotorhub.calc_pitch(sp_state)
    
    def calc_tail(self, pwm: float):
        return self.tail_pitch_trim + self.tail_pitch_gain * (pwm - self.tail_pwm_trim)
