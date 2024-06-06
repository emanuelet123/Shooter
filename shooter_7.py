# Collectible items
###################################################################################################################
import pygame
import os
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
TILE_SIZE = 40
###################################################################################################################
# Define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False
###################################################################################################################
# Load images
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

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))
###################################################################################################################
def draw_bg():
	screen.fill(BG)
	pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))
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

		# Check collision with floor
		if self.rect.bottom + dy > 300:
			dy = 300 - self.rect.bottom
			self.in_air = False

		# Update rectangle position
		self.rect.x += dx
		self.rect.y += dy
	# -------------------------------------------------------------------------------------------------------------
	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			# Reduce ammo
			self.ammo -= 1
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
		self.direction = direction
	# -------------------------------------------------------------------------------------------------------------
	def update(self):
		self.vel_y += GRAVITY
		dx = self.direction * self.speed
		dy = self.vel_y

		# Check collision with floor
		if self.rect.bottom + dy > 300:
			dy = 300 - self.rect.bottom
			self.speed = 0

		# Check collision with walls
		if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
			self.direction *= -1
			dx = self.direction * self.speed

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
###################################################################################################################
# Create item boxes
item_box = ItemBox('Health', 100, 260)
item_box_group.add(item_box)
item_box = ItemBox('Ammo', 400, 260)
item_box_group.add(item_box)
item_box = ItemBox('Grenade', 500, 260)
item_box_group.add(item_box)
###################################################################################################################
# Create player and enemies
player = Soldier('green', 200, 200, 3, 5, 20, 5)
health_bar = HealthBar(10, 10, player.health, player.health)

enemy = Soldier('red', 400, 200, 3, 5, 20, 0)
enemy2 = Soldier('red', 300, 300, 3, 5, 20, 0)
enemy_group.add(enemy)
enemy_group.add(enemy2)
###################################################################################################################
run = True
while run:
	# -------------------------------------------------------------------------------------------------------------
	clock.tick(FPS)

	draw_bg()
	# -------------------------------------------------------------------------------------------------------------
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
		enemy.update()
		enemy.draw()

	# Update and draw groups
	bullet_group.update()
	grenade_group.update()
	explosion_group.update()
	item_box_group.update()
	bullet_group.draw(screen)
	grenade_group.draw(screen)
	explosion_group.draw(screen)
	item_box_group.draw(screen)
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
			player.update_action(2) # 2 -> jump
		elif moving_left or moving_right:
			player.update_action(1) # 1 -> run
		else:
			player.update_action(0) # 0 -> idle
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