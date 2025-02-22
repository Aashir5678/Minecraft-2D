from map_generator import *
from random import randint
import pygame

SKY_BLUE  = (135, 206, 235)
DUSK_LIGHT_ORANGE = (255, 216, 184)
STEVE_BROWN = (169,125,100)
GREEN = (0, 140, 0)
DIRT_BROWN = (130, 100, 57)
MAROON = (128, 0, 0)
STONE_GREY = (96, 92, 83)
TURQUOISE = (12,150,103)
SUN_ORANGE = (244, 48, 55)
SUN_YELLOW = (252, 212, 64)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLOCKS = [GREEN, DIRT_BROWN, STONE_GREY, MAROON]

BLOCK_SIZE = 25
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
GRAVITY = 0.5
SUN_SIZE = 100
BLOCK_GRAVITY = False # Determines whether blocks are affected by gravity, WIP
EDIT_RANGE = 3 # Determines how much range the player has in terms of placing / destroying blocks
RENDER_DISTANCE = 3 # Determines how much new map is generated in relation to the screen width after SCREEN_WIDTH * BLOCK_SIZE distance
JUMP_CONSTANT = 0.5 # BLOCK_SIZE * JUMP_CONSTANT = change in y value of player when jumping per frame
SPRINT_MULTIPLIER = 1.6 # How fast the player sprints, a factor of the player's walking speed sprint_speed = ((BLOCK_SIZE // 5) * SPRINT_MULTIPLIER)
TICKS_TILL_BOOM = 60 * 4 # Determines how long it takes for tnt to blow up after being placed
TNT_RADIUS = 5 # How many blocks out tnt will destroy blocks
FPS = 60


