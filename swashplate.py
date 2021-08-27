import numpy as np

import dictionary_keys as dk


class Swashplate:
    """
    Object in 3D space representing the lower part of swashplate,
    the one that has three snaps connected by rods to servos.
    It is assumed to be symmetrical in y-axis, able to slide along shaft in z, and rotate in x, y around tha shaft.
    The back snap always stays in symmetry plane of the helicopter.
    """

    def __init__(self):
        self.local_snaps = Swashplate._local_snaps_pos(2.0, 1.0, 1.0)
        self.transform = np.identity(4)

    @staticmethod
    def _local_snaps_pos(width: float, front: float, back: float):
        return np.array([[front, -back, front],
                         [-width / 2, 0, width / 2],
                         [0, 0, 0],
                         [1, 1, 1]], dtype=np.float_)  # columns are individual snaps' positions

    def load_config(self, config: dict):
        self.local_snaps = Swashplate._local_snaps_pos(
            config[dk.width],
            config[dk.front],
            config[dk.back]
        )
        self.transform = np.identity(4)

    def update_transform(self, sp_state: np.array):
        """
        Order of channels in equations is: 0-aileron, 1-elevator, 2-collective.
        Order of degrees of freedom in equations is: 0-roll, 1-pitch, 2-slide.
        """
        self.transform = np.identity(4)

        c, s = np.cos(sp_state[0]), np.sin(sp_state[0])
        roll_rot = np.array([[1, 0, 0, 0],
                             [0, c, -s, 0],
                             [0, s, c, 0],
                             [0, 0, 0, 1]])
        self.transform = np.matmul(roll_rot, self.transform)

        c, s = np.cos(sp_state[1]), np.sin(sp_state[1])
        pitch_rot = np.array([[c, 0, s, 0],
                              [0, 1, 0, 0],
                              [-s, 0, c, 0],
                              [0, 0, 0, 1]])
        self.transform = np.matmul(pitch_rot, self.transform)

        self.transform[2, 3] = sp_state[2]  # slide along shaft

    def snaps_pos(self, sp_state=None):
        if sp_state is not None:
            self.update_transform(sp_state)

        return np.matmul(self.transform, self.local_snaps)

    def dof_differentials(self, sp_state=None):
        """
        Calculates differentials of each snap's position for every degree of freedom
        """
        if sp_state is not None:
            self.update_transform(sp_state)

        rotated_snaps = np.matmul(np.concatenate((self.transform[:, :3], np.array([[0], [0], [0], [1]])), axis=1),
                                  self.local_snaps)  # do not translate
        rotated_snaps_v3 = np.transpose(rotated_snaps[:3, :])

        roll_axis = np.array([[1],
                              [0],
                              [0],
                              [0]])  # w component set to 0 ignores translations
        roll_axis = np.matmul(self.transform, roll_axis)  # assumes there is no scaling
        roll_axis_v3 = np.repeat(np.transpose(roll_axis[:3, 0:1]), self.local_snaps.shape[1], axis=0)
        roll_tangents = np.cross(roll_axis_v3, rotated_snaps_v3)

        pitch_axis = np.array([[0],
                               [1],
                               [0],
                               [0]])
        # pitch axis is not rotated by roll
        pitch_axis_v3 = np.repeat(np.transpose(pitch_axis[:3, 0:1]), self.local_snaps.shape[1], axis=0)
        pitch_tangents = np.cross(pitch_axis_v3, rotated_snaps_v3)

        slide_tangents = np.repeat(np.array([[0, 0, 1]], dtype=np.float_), self.local_snaps.shape[1], axis=0)
        return np.stack((roll_tangents, pitch_tangents, slide_tangents))
