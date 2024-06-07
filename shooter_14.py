# Add player colors
# Now the game doesn't have to load a fixed number of columns csv file. Can load any level size 
# Perfect pixel collision
###################################################################################################################
import pygame
from pygame import mixer
import os
import random
import ctypes
import csv
import button
###################################################################################################################
mixer.init()
pygame.init()
###################################################################################################################
# Get device screen size
user32 = ctypes.windll.user32

# Declaring variables
SCREEN_WIDTH, SCREEN_HEIGHT = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')
###################################################################################################################
# Set framerate
clock = pygame.time.Clock()
FPS = 60
###################################################################################################################
# Define game variables
GRAVITY = 0.6
SCROLL_THRESH = 400
ROWS = 16
COLS = 0 # Get by get_number_of_cols_of_level() | default 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
###################################################################################################################
# Get number of levels
MAX_LEVELS = 0
for file in os.listdir("levels"):
	if file.endswith(".csv"):
		MAX_LEVELS += 1
###################################################################################################################
# Define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False
###################################################################################################################
# Load music and sounds
pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)

jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.5)

shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.5)

grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.5)
###################################################################################################################
# Load images

# Button images
start_img = pygame.image.load('img/buttons/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/buttons/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/buttons/restart_btn.png').convert_alpha()

# Background
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()

# Store tiles in a list
tiles_type = 'cave'
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/tiles/{tiles_type}/{x}.png')
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)

# Bullet
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()

# Grenade
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()

# Pick up boxes
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()

item_boxes = {
	'Health'	: health_box_img,
	'Ammo'		: ammo_box_img,
	'Grenade'	: grenade_box_img
}
###################################################################################################################
# Define colors
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

# Define font
font = pygame.font.SysFont('Futura', 30)
###################################################################################################################
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))
###################################################################################################################
def draw_bg():
	screen.fill(BG)
	width = sky_img.get_width()
	for x in range(5):
		# Adding paralex scrolling - each image has its factor of scrolling, a multiplier
		screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
		screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
		screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
		screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))
