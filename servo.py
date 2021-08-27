import numpy as np

import dictionary_keys as dk


class Servo:
    """
    Object in 3D space that rotates a lever arm based on PWM input.
    The reference for positioning is intersection of lever's rotation axis
    and the plane in which center of snap ball moves.
    The rotation is in direction of positive  X, the lever's initial position is to negative Y from rotation axis.
    """

    def __init__(self):
        self.transform = np.identity(4)
        self.lever_length = 1.0
        self.pwm_low = 1100.0
        self.pwm_high = 1900.0
        self.angle_low_rad = np.radians(-45.0)
        self.angle_high_rad = np.radians(45.0)

    def load_config(self, config: dict):
        self.transform = np.identity(4)
        self.transform[0, 3] = config[dk.position][dk.x]
        self.transform[1, 3] = config[dk.position][dk.y]
        self.transform[2, 3] = config[dk.position][dk.z]

        psi = np.radians(config[dk.rotation_deg][dk.z])
        c, s = np.cos(psi), np.sin(psi)

        rot = np.array([[c, -s, 0, 0],
                        [s, c, 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1]])

        self.transform = np.matmul(self.transform, rot)

        self.lever_length = config[dk.lever_length]
        self.pwm_low = config[dk.lerp][dk.pwm_low]
        self.pwm_high = config[dk.lerp][dk.pwm_high]
        self.angle_low_rad = np.radians(config[dk.lerp][dk.angle_low_deg])
        self.angle_high_rad = np.radians(config[dk.lerp][dk.angle_high_deg])

    def snap_pos(self, pwm: float):
        result = np.array([[0],
                           [-self.lever_length],
                           [0],
                           [1]])

        lev_ang = self._lever_angle(pwm)
        c, s = np.cos(lev_ang), np.sin(lev_ang)
        rot = np.array([[1, 0, 0, 0],
                        [0, c, -s, 0],
                        [0, s, c, 0],
                        [0, 0, 0, 1]])
        result = np.matmul(rot, result)

        result = np.matmul(self.transform, result)
        return result

    def _lever_angle(self, pwm: float):  # lerp between angles by PWM
        alpha = (pwm - self.pwm_low) / (self.pwm_high - self.pwm_low)
        return self.angle_low_rad + alpha * (self.angle_high_rad - self.angle_low_rad)

    def __str__(self):
        return 'Servo pos[{0:0.1f} {1:0.1f} {2:0.1f}]'.format(
            self.transform[0, 3], self.transform[1, 3], self.transform[2, 3])
