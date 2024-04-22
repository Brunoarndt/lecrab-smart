
import pygame, sys
from pygame.locals import *
import random
import time
import spritesheet
 
pygame.init()
 
FPS = 60
FramePerSec = pygame.time.Clock()
 
# Cores
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
 
# Screen information
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
 
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("O Fugitivo")


#sprite_sheet_image = pygame.image.load('tilesheet.png').convert_alpha()
#sprite_sheet = spritesheet.SpriteSheet(sprite_sheet_image)

def loadImage():
	img = pygame.image.load("grama.png")
	img.set_colorkey((255,255,255))
	return img

background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
backImg = pygame.image.load("grama.png")
backRect = backImg.get_rect()
print(backRect)
w = 0
h = 0
while w < SCREEN_WIDTH:
	while h < SCREEN_HEIGHT:
		background.blit(backImg, (w,h))
		h = h + backRect[3]
	w = w + backRect[2]
	h = 0

class Element(pygame.sprite.Sprite):
	def __init__(self, img = None):
		super().__init__() 
		self.image = None
		if(img != None):
			self.image = loadImage(img)
			self.rect = self.image.get_rect()
			self.rect.center=(16,16)

	def setPos(self, x, y):
		self.rect.center = (x, y)

	def draw(self, surface):
		if(self.image != None):
			surface.blit(self.image, self.rect)


 
class Enemy(Element):
	def __init__(self):
		super().__init__() 
		self.image = pygame.image.load("enemy.png")
		self.image.set_colorkey((255,255,255))
		self.rect = self.image.get_rect()
		self.rect.center=(100,100) 
		
		self.direction = "DOWN"
		self.counter = 0
		self.counterMax = 50
 
	def move(self):
		dirs = ["UP", "DOWN", "LEFT", "RIGHT"]	
		
		mx = 0; my = 0;
		newd = False
		if(self.direction == "UP"):
			my = -5
		if(self.direction == "DOWN"):
			my = 5
		if(self.direction == "LEFT"):
			mx = -5
		if(self.direction == "RIGHT"):
			mx = 5	
		
		self.counter += 1
		if(self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT 
		or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH
		or self.counter > self.counterMax):
			self.counter = 0
			self.counterMax = random.randint(20,70)
			self.direction = dirs[random.randint(0,3)]
			mx = -mx
			my = -my		
			
		self.rect.move_ip(mx,my)
			
	
		
	
class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__() 
		self.image = pygame.image.load("player.png").convert()
		self.rect = self.image.get_rect()
		self.rect.center = (160, 520)
		
	def setPos(self, x, y):
		self.rect.center = (x, y)
	
	def getRect(self):
		return self.rect
 
	def update(self):
		pressed_keys = pygame.key.get_pressed()
		if pressed_keys[K_UP]:
			self.rect.move_ip(0, -5)
		if pressed_keys[K_DOWN]:
			self.rect.move_ip(0,5)
		 
		if self.rect.left > 0:
			if pressed_keys[K_LEFT]:
				self.rect.move_ip(-5, 0)
				  
		if self.rect.right < SCREEN_WIDTH:		
			if pressed_keys[K_RIGHT]:
				self.rect.move_ip(5, 0)

	def draw(self, surface):
		surface.blit(self.image, self.rect)	 
 
		 
P1 = Player()
E1 = Enemy()

enemies = []
N_ENEMIES = 3
for i in range(N_ENEMIES):
	enemies.append(Enemy())

while True:	 
	for event in pygame.event.get():			  
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
	P1.update()
	for i in range(N_ENEMIES):
		enemies[i].move()
	 
	#DISPLAYSURF.fill(WHITE)
	DISPLAYSURF.blit(background, (0,0))
	P1.draw(DISPLAYSURF)
	
	for i in range(N_ENEMIES):
		enemies[i].draw(DISPLAYSURF)
		
	l = P1.getRect().collidelistall(enemies)
	if(len(l) > 0):
		time.sleep(2)
		P1.setPos(int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2))
		for i in range(N_ENEMIES):
			enemies[i].setPos(100,100)
	
		 
	pygame.display.update()
	FramePerSec.tick(FPS)
