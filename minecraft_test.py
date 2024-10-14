from map_generator import Block, generate_noise_map, get_blocks
from random import randint
from math import sqrt
import pygame

SKY_BLUE  = (135, 206, 235)
STEVE_BROWN = (169,125,100)
GREEN = (0, 140, 0)
DIRT_BROWN = (130, 100, 57)
MAROON = (128, 0, 0)
STONE_GREY = (96, 92, 83)
TURQUOISE = (12,150,103)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

BLOCK_SIZE = 30
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
GRAVITY = 0.5
EDIT_RANGE = 3 # Determines how much range the player has in terms of placing / destroying blocks
RENDER_DISTANCE = 3 # Determines how much new map is generated in relation to the screen width after SCREEN_WIDTH * BLOCK_SIZE distance
JUMP_CONSTANT = 0.5 # BLOCK_SIZE * JUMP_CONSTANT = change in y value of player when jumping per frame
SPRINT_MULTIPLIER = 1.6
FPS = 60


class Player:
	def __init__(self, screen, x, y):
		self.screen = screen
		self.x = x
		self.y = y
		self.vel_x = 0
		self.vel_y = 0
		self.acc_y = GRAVITY

		self.head_rect = pygame.Rect(self.x, self.y - BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
		self.torso_rect = pygame.Rect(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE)
		self.block_holding_rect = pygame.Rect(self.x + BLOCK_SIZE // 2, self.y, BLOCK_SIZE * 0.8, BLOCK_SIZE * 0.8)
		self.block_holding = GREEN

	def on_block(self, block):
		return (abs(block.x - self.x) < BLOCK_SIZE and abs(self.y + BLOCK_SIZE - block.y) <= BLOCK_SIZE + 0.5)

	def in_left_block(self, block):
		return (self.x - block.x) < 0 and ((abs(self.head_rect.y - block.y) < BLOCK_SIZE))

	def in_right_block(self, block):
		return (self.x + BLOCK_SIZE - block.x) > 0 and ((abs(self.head_rect.y - block.y) < BLOCK_SIZE))

	def in_range(self, block):
		return abs(block.x - self.x) <= BLOCK_SIZE * EDIT_RANGE and abs(block.y - self.y) <= BLOCK_SIZE * EDIT_RANGE

	def update(self):
		self.vel_y += self.acc_y

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


def get_nearest_block_to_point(point_x, point_y, blocks_dict):
	smallest_dist = float("inf")
	smallest_dist_x = float("inf")
	smallest_dist_y = float("inf")
	closest_block = None

	for block in blocks_dict.keys():
		dist_x = abs(point_x - (block.x + (BLOCK_SIZE // 2)))
		dist_y = abs(point_y - (block.y + (BLOCK_SIZE //2)))

		euclid_dist = sqrt(dist_x ** 2 + dist_y ** 2)

		if euclid_dist < smallest_dist:
			smallest_dist_x = dist_x
			smallest_dist_y = dist_y

			smallest_dist = euclid_dist
			closest_block = block


	return closest_block, smallest_dist_x, smallest_dist_y


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
fps_font = pygame.font.SysFont('Arial', 30)
mouse_x, mouse_y = 0, 0

blocks_placed = []
blocks_dict = {}

for block in blocks:
	blocks_dict[block] = "block"



for block in surface_blocks:
	blocks_dict[block] = "surface_block"

player = Player(screen, BLOCK_SIZE * 5, -BLOCK_SIZE * 2)

clock = pygame.time.Clock()
run = True
d_pressed = False
a_pressed = False
jumping = False
sprinting = False
destroy = False

while run:
	clock.tick(FPS)
	screen.fill(SKY_BLUE)
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

						try:
							del blocks_dict[block]

						except KeyError:
							pass

				destroy = True

			elif event.button == 3: # Right click
				mouse_x, mouse_y = pygame.mouse.get_pos()
				# block_x = (mouse_x // BLOCK_SIZE) * BLOCK_SIZE
				# block_y = (mouse_y // BLOCK_SIZE) * BLOCK_SIZE
				block_x = mouse_x - (mouse_x % BLOCK_SIZE)
				block_y = mouse_y - (mouse_y % BLOCK_SIZE)
				block_placed = Block(screen, block_x, block_y, color=player.block_holding)
				right = (block_x + BLOCK_SIZE + BLOCK_SIZE / 2, block_y)
				left = (block_x - BLOCK_SIZE / 2, block_y)
				top = (block_x, block_y - BLOCK_SIZE / 2)
				bottom = (block_x, block_y + BLOCK_SIZE)

				for block in blocks:
					if block.block_rect.collidepoint(top) or block.block_rect.collidepoint(bottom) or block.block_rect.collidepoint(left) or block.block_rect.collidepoint(right):
						blocks_placed.append(block_placed)
						blocks_dict[block_placed] = "placed_block"
						break
				# block_distance_x, block_distance_y = block_placed.distance_from(block_x, block_y)
				# closest_block, dist_x, dist_y = get_nearest_block_to_point(mouse_x, mouse_y, blocks_dict)

				# if player.in_range(block_placed) and dist_x <= BLOCK_SIZE and dist_y <= BLOCK_SIZE and block_placed not in blocks_dict:
				# 	# block_above = (block_placed.x, block_placed.y - BLOCK_SIZE)
				# 	# block_below = (block_placed.x, block_placed.y + BLOCK_SIZE)
				# 	# block_right = (block_placed.x + BLOCK_SIZE, block_placed.y)
				# 	# block_left = (block_placed.x - BLOCK_SIZE, block_placed.y)

				# 	# print (block_placed.x)
				# 	# print (block_placed.y)

				# 	# if block_above in blocks_dict or block_below in blocks_dict or block_right in blocks_dict or block_left in blocks_dict:
					
				# 	blocks_placed.append(block_placed)
				# 	blocks_dict[block_placed] = "placed_block"

				else:
					print ("not added")

				blocks_dict[block_placed] = "placed_block"
				mouse_x = 0
				mouse_y = 0
				destroy = False


	keys = pygame.key.get_pressed()

	if keys[pygame.K_1]:
		player.block_holding = GREEN

	elif keys[pygame.K_2]:
		player.block_holding = DIRT_BROWN

	elif keys[pygame.K_3]:
		player.block_holding = STONE_GREY

	elif keys[pygame.K_4]:
		player.block_holding = MAROON

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
			blocks_dict[block] = "placed_block"

	for block in blocks:
		block.update(block.x - scroll_speed, block.y)

		if block.x < -BLOCK_SIZE * SCREEN_WIDTH * 4 and block in blocks:
			blocks.remove(block)
			del blocks_dict[block]

		if (player.on_block(block) and player.vel_y > 0) or (abs(player.x - block.x) <= BLOCK_SIZE and abs(player.y - block.y) <= BLOCK_SIZE) and block in surface_blocks: # Stop player phasing through blocks
			# if (player.x + BLOCK_SIZE) > block.x:
			# 	print ("continue")
			# 	player.vel_x = 0
			# 	player.x -= BLOCK_SIZE
			# 	continue

			# if player.on_block(block) and player.vel_y > 0:
			# 	print ("on block func")

			# else:
			# 	print (abs(player.y - block.y))
			# 	print  ("bad code")

			# if player.in_right_block(block):
			# 	player.vel_x = 0
			# 	scroll_speed = 0
			# 	player.x = block.x - BLOCK_SIZE * 1.5
			# 	player.update()
			# 	continue

			# elif player.in_left_block(block):
			# 	player.vel_x = 0
			# 	player.x = block.x + BLOCK_SIZE * 1.5
			# 	scroll_speed = 0
			# 	player.update()
			# 	continue

			player.y = block.y - BLOCK_SIZE
			player.vel_y = 0
			jumping = False

		# elif abs(player.x + BLOCK_SIZE - block.x) <= BLOCK_SIZE and abs(player.y - BLOCK_SIZE - block.y) <= BLOCK_SIZE and player.vel_x != 0:
		# 	print ("aight")
		# 	player.vel_x = 0
		# 	player.x = block.x - BLOCK_SIZE

		# if mouse_x != 0 and mouse_y != 0 and destroy:
		# 	# mouse_distance_x, mouse_distance_y = block.distance_from(mouse_x, mouse_y)
		# 	closest_block, dist_x, dist_y = get_nearest_block_to_point(mouse_x, mouse_y, blocks_dict)
		# 	if mouse_distance_x < BLOCK_SIZE and mouse_distance_y < BLOCK_SIZE and player.in_range(block): # Destroy block if in player range
		# 		blocks.remove(block)
		# 		if block in blocks_placed:
		# 			blocks_placed.remove(block)
				
		# 		del blocks_dict[block]

		# 		mouse_x = 0
		# 		mouse_y = 0
		# 		destory = False

		# elif not destroy and mouse_x != 0 and mouse_y != 0:
		# 	block_x = (mouse_x // BLOCK_SIZE) * BLOCK_SIZE
		# 	block_y = (mouse_y // BLOCK_SIZE) * BLOCK_SIZE
		# 	block_placed = Block(screen, block_x, block_y)
		# 	print (f"{str(block_x)}, {str(block_y)}")
		# 	block_distance_x, block_distance_y = block_placed.distance_from(block_x, block_y)

		# 	if player.in_range(block_placed) and block_distance_x < BLOCK_SIZE and block_distance_y < BLOCK_SIZE and block_placed not in blocks_dict:
		# 		# block_above = (block_placed.x, block_placed.y - BLOCK_SIZE)
		# 		# block_below = (block_placed.x, block_placed.y + BLOCK_SIZE)
		# 		# block_right = (block_placed.x + BLOCK_SIZE, block_placed.y)
		# 		# block_left = (block_placed.x - BLOCK_SIZE, block_placed.y)

		# 		# print (block_placed.x)
		# 		# print (block_placed.y)

		# 		# if block_above in blocks_dict or block_below in blocks_dict or block_right in blocks_dict or block_left in blocks_dict:
				
		# 		blocks_placed.append(block_placed)
		# 		blocks_dict[block_placed] = "placed_block"

		# 	else:
		# 		print ("not added")

		# 	blocks_dict[block_placed] = "placed_block"
		# 	mouse_x = 0
		# 	mouse_y = 0

		block.draw()


	if blocks[-1].x <= SCREEN_WIDTH:
		start_noise_number = noise_number - (SCREEN_WIDTH // BLOCK_SIZE) # Noise number from first block on the left side of the screen
		end_noise_number = int(noise_number + (SCREEN_WIDTH // BLOCK_SIZE) * RENDER_DISTANCE) # Noise number for the block RENDER_DISTANCEx screen width away

		noise_map = generate_noise_map(seed=seed, octaves=octaves, start=start_noise_number, end=end_noise_number)
		surface_blocks, blocks, noise_number = get_blocks(screen, noise_map, start_x=0, start_n=start_noise_number)

		for block in blocks:
			blocks_dict[block] = "block"

		for block in surface_blocks:
			blocks_dict[block] = "surface_block"

	
	
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
	fps_text_surface = fps_font.render(str(round(clock.get_fps())), False, (0, 0, 0))
	screen.blit(fps_text_surface, (5, 5))
	# draw_grid_lines(screen)

	player.draw()
	pygame.display.update()

pygame.quit()
quit()