class Player:
	def __init__(self, screen, x, y):
		self.screen = screen
		self.x = x
		self.y = y
		self.vel_x = 0
		self.vel_y = 0
		self.acc_y = GRAVITY

		self.block_to_right = False
		self.block_to_left = False
		self.head_rect = pygame.Rect(self.x, self.y - BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
		self.torso_rect = pygame.Rect(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE)
		self.block_holding_rect = pygame.Rect(self.x + BLOCK_SIZE // 2, self.y, BLOCK_SIZE * 0.8, BLOCK_SIZE * 0.8)
		self.block_holding = GREEN

	def on_block(self, block):
		return (abs(block.x - self.x) < BLOCK_SIZE and abs(self.y + BLOCK_SIZE - block.y) <= BLOCK_SIZE + 0.5)

	def in_range(self, block):
		return abs(block.x - self.x) <= BLOCK_SIZE * EDIT_RANGE and abs(block.y - self.y) <= BLOCK_SIZE * EDIT_RANGE

	def update(self):
		self.vel_y += self.acc_y

		if (self.vel_x > 0 and not self.block_to_right) or (self.vel_x < 0 and not self.block_to_left):
			self.x += self.vel_x

		self.y += self.vel_y

		self.head_rect = pygame.Rect(self.x, self.y - BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
		self.torso_rect = pygame.Rect(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE)

		if self.block_holding is not None:
			self.block_holding_rect = pygame.Rect(self.x + (BLOCK_SIZE // 2), self.y, BLOCK_SIZE * 0.8, BLOCK_SIZE * 0.8)

	def draw(self):
		pygame.draw.rect(self.screen, STEVE_BROWN, self.head_rect)
		pygame.draw.rect(self.screen, TURQUOISE, self.torso_rect)

		if self.block_holding is not None:
			pygame.draw.rect(self.screen, self.block_holding, self.block_holding_rect)


def get_suraface_blocks(blocks):
	surface_blocks = []
	block_x = -1

	for block in blocks:
		if block.x != block_x:
			surface_blocks.append(block)

		block_x = block.x

	return surface_blocks


def draw_grid_lines(screen):
	for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
		pygame.draw.line(screen, BLACK, (x, 0), (x, SCREEN_HEIGHT))

	for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
		pygame.draw.line(screen, BLACK, (0, y), (SCREEN_WIDTH, y))


def draw_sun(screen, center_x, center_y, time_of_day):
	if time_of_day != "night":
		sun_rect = pygame.Rect(center_x - (SUN_SIZE // 2), center_y - (SUN_SIZE // 2), SUN_SIZE, SUN_SIZE)
		pygame.draw.rect(screen, SUN_ORANGE, sun_rect)
		pygame.draw.rect(screen, SUN_YELLOW, (sun_rect.x + 5, sun_rect.y + 5, SUN_SIZE - 10, SUN_SIZE - 10))

	else:
		pygame.draw.rect(screen, WHITE, (center_x - (SUN_SIZE // 2), center_y - (SUN_SIZE // 2), SUN_SIZE, SUN_SIZE))

seed = randint(-99999, 99999)
# seed = 3432
print (f"Seed: {str(seed)}")

octaves = 20
noise_number = 0
scroll_speed = 0
noise_map = generate_noise_map(octaves=octaves, seed=seed, start=noise_number, end=int((SCREEN_WIDTH // BLOCK_SIZE) * RENDER_DISTANCE))

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
surface_blocks, blocks, noise_number = get_blocks(screen, noise_map)
blocks_dict = {}

for block in blocks:
	blocks_dict[(block.x, round(block.y))] = block

fps_font = pygame.font.SysFont('Arial', 30)
mouse_x, mouse_y = 0, 0

blocks_placed = []
player = Player(screen, BLOCK_SIZE * 5, -BLOCK_SIZE * 2)
block_index = 0
player.block_holding = BLOCKS[block_index]

clock = pygame.time.Clock()
sky_color = list(SKY_BLUE)
time_of_day = "daytime"
sun_y = 10
time_multiplier = 1

run = True
d_pressed = False
a_pressed = False
jumping = False
sprinting = False

from time import time
time_taken_blocks = []
time_taken = []

while run:
	start = time()
	clock.tick(FPS)
	try:
		screen.fill(tuple(sky_color))

	except ValueError:
		sky_color = list(SKY_BLUE)


	if sky_color[0] < 255 and time_of_day == "daytime":
		sky_color[0] += 0.05 * time_multiplier

	if sky_color[1] < 216 and time_of_day == "daytime":
		sky_color[1] += 0.01 * time_multiplier

	if sky_color[2] > 184 and time_of_day == "daytime":
		sky_color[2] -= 0.02 * time_multiplier


	if (round(sky_color[0]), round(sky_color[1]), round(sky_color[2])) == DUSK_LIGHT_ORANGE:
		time_of_day = "dusk"

	if time_of_day == "dusk" and sky_color[2] > 0:
		sky_color[1] -= 0.01 * time_multiplier
		sky_color[2] -= 0.02 * time_multiplier

	draw_sun(screen, SCREEN_WIDTH * 0.75, sun_y, time_of_day)
	sun_y += 0.04 * time_multiplier

	if sun_y > SCREEN_HEIGHT and time_of_day == "night":
		sun_y = 10
		time_of_day = "daytime"
		sky_color = list(SKY_BLUE)

	elif sun_y > SCREEN_HEIGHT and time_of_day == "dusk":
		sun_y = 10
		time_of_day = "night"
		sky_color = [27, 30, 35]

	pygame.display.set_caption("Minecraft 2D")

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
			break

		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1: # Left click
				mouse_x, mouse_y = pygame.mouse.get_pos()

				for block in blocks:
					if block.block_rect.collidepoint((mouse_x, mouse_y)) and player.in_range(block):
						blocks.remove(block)
						if block in blocks_placed:
							blocks_placed.remove(block)

						if (block.x, round(block.y)) in blocks_dict and BLOCK_GRAVITY:
							del blocks_dict[(block.x, round(block.y))]


			elif event.button == 3: # Right click
				mouse_x, mouse_y = pygame.mouse.get_pos()
				block_x = mouse_x - (mouse_x % BLOCK_SIZE)
				block_y = mouse_y - (mouse_y % BLOCK_SIZE)
				block_placed = Block(screen, block_x, block_y, color=player.block_holding)
				right = (block_x + BLOCK_SIZE + BLOCK_SIZE / 2, block_y)
				left = (block_x - BLOCK_SIZE / 2, block_y)
				top = (block_x, block_y - BLOCK_SIZE / 2)
				bottom = (block_x, block_y + BLOCK_SIZE)

				for block in blocks:
					if block.block_rect.collidepoint(top) or block.block_rect.collidepoint(bottom) or block.block_rect.collidepoint(left) or block.block_rect.collidepoint(right):
						break

				else:
					continue

				mouse_x = 0
				mouse_y = 0

				if player.block_holding == MAROON:
					block_placed = TNT(screen, block_x, block_y)

				blocks_placed.append(block_placed)
				if BLOCK_GRAVITY:
					blocks_dict[(block_placed.x, round(block_placed.y))] = block_placed

		elif event.type == pygame.MOUSEWHEEL:
			if event.y < 0:
				block_index += 1
				if block_index > len(BLOCKS) - 1:
					block_index = 0

			else:
				block_index -= 1
				if block_index < 0:
					block_index = len(BLOCKS) - 1

			player.block_holding = BLOCKS[block_index]



	keys = pygame.key.get_pressed()

	if keys[pygame.K_1]:
		player.block_holding = GREEN

	elif keys[pygame.K_2]:
		player.block_holding = DIRT_BROWN

	elif keys[pygame.K_3]:
		player.block_holding = STONE_GREY

	elif keys[pygame.K_4]:
		player.block_holding = MAROON

	elif keys[pygame.K_t]:
		time_multiplier += 0.1

	elif keys[pygame.K_r]:
		time_multiplier -= 0.1


	if keys[pygame.K_LCTRL]:
		sprinting = True

	else:
		sprinting = False

	if keys[pygame.K_SPACE] and not jumping:
		player.vel_y += -BLOCK_SIZE * JUMP_CONSTANT
		jumping = True
		player.update()

	a_pressed = keys[pygame.K_a]
	d_pressed = keys[pygame.K_d]

	if a_pressed:
		if not sprinting:
			player.vel_x = -BLOCK_SIZE // 5

		else:
			player.vel_x = (-BLOCK_SIZE // 5) * SPRINT_MULTIPLIER


	if d_pressed:
		if not sprinting:
			player.vel_x = BLOCK_SIZE // 5

		else:
			player.vel_x = (BLOCK_SIZE // 5) * SPRINT_MULTIPLIER

	if not a_pressed and not d_pressed:
		player.vel_x = 0


	for block in blocks_placed:
		if block not in blocks:
			blocks.insert(0, block)

		if isinstance(block, TNT):
			block.ticks += 1

			if block.color == MAROON and block.ticks % 15 == 0:
				block.update(block.x, block.y, WHITE)

			elif block.ticks % 30 == 0:
				block.update(block.x, block.y, MAROON)

			if block.ticks >= TICKS_TILL_BOOM:
				for destroyed_block in (blocks + blocks_placed):
					if isinstance(destroyed_block, TNT):
						continue

					if block.distance_from_block(destroyed_block) <= TNT_RADIUS * BLOCK_SIZE and destroyed_block in blocks:
						blocks.remove(destroyed_block)

					elif destroyed_block in blocks_placed:
						blocks_placed.remove(destroyed_block)

					if (destroyed_block.x, round(destroyed_block.y)) in blocks_dict and BLOCK_GRAVITY:
						del blocks_dict[(destroyed_block.x, round(destroyed_block.y))]


				if block in blocks:
					blocks.remove(block)

				if block in blocks_placed:
					blocks_placed.remove(block)

				if (block.x, round(block.y)) in blocks_dict and BLOCK_GRAVITY:
					del blocks_dict[(block.x, round(block.y))]

				block.ticks = 0

		if BLOCK_GRAVITY:
			pass

	start_blocks = time()
	for block in blocks:
		if scroll_speed != 0 and BLOCK_GRAVITY:
			try:
				del blocks_dict[(block.x, round(block.y))]

			except KeyError as e:
				print (e)
				print (blocks_dict.keys())
				quit()
			block.update(block.x - scroll_speed, block.y, block.color)
			blocks_dict[(block.x, round(block.y))] = block

		elif scroll_speed != 0:
			block.update(block.x - scroll_speed, block.y, block.color)

		if block.x < -BLOCK_SIZE * SCREEN_WIDTH * 2:
			blocks.remove(block)

			if (block.x, round(block.y)) in blocks_dict and BLOCK_GRAVITY:
				del blocks_dict[(block.x, round(block.y))]

		if (player.on_block(block) and player.vel_y > 0) or (abs(player.x - block.x) <= BLOCK_SIZE and abs(player.y - block.y) <= BLOCK_SIZE) and block in surface_blocks: # Stop player phasing through blocks
			player.y = block.y - BLOCK_SIZE
			player.vel_y = 0
			jumping = False


		if block.block_rect.colliderect(player.torso_rect):
			if block.x > player.x:
				player.block_to_right = True

			else:
				player.block_to_left = True

		else:
			player.block_to_right = False
			player.block_to_left = False


		## WIP
		if BLOCK_GRAVITY:
			if block.y + BLOCK_SIZE < SCREEN_HEIGHT and (block.x, block.y + BLOCK_SIZE) not in blocks_dict:
				block.y_vel += GRAVITY

			else:
				block.y_vel = 0


		block.draw()

	time_taken_blocks.append(time() - start_blocks)


	
	
	if blocks[-1].x < SCREEN_WIDTH:
		start_noise_number = noise_number - (SCREEN_WIDTH // BLOCK_SIZE) # Noise number from first block on the left side of the screen
		end_noise_number = int(noise_number + (SCREEN_WIDTH // BLOCK_SIZE) * RENDER_DISTANCE) # Noise number for the block RENDER_DISTANCEx screen width away

		noise_map = generate_noise_map(seed=seed, octaves=octaves, start=start_noise_number, end=end_noise_number)
		surface_blocks, blocks, noise_number = get_blocks(screen, noise_map, start_x=0, start_n=start_noise_number)

		if BLOCK_GRAVITY:
			blocks_dict = {}

			for block in blocks:
				blocks_dict[(block.x, round(block.y))] = block
		
	
	# player.vel_y += GRAVITY

	# Scroll the screen whenever the player gets half way across

	if player.x > SCREEN_WIDTH // 4 and player.vel_x > 0:
		scroll_speed = player.vel_x
		player.vel_x = 0
		d_pressed = True

	elif player.x < SCREEN_WIDTH // 4 and player.vel_x < 0:
		scroll_speed = player.vel_x
		player.vel_x = 0
		a_pressed = True

	if scroll_speed > 0 and player.vel_x == 0 and not d_pressed:
		scroll_speed = 0

	elif scroll_speed < 0 and player.vel_x == 0 and not a_pressed:
		scroll_speed = 0

	if player.y - BLOCK_SIZE > SCREEN_HEIGHT: # Reset player if they fall off the end of the map
		player.x = SCREEN_WIDTH // 2
		player.y = -BLOCK_SIZE * 2

	player.update()
	fps_text_surface = fps_font.render(str(round(clock.get_fps(), 1)), False, (0, 0, 0))
	screen.blit(fps_text_surface, (5, 5))
	# draw_grid_lines(screen)

	player.draw()
	pygame.display.flip()
	pygame.display.update()

	time_taken.append(time() - start)


total_average_time_taken = round(sum(time_taken) / len(time_taken), 6)
total_average_blocks = round(sum(time_taken_blocks) / len(time_taken_blocks), 6)

print (f"Average time taken per frame: {str(total_average_time_taken)}")
print (f"Average time taken to iterate through every block in one frame: {str(total_average_blocks)}")
print (f"Average % of game loop spent in blocks loop: {str(round(total_average_blocks / total_average_time_taken * 100, 2))}")
pygame.quit()
quit()