import pygame
import button
import csv
import ctypes

pygame.init()
###################################################################################################################
clock = pygame.time.Clock()
FPS = 60
###################################################################################################################
# Game window
# Get device screen size
user32 = ctypes.windll.user32

# Declaring variables
LOWER_MARGIN = 100
SIDE_MARGIN = 300
SCREEN_WIDTH, SCREEN_HEIGHT = user32.GetSystemMetrics(0) - SIDE_MARGIN, user32.GetSystemMetrics(1) - LOWER_MARGIN

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Shooter Level Editor')
###################################################################################################################
# Define game variables
ROWS = 16
COLS = 150 # Ajust acoording to the size of game you want | deafult is 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
level = 0
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1
###################################################################################################################
# Load images
pine1_img = pygame.image.load('img/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/background/sky_cloud.png').convert_alpha()

# Store tiles in a list
tiles_type = 'cave'
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/tiles/{tiles_type}/{x}.png').convert_alpha()
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)

save_img = pygame.image.load('img/buttons/save_btn.png').convert_alpha()
load_img = pygame.image.load('img/buttons/load_btn.png').convert_alpha()
###################################################################################################################
# Define colors
GREEN = (144, 201, 120)
WHITE = (255, 255, 255)
RED = (200, 25, 25)
###################################################################################################################
# Define font
font = pygame.font.SysFont('Futura', 30)
###################################################################################################################
# Create empty tile list
world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)

# Create ground
for tile in range(0, COLS):
	world_data[ROWS - 1][tile] = 0
###################################################################################################################
# Function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))
###################################################################################################################
# Create function for drawing background
def draw_bg():
	screen.fill(GREEN)
	width = sky_img.get_width()
	for x in range(4):
		screen.blit(sky_img, ((x * width) - scroll * 0.5, 0))
		screen.blit(mountain_img, ((x * width) - scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
		screen.blit(pine1_img, ((x * width) - scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
		screen.blit(pine2_img, ((x * width) - scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))
###################################################################################################################
# Draw grid
def draw_grid():
	# Vertical lines
	for c in range(COLS + 1):
		pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
	# Horizontal lines
	for c in range(ROWS + 1):
		pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))
###################################################################################################################
# Function for drawing the world tiles
def draw_world():
	for y, row in enumerate(world_data):
		for x, tile in enumerate(row):
			if tile >= 0:
				screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))
###################################################################################################################
# Create buttons
save_button = button.Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN - 50, save_img, 1)
load_button = button.Button(SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT + LOWER_MARGIN - 50, load_img, 1)

# Make a button list
button_list = []
button_col = 0
button_row = 0

for i in range(len(img_list)):
	tile_button = button.Button(SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_row + 50, img_list[i], 1)
	button_list.append(tile_button)
	button_col += 1
	if button_col == 3:
		button_row += 1
		button_col = 0
###################################################################################################################
run = True
while run:
	# -------------------------------------------------------------------------------------------------------------
	clock.tick(FPS)
	# -------------------------------------------------------------------------------------------------------------
	draw_bg()
	draw_grid()
	draw_world()

	draw_text(f'Level: {level}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
	draw_text('Press UP or DOWN to change level', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)
	# -------------------------------------------------------------------------------------------------------------
	# Save and load data
	if save_button.draw(screen):
		# Save level data
		with open(f'levels/level{level}_data.csv', 'w', newline='') as csvfile:
			writer = csv.writer(csvfile, delimiter = ',')
			for row in world_data:
				writer.writerow(row)

	if load_button.draw(screen):
		# Load in level data
		# Reset scroll back to the start of the level
		scroll = 0
		with open(f'levels/level{level}_data.csv', newline='') as csvfile:
			reader = csv.reader(csvfile, delimiter = ',')
			for x, row in enumerate(reader):
				for y, tile in enumerate(row):
					world_data[x][y] = int(tile)
				
	# Draw tile panel and tiles
	pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))
	# -------------------------------------------------------------------------------------------------------------
	# Choose a tile
	button_count = 0
	for button_count, i in enumerate(button_list):
		if i.draw(screen):
			current_tile = button_count
	
	# Highlight the selected tile
	pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)
	# -------------------------------------------------------------------------------------------------------------
	# Scroll the map
	if scroll_left and scroll > 0:
		scroll -= 5 * scroll_speed
	if scroll_right and scroll < (COLS * TILE_SIZE) - SCREEN_WIDTH:
		scroll += 5 * scroll_speed
	# -------------------------------------------------------------------------------------------------------------
	# Add new tiles to the screen
	# Get mouse position
	pos = pygame.mouse.get_pos()
	x = (pos[0] + scroll) // TILE_SIZE
	y = pos[1] // TILE_SIZE
	# -------------------------------------------------------------------------------------------------------------
	# Check that the coordinates are within the tile area
	if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
		# Update tile value
		if pygame.mouse.get_pressed()[0] == 1:
			try: # Avoid error when clicking outside limits
				if world_data[y][x] != current_tile:
					world_data[y][x] = current_tile
			except:
				pass
		if pygame.mouse.get_pressed()[2] == 1:
			try: # Avoid error when clicking outside limits
				world_data[y][x] = -1
			except:
				pass
	# -------------------------------------------------------------------------------------------------------------
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		# Keyboard presses
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:
				level += 1
			if event.key == pygame.K_s and level > 0:
				level -= 1
			if event.key == pygame.K_a:
				scroll_left = True
			if event.key == pygame.K_d:
				scroll_right = True
			if event.key == pygame.K_LSHIFT:
				scroll_speed = 5
			if event.key == pygame.K_ESCAPE:
				run = False

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				scroll_left = False
			if event.key == pygame.K_d:
				scroll_right = False
			if event.key == pygame.K_LSHIFT:
				scroll_speed = 1
	# -------------------------------------------------------------------------------------------------------------
	pygame.display.update()
###################################################################################################################	
pygame.quit()

