# Collision between player and tiles
###################################################################################################################
import pygame
import os
import random
import csv
import ctypes

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
GRAVITY = 0.75
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
level = 1
###################################################################################################################
# Define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False
###################################################################################################################
# Load images

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
###################################################################################################################
# Define font
font = pygame.font.SysFont('Futura', 30)
###################################################################################################################
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))
###################################################################################################################
def draw_bg():
	screen.fill(BG)
###################################################################################################################
class Soldier(pygame.sprite.Sprite):
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self, char_color, x, y, scale, speed, ammo, grenades):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.char_color = char_color
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cooldown = 0
		self.grenades = grenades
		self.health = 100
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
		# AI specific variables
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
	# -------------------------------------------------------------------------------------------------------------
	def update(self):
		self.update_animation()
		self.check_alive()
		# Update cooldown
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1
	# -------------------------------------------------------------------------------------------------------------
	def move(self, moving_left, moving_right):
		# Reset movement variables
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

		# Update rectangle position
		self.rect.x += dx
		self.rect.y += dy
	# -------------------------------------------------------------------------------------------------------------
	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			# Reduce ammo
			self.ammo -= 1
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
					self.update_action(1) # 1 -> run
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
		pygame.draw.rect(screen, RED, self.rect, 1)
		pygame.draw.rect(screen, BLACK, self.vision, 1)
###################################################################################################################
class World():
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self):
		self.obstacle_list = []
	# -------------------------------------------------------------------------------------------------------------
	def process_data(self, data):
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
						player = Soldier('green', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
						health_bar = HealthBar(10, 10, player.health, player.health)
					elif tile == 16: # Create enemies
						enemy = Soldier('red', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
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
			screen.blit(tile[0], tile[1])
###################################################################################################################
class Decoration(pygame.sprite.Sprite):
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
###################################################################################################################
class Water(pygame.sprite.Sprite):
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
###################################################################################################################
class Exit(pygame.sprite.Sprite):
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
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
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction
	# -------------------------------------------------------------------------------------------------------------
	def update(self):
		# Move bullet
		self.rect.x += (self.direction * self.speed)
		# Check if bullet has gone off screen
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()
		# Check for collision with level
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		# Check collision with characters
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
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
		self.rect.x += dx
		self.rect.y += dy

		# Countdown timer
		self.timer -= 1
		if self.timer <= 0:
			self.kill()
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
# Create empty tile list
world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)

# Load in level data and create world
with open(f'levels/level{level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)
			
world = World()
player, health_bar = world.process_data(world_data)
###################################################################################################################
run = True
while run:
	# -------------------------------------------------------------------------------------------------------------
	clock.tick(FPS)
	
	# Update background
	draw_bg()
	# -------------------------------------------------------------------------------------------------------------
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
	# -------------------------------------------------------------------------------------------------------------
	player.update()
	player.draw()

	for enemy in enemy_group:
		enemy.ai()
		enemy.update()
		enemy.draw()

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
	# -------------------------------------------------------------------------------------------------------------
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
			player.update_action(2) # 2 -> Jump
		elif moving_left or moving_right:
			player.update_action(1) # 1 -> Run
		else:
			player.update_action(0) # 0 -> Idle
		player.move(moving_left, moving_right)
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