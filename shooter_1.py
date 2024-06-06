# Creating the player
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
class Soldier(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/characters/green/Idle/0.png')
		self.image = pygame.transform.scale_by(img, scale)
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)

	def draw(self):
		# Draw itself
		screen.blit(self.image, self.rect)
###################################################################################################################
# Create instances of the players
player = Soldier(200, 200, 3)
player2 = Soldier(400, 200, 5)
###################################################################################################################
run = True
while run:
	# -------------------------------------------------------------------------------------------------------------
	# Draw players
	player.draw()
	player2.draw()
	# -------------------------------------------------------------------------------------------------------------
	for event in pygame.event.get():
		# Quit game
		if event.type == pygame.QUIT:
			run = False

		# Keys pressed
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				run = False
	# -------------------------------------------------------------------------------------------------------------
	pygame.display.update()
###################################################################################################################
pygame.quit()