###################################################################################################################
def get_number_of_cols_of_level():
	with open(f'levels/level{level}_data.csv', newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		return len(next(reader))
###################################################################################################################
# Function to create empty tile list
def create_empty_tile_list():
	COLS = get_number_of_cols_of_level()
	world_data = []
	for _ in range(ROWS):
		r = [-1] * COLS
		world_data.append(r)
	return world_data

# Function to load in level data and create world
def load_level_and_create_world():
	with open(f'levels/level{level}_data.csv', newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for x, row in enumerate(reader):
			for y, tile in enumerate(row):
				world_data[x][y] = int(tile)

	world = World()
	player, health_bar = world.process_data(world_data)
	return world, player, health_bar

# Function to reset level
def reset_level():
	# Clear all sprite groups
	enemy_group.empty()
	bullet_group.empty()
	grenade_group.empty()
	explosion_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	water_group.empty()
	exit_group.empty()

	return create_empty_tile_list()
###################################################################################################################
class Soldier(pygame.sprite.Sprite):
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self, char_color, x, y, scale, speed, ammo, grenades, health):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.char_color = char_color
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cooldown = 0
		self.grenades = grenades
		self.health = health
		self.max_health = self.health
		self.direction = 1
		self.vel_y = 0
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		# Ai specific variables
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, TILE_SIZE * 4, 20)
		self.idling = False
		self.idling_counter = 0
		
		# Load all images for the players
		animation_types = ['idle', 'run', 'jump', 'death']
		for animation in animation_types:
			# Reset temporary list of images
			temp_list = []
			# Count number of files in the folder
			num_of_frames = len(os.listdir(f'img/characters/{self.char_color}/{animation}'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'img/characters/{self.char_color}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale_by(img, scale)
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.mask = pygame.mask.from_surface(self.image)
	# -------------------------------------------------------------------------------------------------------------
	def move(self, moving_left, moving_right):
		# Reset movement variables
		screen_scroll = 0
		dx = 0
		dy = 0

		# Assign movement variables if moving left or right
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1

		# Jump
		if self.jump and not self.in_air:
			self.vel_y = -11
			self.jump = False
			self.in_air = True
			jump_fx.play()

		# Apply gravity
		self.vel_y += GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		# Check for collision
		for tile in world.obstacle_list:
			# Check collision in the x direction
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
				# If the ai has hit a wall then make it turn around
				if self.char_color == 'red':
					self.direction *= -1
					self.move_counter = 0
			# Check for collision in the y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				# Check if below the ground, i.e. jumping
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				# Check if above the ground, i.e. falling
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom

		# Check for collision between player and water
		if pygame.sprite.spritecollide(self, water_group, False):
			# Check for pixel collision
			if pygame.sprite.spritecollide(self, water_group, False, pygame.sprite.collide_mask):
				self.health = 0

		# Check for collision between player and exit
		level_complete = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			# Check for pixel collision
			if pygame.sprite.spritecollide(self, exit_group, False, pygame.sprite.collide_mask):
				level_complete = True

		# Check if fallen off the map
		if self.rect.bottom > SCREEN_HEIGHT:
			self.health = 0


		# Check if going off the edges of the screen
		if self.char_color != 'red':
			if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
				dx = 0

		# Update rectangle position
		self.rect.x += dx
		self.rect.y += dy

		# Update scroll based on player position
		if self.char_color != 'red':
			if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
				or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
				self.rect.x -= dx
				screen_scroll = -dx # Screen has to scroll in the opposite way of player, while player stays stationary

		return screen_scroll, level_complete
	# -------------------------------------------------------------------------------------------------------------
	def update(self):
		self.update_animation()
		self.check_alive()
		# Update shoot_cooldown
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1
	# -------------------------------------------------------------------------------------------------------------
	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 10
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			# Reduce ammo
			self.ammo -= 1
			shot_fx.play()
	# -------------------------------------------------------------------------------------------------------------
	def ai(self):
		if self.alive and player.alive:
			if not self.idling and random.randint(1, 200) == 1:
				self.update_action(0) # 0 -> Idle
				self.idling = True
				self.idling_counter = 50
			# Check if the ai in near the player
			if self.vision.colliderect(player.rect):
				# Stop running and face the player
				self.update_action(0) # 0 -> Idle
				# Shoot
				self.shoot()
			else:
				if not self.idling:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1) # 1 -> Run
					self.move_counter += 1
					# Update ai vision as the enemy moves
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False
	
		# Scroll
		self.rect.x += screen_scroll
	# -------------------------------------------------------------------------------------------------------------
	def update_animation(self):
		# Update animation
		ANIMATION_COOLDOWN = 100
		# Update image depending on current frame
		self.image = self.animation_list[self.action][self.frame_index]
		# Check if enough time has passed since the last update
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		# If the animation has run out the reset back to the start
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0
	# -------------------------------------------------------------------------------------------------------------
	def update_action(self, new_action):
		# Check if the new action is different to the previous one
		if new_action != self.action:
			self.action = new_action
			# Update the animation settings
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()
	# -------------------------------------------------------------------------------------------------------------
	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)
	# -------------------------------------------------------------------------------------------------------------
	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
		# pygame.draw.rect(screen, RED, self.rect, 1)
		# pygame.draw.rect(screen, WHITE, self.vision, 1)
###################################################################################################################
class World():
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self):
		self.obstacle_list = []
	# -------------------------------------------------------------------------------------------------------------
	def process_data(self, data):
		self.level_length = len(data[0])
		# Iterate through each value in level data file
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					tile_data = (img, img_rect)
					if tile >= 0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10:
						water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
						water_group.add(water)
					elif tile >= 11 and tile <= 14:
						decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)
					elif tile == 15: # Create player
						player = Soldier('yellow', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5, 100)
						health_bar = HealthBar(10, 10, player.health, player.health)
					elif tile == 16: # Create enemies
						enemy = Soldier('red', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0, 100)
						enemy_group.add(enemy)
					elif tile == 17: # Create ammo box
						item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 18: # Create grenade box
						item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 19: # Create health box
						item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 20: # Create exit
						exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)

		return player, health_bar
	# -------------------------------------------------------------------------------------------------------------
	def draw(self):
		for tile in self.obstacle_list:
			tile[1][0] += screen_scroll
			screen.blit(tile[0], tile[1])
###################################################################################################################
class Decoration(pygame.sprite.Sprite):
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
	# -------------------------------------------------------------------------------------------------------------
	def update(self):
		self.rect.x += screen_scroll
###################################################################################################################
class Water(pygame.sprite.Sprite):
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
	# -------------------------------------------------------------------------------------------------------------
	def update(self):
		self.rect.x += screen_scroll
###################################################################################################################
class Exit(pygame.sprite.Sprite):
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
	# -------------------------------------------------------------------------------------------------------------
	def update(self):
		self.rect.x += screen_scroll
###################################################################################################################
class ItemBox(pygame.sprite.Sprite):
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
	# -------------------------------------------------------------------------------------------------------------
	def update(self):
		# Scroll
		self.rect.x += screen_scroll
		# Check if the player has picked up the box
		if pygame.sprite.collide_rect(self, player):
			# Check what kind of box it was
			if self.item_type == 'Health':
				player.health += 25
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == 'Ammo':
				player.ammo += 15
			elif self.item_type == 'Grenade':
				player.grenades += 3
			# Delete the item box
			self.kill()
