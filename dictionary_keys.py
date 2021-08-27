"""
Definitions of strings to use as keys in dictionaries.
Meant to be used kind of like an Enum to avoid typos.
"""

position = 'position'
rotation_deg = 'rotation_deg'
x = 'x'
y = 'y'
z = 'z'
channel = 'channel'
collective = 'collective'
aileron = 'aileron'
elevator = 'elevator'
verbose = 'verbose'

channel_order = {
    aileron: 0,
    elevator: 1,
    collective: 2
}  # order in matrices
motor_order = {
    aileron: 1,
    elevator: 3,
    collective: 2
}  # order in ArduPilot

servos = 'servos'
lerp = 'lerp'
pwm_low = 'pwm_low'
pwm_high = 'pwm_high'
angle_low_deg = 'angle_low_deg'
angle_high_deg = 'angle_high_deg'
rod_length = 'rod_length'
lever_length = 'lever_length'
angle_trim_deg = 'angle_trim_deg'

swashplate = 'swashplate'
width = 'width'
front = 'front'
back = 'back'
sp_roll = 'sp_roll'
sp_pitch = 'sp_pitch'
sp_slide = 'sp_slide'

solver = 'solver'
tolerance = 'tolerance'
max_iterations = 'max_iterations'

rotorhub = 'rotorhub'

tail = 'tail'
pitch_gain = 'pitch_gain'
pitch_trim = 'pitch_trim'
pwm_trim = 'pwm_trim'
