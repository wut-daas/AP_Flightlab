import numpy as np

import dictionary_keys as dk


class Rotorhub:
    """
    Object representing linkage from upper part of swashplate to blade grips.
    """

    def __init__(self):
        self.grip_lever_length = 1.0
        self.rod_length = 3.0
        self.swashplate_lever_length = 1.0

    def load_config(self, config: dict):
        self.grip_lever_length = config[dk.rotorhub][dk.lever_length]
        self.rod_length = config[dk.rotorhub][dk.rod_length]
        self.swashplate_lever_length = config[dk.swashplate][dk.lever_length]

    def calc_pitch(self, sp_state: np.array):
        """
        Calculate pitch components from swashplate state.
        Assumes CW (clockwise) rotor rotation direction
        Order of pitch components in output is: 0-collective, 1-cyclic pitching nose up, 2-cyclic rolling right.
        """
        quad_params = np.zeros((4, 2))
        quad_params[:, 1] = sp_state[2]
        quad_params[0, 0] = np.pi / 2 + sp_state[1]  # azimuth 0 deg (back)
        quad_params[1, 0] = np.pi / 2 - sp_state[0]  # azimuth 90 deg (left)
        quad_params[2, 0] = np.pi / 2 - sp_state[1]  # azimuth 180 deg (front)
        quad_params[3, 0] = np.pi / 2 + sp_state[0]  # azimuth 270 deg (right)

        gamma = self.solve_quad(quad_params)

        return np.array([
            np.sum(gamma) / 4,  # collective
            (gamma[2] - gamma[0]) / 2,  # cyclic nose up
            (gamma[1] - gamma[3]) / 2,  # cyclic to right
        ])

    def solve_quad(self, quad_params: np.array):
        """
        Solves quadgon for each row where first column is bottom angle, second is length along shaft
        """
        assert quad_params.shape[1] == 2

        S = np.zeros(quad_params.shape)  # point S, center of swashplate ball
        S[:, 0] = self.swashplate_lever_length * np.sin(quad_params[:, 0])  # x coordinate
        S[:, 1] = quad_params[:, 1] - self.swashplate_lever_length * np.cos(quad_params[:, 0])  # y coordinate

        s = np.sqrt(np.sum(S * S, axis=1))  # distance from origin to point S
        zeta = np.arctan2(S[:, 0], S[:, 1])  # angle between point S and shaft, at origin

        y = np.repeat(self.grip_lever_length, quad_params.shape[0])
        L = np.repeat(self.rod_length, quad_params.shape[0])
        eta = np.arccos((y*y + s*s - L*L) / (2 * y * s))  # angle between point S and blade chord

        return zeta + eta - np.repeat(np.pi / 2, quad_params.shape[0])  # pitch angle (gamma)