###################################################################################################################
class HealthBar():
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health
	# -------------------------------------------------------------------------------------------------------------
	def draw(self, health):
		# Update with new health
		self.health = health
		# Calculate health ratio
		ratio = self.health / self.max_health
		pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
		pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))
###################################################################################################################
class Bullet(pygame.sprite.Sprite):
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 15
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction
	# -------------------------------------------------------------------------------------------------------------
	def update(self):
		# Move bullet
		self.rect.x += (self.direction * self.speed) + screen_scroll
		# Check if bullet has gone off screen
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()
		# Check for collision with level
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		# Check collision between bullets and player
		if pygame.sprite.spritecollide(player, bullet_group, False):
			# Check for pixel collision
			if pygame.sprite.spritecollide(self, bullet_group, False, pygame.sprite.collide_mask):
				if player.alive:
					player.health -= 5
					self.kill()

		for enemy in enemy_group:
			# Check collision between bullets and enemies
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				# Check for pixel collision
				if pygame.sprite.spritecollide(self, bullet_group, False, pygame.sprite.collide_mask):
					if enemy.alive:
						enemy.health -= 25
						self.kill()
###################################################################################################################
class Grenade(pygame.sprite.Sprite):
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 100
		self.vel_y = -11
		self.speed = 7
		self.image = grenade_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.direction = direction
	# -------------------------------------------------------------------------------------------------------------
	def update(self):
		self.vel_y += GRAVITY
		dx = self.direction * self.speed
		dy = self.vel_y

		# Check for collision with level
		for tile in world.obstacle_list:
			# Check collision with walls
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				self.direction *= -1
				dx = self.direction * self.speed
			# Check for collision in the y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				self.speed = 0
				# Check if below the ground, i.e. thrown up
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				# Check if above the ground, i.e. falling
				elif self.vel_y >= 0:
					self.vel_y = 0
					dy = tile[1].top - self.rect.bottom	

		# Update grenade position
		self.rect.x += dx + screen_scroll
		self.rect.y += dy

		# Countdown timer
		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			grenade_fx.play()
			explosion = Explosion(self.rect.x, self.rect.y, 0.5)
			explosion_group.add(explosion)
			# Do damage to anyone that is nearby
			# 1º layer of damage to player
			if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 1 and \
				abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 1:
				player.health -= 100
			# 2º layer of damage to player
			elif abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
				abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
				player.health -= 50
			# 3º layer of damage to player
			elif abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 3 and \
				abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 3:
				player.health -= 25

			for enemy in enemy_group:
				# 1º layer of damage to enemy
				if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 1 and \
					abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 1:
					enemy.health -= 100
				# 2º layer of damage to enemy
				elif abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
					abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
					enemy.health -= 50
				# 3º layer of damage to enemy
				elif abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 3 and \
					abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 3:
					enemy.health -= 25
###################################################################################################################
class Explosion(pygame.sprite.Sprite):
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
			img = pygame.transform.scale_by(img, scale)
			self.images.append(img)
		self.frame_index = 0
		self.image = self.images[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0
	# -------------------------------------------------------------------------------------------------------------
	def update(self):
		# Scroll
		self.rect.x += screen_scroll

		EXPLOSION_SPEED = 4
		# Update explosion amimation
		self.counter += 1

		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.frame_index += 1
			# If the animation is complete then delete the explosion
			if self.frame_index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.frame_index]
###################################################################################################################
class ScreenFade():
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self, direction, color, speed):
		self.direction = direction
		self.color = color
		self.speed = speed
		self.fade_counter = 0
	# -------------------------------------------------------------------------------------------------------------
	def fade(self):
		fade_complete = False
		self.fade_counter += self.speed

		if self.direction == 1: # Whole screen fade
			pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT)) # Left
			pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) # Right
			pygame.draw.rect(screen, self.color, (0, 0 - self.fade_counter * (1/(SCREEN_WIDTH/SCREEN_HEIGHT)), SCREEN_WIDTH, SCREEN_HEIGHT // 2)) # Up
			pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT // 2 + self.fade_counter * (1/(SCREEN_WIDTH/SCREEN_HEIGHT)), SCREEN_WIDTH, SCREEN_HEIGHT)) # Down

		if self.direction == 2: # Vertical screen fade down
			pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))

		if self.fade_counter >= SCREEN_HEIGHT:
			fade_complete = True

		return fade_complete
