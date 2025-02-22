"""
Program that uses Perlin Noise to procedurally generate grassy terrain using pygame

Packages required: perlin_noise

pip install perlin-noise

"""

from perlin_noise import PerlinNoise
from math import sqrt
import random
import pygame

SKY_BLUE  = (135, 206, 235)
GREEN = (0, 140, 0)
MAROON = (128, 0, 0)
STONE_GREY = (96, 92, 83)
DIRT_BROWN = (130, 100, 57)
BLACK = (0, 0, 0)
FPS = 60
BLOCK_SIZE = 25
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
RENDER_DISTANCE = 3 # Determines how much new map is generated in relation to the screen width after SCREEN_WIDTH * BLOCK_SIZE distance


class Block:
	def __init__(self, screen, x, y, color=(0, 140, 0)):
		self.screen = screen
		self.x = x
		self.y = y
		self.y_vel = 0

		self.center_x = self.x + BLOCK_SIZE // 2
		self.center_y = self.y + BLOCK_SIZE // 2

		self.color = color
		self.block_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
		self.block_surface.fill(self.color)
		self.block_rect = self.block_surface.get_rect()

	def __repr__(self):
		return f"Block({self.x}, {self.y})"

	def __eq__(self, other):
		return self.x == other.x and self.y == other.y

	def __hash__(self):
		return hash((self.x, self.y))

	def update(self, x, y, color):
		self.x = x
		self.y = y
		self.color = color
		self.block_surface.fill(self.color)
		self.block_rect.x = x
		self.block_rect.y = y
		self.y += self.y_vel

		self.center_x = self.x + BLOCK_SIZE / 2
		self.center_y = self.y + BLOCK_SIZE / 2


	def distance_from_block(self, block):
		dist_x = abs(self.center_x - block.center_x)
		dist_y = abs(self.center_y - block.center_y)

		euclid_dist = sqrt(dist_x ** 2 + dist_y ** 2)
		return euclid_dist

	def draw(self):
		self.screen.blit(self.block_surface, (self.x, self.y))


class TNT(Block):
	def __init__(self, screen, x, y, color=(128, 0, 0)):
		Block.__init__(self, screen, x, y, color=color)
		self.x = x
		self.y = y
		self.color = color
		self.ticks = 0








def generate_noise_map(octaves=4, seed=1, start=0, end=0):
	if end == 0:
		end = SCREEN_WIDTH

	noise = PerlinNoise(octaves=octaves, seed=seed)
	noise_map = []
	for spec in range(start, end + 1):
		noise_map.append(abs(noise(spec/1000)))

	return noise_map

def get_blocks(screen, noise_map, start_x=0, start_n=0):
	"""
	Max height = 3/4 of SCREEN_HEIGHT
	Min height = SCREEN_HEIGHT - BLOCK_SIZE
	"""
	blocks = []
	surface_blocks = []

	for gradient in noise_map:
		block_y = (gradient * 1000) + BLOCK_SIZE * 10

		if block_y > SCREEN_HEIGHT - BLOCK_SIZE:
			block_y = SCREEN_HEIGHT - BLOCK_SIZE

		block_y = round(block_y, 4)

		block = Block(screen, start_x, block_y)
		blocks.append(block)
		surface_blocks.append(block)
		start_n += 1

		# Draw the ground underneath the block
		ground_y = block_y
		for i in range(0, int(SCREEN_HEIGHT - block_y), BLOCK_SIZE):
			ground_y += BLOCK_SIZE
			randomizer = random.randint(1, 10)

			if randomizer == 1:
				blocks.append(Block(screen, start_x, ground_y, color=STONE_GREY))


			else:
				blocks.append(Block(screen, start_x, ground_y, color=DIRT_BROWN))

		start_x += BLOCK_SIZE

	return surface_blocks, blocks, start_n


if __name__ == "__main__":
	seed = random.randint(-99999, 99999)
	print (f"Seed: {str(seed)}")


	octaves = 20
	scroll_speed = 0
	noise_number = 0

	pygame.init()
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	clock = pygame.time.Clock()


	noise_map = generate_noise_map(octaves=octaves, seed=seed, start=noise_number, end=int((SCREEN_WIDTH // BLOCK_SIZE) * RENDER_DISTANCE))
	surface_blocks, blocks, noise_number = get_blocks(screen, noise_map)

	run = True

	while run:
		screen.fill(SKY_BLUE)
		clock.tick(FPS)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				break

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and scroll_speed == 0:
					seed = random.randint(-99999, 99999)
					print (f"Seed: {str(seed)}")
					noise_map = generate_noise_map(seed=seed, octaves=octaves, end=noise_number)
					surface_blocks, blocks, noise_number = get_blocks(screen, noise_map)

				elif event.key == pygame.K_q and scroll_speed == 0 and octaves > 1:
					octaves -= 1
					noise_map = generate_noise_map(seed=seed, octaves=octaves, end=noise_number)
					surface_blocks, blocks, noise_number = get_blocks(screen, noise_map)

				elif event.key == pygame.K_e and scroll_speed == 0:
					octaves += 1
					noise_map = generate_noise_map(seed=seed, octaves=octaves, end=noise_number)
					surface_blocks, blocks, noise_number = get_blocks(screen, noise_map)

				elif event.key == pygame.K_DOWN and scroll_speed != 0:
					scroll_speed -= 0.5

				elif event.key == pygame.K_UP:
					scroll_speed += 0.5


		for block in blocks:
			block.draw()
			block.x -= scroll_speed

			if block.x < -BLOCK_SIZE * 3 and block in blocks:
				blocks.remove(block)

		if blocks[-1].x <= SCREEN_WIDTH:
			start_noise_number = noise_number - (SCREEN_WIDTH // BLOCK_SIZE) # Noise number from first block on the left side of the screen
			end_noise_number = int(noise_number + (SCREEN_WIDTH // BLOCK_SIZE) * RENDER_DISTANCE) # Noise number for the block RENDER_DISTANCEx screen width away

			noise_map = generate_noise_map(seed=seed, octaves=octaves, start=start_noise_number, end=end_noise_number)
			surface_blocks, blocks, noise_number = get_blocks(screen, noise_map, start_x=0, start_n=start_noise_number)


		pygame.display.set_caption(str(round(clock.get_fps())))
		pygame.display.flip()
		pygame.display.update()

	pygame.quit()
	quit()
