# Context + Potential New Features

This project was made over the course of 5 months from March 2024 to August 2024 using entirely the Python pygame and perlin-noise libraries. The next thing I wanted to add was block gravity for the TNT block at the very least if possible, but doing this and keeping the FPS high is hard due to the double for loop (for every block check if there is another block under it if not increase it's y velocity), which raises the time complexity from O(B) to O(B^2) where B is the combined length of the blocks list and blocks placed list. I'm sure there is a way to do this using a dictionary or hash set but at this point in time i'm not sure how I would, any help would be appreciated. At this point of time the i've pushed this project to the side.

# Requirements

To run this project, you must have pygame and the perlin_noise library installed. If you have pip installed, run the following two commands in the command prompt

pip install pygame

pip install perlin-noise

## minecraft.py

This is the minecraft clone itself which includes procederally generated terrain using the Perlin Noise algorithm, to generate random values with smooth transitions, which is then mapped to the y values of the surface blocks. 

Controls:
- Use a and d to move forwards and backwards
- Space to jump
- Holding the left control button while moving will make you move faster.
- You can also place and destroy blocks using the left and right click.
- Use the scroll wheel or numbers 1-4 to change the block you are holding.

The fourth maroon block is TNT, and when placed, blows up after 240 ticks or 4 seconds (this can be adjusted in the minecraft.py file by changing the TICKS_TILL_BOOM constant), and it destroys every
block in a 5 block radius (can also be changed by editing TNT_RADIUS constant).

There is also a day and night cycle with a sun and moon. The sun affects the color of thes sky as it sets. The duration
of one day can be shortened by pressing t, or increased by pressing r.

## map_generator.py

Running this file will simply create a window with the randomly smooth generated terrain. Pressing the up arrow will increase the speed of the camera, and the down arrow will slow it down. 

The following commands will only work if the camera isn't moving:

- Pressing space will generate a new random world
- Pressing e will increase the octave of the current world with the same seed (stretch it out)
- Pressing q will decrease the octave with the same seed (compress it)
  