###################################################################################################################
# Create screen fades
intro_fade = ScreenFade(1, BLACK, 8)
death_fade = ScreenFade(2, PINK, 10)
###################################################################################################################
# Create buttons
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)
###################################################################################################################
# Create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
###################################################################################################################
# Create world
world_data = create_empty_tile_list()

world, player, health_bar = load_level_and_create_world()
###################################################################################################################
run = True
while run:
	# -------------------------------------------------------------------------------------------------------------
	clock.tick(FPS)
	# -------------------------------------------------------------------------------------------------------------
	if not start_game:
		# Draw menu
		screen.fill(BG)
		# Add buttons

		# Draw start button and check if it was clicked
		if start_button.draw(screen):
			start_game = True
			start_intro = True

		# Draw exit button and check if it was clicked
		if exit_button.draw(screen):
			run = False
	else:
		# Update background
		draw_bg()
		# Draw world map
		world.draw()
		# Show player health
		health_bar.draw(player.health)
		# Show ammo
		draw_text('AMMO: ', font, WHITE, 10, 35)
		for x in range(player.ammo):
			screen.blit(bullet_img, (90 + (x * 10), 40))
		# Show grenades
		draw_text('GRENADES: ', font, WHITE, 10, 60)
		for x in range(player.grenades):
			screen.blit(grenade_img, (135 + (x * 15), 60))
		# ---------------------------------------------------------------------------------------------------------
		player.update()
		player.draw()
		# ---------------------------------------------------------------------------------------------------------
		for enemy in enemy_group:
			enemy.ai()
			enemy.update()
			enemy.draw()
		# ---------------------------------------------------------------------------------------------------------
		# Update and draw groups
		bullet_group.update()
		grenade_group.update()
		explosion_group.update()
		item_box_group.update()
		decoration_group.update()
		water_group.update()
		exit_group.update()
		bullet_group.draw(screen)
		grenade_group.draw(screen)
		explosion_group.draw(screen)
		item_box_group.draw(screen)
		decoration_group.draw(screen)
		water_group.draw(screen)
		exit_group.draw(screen)
		# ---------------------------------------------------------------------------------------------------------
		# Show intro
		if start_intro:
			# Call fade effect 1 and check if it's completed
			if intro_fade.fade():
				# Restart fade variables
				start_intro = False
				intro_fade.fade_counter = 0
		# ---------------------------------------------------------------------------------------------------------
		# Update player actions
		if player.alive:
			# Shoot bullets
			if shoot:
				player.shoot()
			# Throw grenades
			elif grenade and not grenade_thrown and player.grenades > 0:
				grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
				 			player.rect.top, player.direction)
				grenade_group.add(grenade)
				# Reduce grenades
				player.grenades -= 1
				grenade_thrown = True
			if player.in_air:
				player.update_action(2) # 2 -> jump
			elif moving_left or moving_right:
				player.update_action(1) # 1 -> run
			else:
				player.update_action(0)#0: idle
			screen_scroll, level_complete = player.move(moving_left, moving_right)
			bg_scroll -= screen_scroll
			# Check if player has completed the level
			if level_complete:
				start_intro = True

				# Add 1 level
				level += 1

				# Bring screen to the beggining of game
				bg_scroll = 0

				# Reset level assets - enemies, item_boxes, bullets, grenades, ...
				world_data = reset_level()
				if level <= MAX_LEVELS:
					world, player, health_bar = load_level_and_create_world()
		else:
			# Stop any scrolling
			screen_scroll = 0

			# Call fade effect 2 and check if it's completed
			if death_fade.fade():
				# Draw restart button and check if it was clicked
				if restart_button.draw(screen):
					
					# Restart fade variables
					death_fade.fade_counter = 0
					start_intro = True
					
					# Bring screen to the beggining of game
					bg_scroll = 0

					# Reset level assets - enemies, item_boxes, bullets, grenades, ...
					world_data = reset_level()

					# Load in level data and create world
					world, player, health_bar = load_level_and_create_world()
	# -------------------------------------------------------------------------------------------------------------
	for event in pygame.event.get():
		# Quit game
		if event.type == pygame.QUIT:
			run = False
		# Keys pressed
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_w:
				shoot = True
			if event.key == pygame.K_q:
				grenade = True
			if event.key == pygame.K_SPACE and player.alive:
				player.jump = True
			if event.key == pygame.K_ESCAPE:
				run = False

		# Keys released
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_w:
				shoot = False
			if event.key == pygame.K_q:
				grenade = False
				grenade_thrown = False
	# -------------------------------------------------------------------------------------------------------------
	pygame.display.update()
###################################################################################################################
pygame.quit()