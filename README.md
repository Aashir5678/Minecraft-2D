# Requirements

To run this project, you must have pygame and the perlin_noise library installed. If you have pip installed, run the following two commands in the command prompt

pip install pygame
pip install perlin-noise

## minecraft.py

This is the minecraft clone itself which includes procederally generated terrain using the Perlin Noise algorithm, to generate random values with smooth transitions. Use a and d to move
forwards and backwards and space to jump, and by holding the left control button while moving you can move faster. You can also place and destroy blocks using the left and right click. Use the scroll wheel or numbers 1-4 to change the block you are holding.
The fourth block is TNT, and when placed, blows up after 240 ticks or 4 seconds (this can be adjusted in the minecraft.py file by changing the TICKS_TILL_BOOM constant), and it destroys every
block in a 5 block radius (can also be changed by editing TNT_RADIUS constant). There is also a day and night cycle with a sun and moon. The sun affects the color of thes sky as it sets. The duration
of one day can be shortened by pressing t, or increase the duration by pressing r.

## map_generator.py

