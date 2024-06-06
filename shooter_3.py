# Sprite animation
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
# Game variables
GRAVITY = 0.75

# Player action variables
moving_left = False
moving_right = False
###################################################################################################################
# Colors
BG = (144, 201, 120)
RED = (255, 0, 0)

def draw_bg():
	screen.fill(BG)
	pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))
###################################################################################################################
class Soldier(pygame.sprite.Sprite):
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self, char_color, x, y, scale, speed):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.char_color = char_color
		self.speed = speed
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
		animation_types = ['idle', 'run', 'jump']
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
	def draw(self):
		# Draw itself
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
		pygame.draw.rect(screen, RED, self.rect, 1)
###################################################################################################################
# Create player and enemy
player = Soldier('green', 200, 200, 3, 5)
enemy = Soldier('red', 400, 200, 3, 5)
###################################################################################################################
run = True
while run:
	# -------------------------------------------------------------------------------------------------------------
	clock.tick(FPS)

	# Draw background
	draw_bg()
	# -------------------------------------------------------------------------------------------------------------
	# Update player animation
	player.update_animation()
	# Draw player and enemy
	player.draw()
	enemy.draw()
	# -------------------------------------------------------------------------------------------------------------
	# Update player actions
	if player.alive:
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
	# -------------------------------------------------------------------------------------------------------------
	pygame.display.update()
###################################################################################################################
pygame.quit()