import numpy as np
from typing import List

import dictionary_keys as dk
from servo import Servo
from swashplate import Swashplate


class RodSolver:
    """
    Finds swashplate state that gives correct connecting rod lengths for  a given servo input
    """

    def __init__(self, config: dict, swashplate: Swashplate, target_rod_lengths: np.array):
        self.swashplate = swashplate
        self.target_lengths = target_rod_lengths

        self.previous_sp_state = np.zeros(3)
        self.previous_sp_state[2] = config[dk.swashplate][dk.position][dk.z]  # default state
        self.tolerance = config[dk.solver][dk.tolerance]
        self.max_iterations = config[dk.solver][dk.max_iterations]
        self.verbose_output = config[dk.solver][dk.verbose]
        self.previous_servo_snaps = np.zeros(3)
        # TODO: load other adequate variables from config

    def solve_for_sp_state(self, servo_snaps: np.array):
        sp_state = self.previous_sp_state
        found_solution = False

        for iteration in range(self.max_iterations):

            self.swashplate.update_transform(sp_state)
            swashplate_snaps = self.swashplate.snaps_pos()

            rods_v3 = np.transpose(servo_snaps - swashplate_snaps)[:, :3]
            rod_lengths = np.sqrt(np.sum(rods_v3 * rods_v3, axis=1))
            rod_lengths_diff = rod_lengths - self.target_lengths

            if np.max(np.abs(rod_lengths_diff)) < self.tolerance:
                if self.verbose_output:
                    print('error is {}, tolerance is {}, breaking loop on {} iteration'.format(
                        np.max(rod_lengths_diff), self.tolerance, iteration))
                found_solution = True
                break

            rods_normalized_v3 = rods_v3 / np.repeat(np.reshape(rod_lengths, (3, 1)), 3, axis=1)

            pos_differentials = self.swashplate.dof_differentials()
            length_differentials = np.sum(pos_differentials *
                                          np.stack((rods_normalized_v3, rods_normalized_v3, rods_normalized_v3)),
                                          axis=2)
            coeff = np.transpose(length_differentials)
            """
            coeff is coefficients for linear equation set:
            a-aileron rod length, e-elevator rod length, c-collective rod length,
            r-swashplate roll, p-swashplate pitch, s-swashplate slide
            
                    | da/dr da/dp da/ds |
            coeff = | de/dr de/dp de/ds | 
                    | dc/dr dc/dp dc/ds |
            """
            coeff_inv = np.linalg.inv(coeff)

            sp_delta = np.matmul(coeff_inv, np.reshape(rod_lengths_diff, (3, 1)))

            sp_state += np.reshape(sp_delta, 3)

            if self.verbose_output:
                print('swashplate state deltas')
                print(sp_delta)
                print('new swashplate state')
                print('roll: {:.2f}deg, pitch:{:.2f}deg, slide:{:.2f}mm'.format(
                    np.rad2deg(sp_state[0]), np.rad2deg(sp_state[1]), sp_state[2]))

        if not found_solution:
            raise RuntimeError('Failed to find solutions before max number of iterations')

        self.previous_sp_state = sp_state
        self.previous_servo_snaps = servo_snaps
        return sp_state
