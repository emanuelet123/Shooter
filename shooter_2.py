# Keyboard input
###################################################################################################################
import pygame
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
# Player action variables
moving_left = False
moving_right = False
###################################################################################################################
# Colors
BG = (144, 201, 120)
RED = (255, 0, 0)

def draw_bg():
	screen.fill(BG)
###################################################################################################################
class Soldier(pygame.sprite.Sprite):
	# -------------------------------------------------------------------------------------------------------------
	def __init__(self, char_color, x, y, scale, speed):
		pygame.sprite.Sprite.__init__(self)
		self.char_color = char_color
		self.speed = speed
		self.direction = 1
		self.flip = False
		img = pygame.image.load(f'img/characters/{self.char_color}/idle/0.png')
		self.image = pygame.transform.scale_by(img, scale)
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

		# Update rectangle position
		self.rect.x += dx
		self.rect.y += dy
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

	# Draw player and enemy
	player.draw()
	enemy.draw()

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