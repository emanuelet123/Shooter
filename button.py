import pygame 

# Button class
class Button():
	def __init__(self,x, y, image, scale):
		self.image = pygame.transform.scale_by(image, scale)
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False

		# Get mouse position
		pos = pygame.mouse.get_pos()

		# Check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		# Draw button
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action