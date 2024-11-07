import pygame, sys
from pygame.locals import *
import random
import time
import re

 
pygame.init()
 
FPS = 60
FramePerSec = pygame.time.Clock()
SecPerFrame = 1/FPS
 
# Cores
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
 


def loadImage(img):
	img = pygame.image.load(img)
	img.set_colorkey(img.get_at((0,0)))
	return img

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

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

	def getRect(self):
		return self.rect

	def draw(self, surface):
		if(self.image != None):
			surface.blit(self.image, self.rect)

	def move(self):
		pass
	def update(self):
		pass


 
class Enemy(Element):
    def __init__(self, img="crab.png"):
        super().__init__(img) 		
        self.direction = "DOWN"
        self.counter = 0
        self.counterMax = 50
        self.setPos(32,32)
        self.destNode = (1,1)
        self.lastNode = (1,1)
        self.position_history = []
        self.max_history_length = 20
        self.speed = random.randint(2,4) #pixels per frame
        
    def getNodePos(self):
        return self.lastNode

    def isSafeNode(self, x, y):
        if x < 0 or x >= len(MAP):
            return False
        if y < 0 or y >= len(MAP[0]):
            return False
        if(MAP[x][y] != 0): 
            return False
        return True
    
    def setNode(self, x, y):
        self.lastNode = (x, y)
        self.destNode = (x, y)
        self.setPos(x * self.rect[2], y * self.rect[3])

    
    def nextNode(self, player_pos):
        """Choose the next node based on the player’s position, with obstacle check and deviation if stuck."""
        px, py = player_pos
        ex, ey = self.lastNode

        # Check if the enemy is in a loop
        if self.isStuck(ex, ey):
            return self.escapePath(ex, ey)


        # Usual pathfinding logic to move towards the player
        dx = px - ex
        dy = py - ey

        preferred_directions = []

        if dx > 0:
            preferred_directions.append("RIGHT")
        elif dx < 0:
            preferred_directions.append("LEFT")

        if dy > 0:
            preferred_directions.append("DOWN")
        elif dy < 0:
            preferred_directions.append("UP")

        # Avoid returning to the previous position
        preferred_directions = [d for d in preferred_directions if not self.isOppositeDirection(d, ex, ey)]

        for direction in preferred_directions:
            if direction == "UP" and self.isSafeNode(ex, ey - 1):
                self.direction = "UP"
                return (ex, ey - 1)
            elif direction == "DOWN" and self.isSafeNode(ex, ey + 1):
                self.direction = "DOWN"
                return (ex, ey + 1)
            elif direction == "LEFT" and self.isSafeNode(ex - 1, ey):
                self.direction = "LEFT"
                return (ex - 1, ey)
            elif direction == "RIGHT" and self.isSafeNode(ex + 1, ey):
                self.direction = "RIGHT"
                return (ex + 1, ey)

        return self.escapePath(ex, ey)

    def isStuck(self, ex, ey):
        # Add the current position to the history
        self.position_history.append((ex, ey))
        
        # Limit the size of the history
        if len(self.position_history) > self.max_history_length:
            self.position_history.pop(0)
        
        # Check if the current position appears more than 3 times in the history, indicating that the enemy is stuck
        if self.position_history.count((ex, ey)) > 3:
            return True
        return False

    def isOppositeDirection(self, direction, ex, ey):
            """Check if the direction is opposite to the previous direction."""
            if self.direction == "UP" and direction == "DOWN":
                return True
            elif self.direction == "DOWN" and direction == "UP":
                return True
            elif self.direction == "LEFT" and direction == "RIGHT":
                return True
            elif self.direction == "RIGHT" and direction == "LEFT":
                return True
            return False

    def escapePath(self, ex, ey):
        """Find an alternative path when stuck, avoiding recently visited positions."""
        # Define the possible directions to move (UP, DOWN, LEFT, RIGHT)
        directions = [("UP", (ex, ey - 1)),
                    ("DOWN", (ex, ey + 1)),
                    ("LEFT", (ex - 1, ey)),
                    ("RIGHT", (ex + 1, ey))]
        
        # Filter the directions that are safe (no obstacles) and have not been visited recently
        safe_directions = []
        for direction, (nx, ny) in directions:
            if self.isSafeNode(nx, ny) and (nx, ny) not in self.position_history:
                safe_directions.append((direction, (nx, ny)))

        # If there are safe directions that have not been visited recently, choose the first available
        if safe_directions:
            chosen_direction, next_node = random.choice(safe_directions)
            self.direction = chosen_direction  # Update the enemy's direction
            return next_node

        # If all directions have been visited recently, choose the first safe one (even if already visited)
        for direction, (nx, ny) in directions:
            if self.isSafeNode(nx, ny):
                self.direction = direction  # Update the enemy's direction
                return (nx, ny)

        # If no options are available, return the current position (avoids a return error)
        return (ex, ey)



    def update(self, player_pos):
        mx = 0
        my = 0

        if self.destNode != None:
            d = self.destNode[0] * 32 - self.rect.center[0]
            mx = d
            d = self.destNode[1] * 32 - self.rect.center[1]
            my = d

        if mx == 0 and my == 0:
            self.destNode = self.nextNode(player_pos)
            if self.destNode is None:
                return
            else:
                self.lastNode = self.destNode

        mx = clamp(mx, -self.speed, self.speed)
        my = clamp(my, -self.speed, self.speed)

        self.rect.move_ip(mx, my)

class Player(Enemy):
    def __init__(self):
        super().__init__("player.png") 
        self.direction = "UP"
        self.newDir = None
        self.speed = 3

    def nextNode(self):
        if self.newDir is not None:
            if self.newDir == "UP":
                if self.isSafeNode(self.lastNode[0], self.lastNode[1]-1):
                    self.direction = self.newDir
                    self.newDir = None
                    return (self.lastNode[0], self.lastNode[1]-1)
            if self.newDir == "DOWN":
                if self.isSafeNode(self.lastNode[0], self.lastNode[1]+1):
                    self.direction = self.newDir
                    self.newDir = None
                    return (self.lastNode[0], self.lastNode[1]+1)
            if self.newDir == "LEFT":
                if self.isSafeNode(self.lastNode[0]-1, self.lastNode[1]):       
                    self.direction = self.newDir
                    self.newDir = None
                    return (self.lastNode[0]-1, self.lastNode[1])
            if self.newDir == "RIGHT":
                if self.isSafeNode(self.lastNode[0]+1, self.lastNode[1]):
                    self.direction = self.newDir
                    self.newDir = None
                    return (self.lastNode[0]+1, self.lastNode[1])	

        if self.direction == "UP":
            if self.isSafeNode(self.lastNode[0], self.lastNode[1]-1):
                return (self.lastNode[0], self.lastNode[1]-1)
        if self.direction == "DOWN":
            if self.isSafeNode(self.lastNode[0], self.lastNode[1]+1):
                return (self.lastNode[0], self.lastNode[1]+1)
        if self.direction == "LEFT":
            if self.isSafeNode(self.lastNode[0]-1, self.lastNode[1]):
                return (self.lastNode[0]-1, self.lastNode[1])
        if self.direction == "RIGHT":
            if self.isSafeNode(self.lastNode[0]+1, self.lastNode[1]):
                return (self.lastNode[0]+1, self.lastNode[1])	
			
        return None

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_UP]:
            self.newDir = "UP"
        elif pressed_keys[K_DOWN]:
            self.newDir = "DOWN"		 
        if pressed_keys[K_LEFT]:
            self.newDir = "LEFT"
        if pressed_keys[K_RIGHT]:
            self.newDir = "RIGHT"

        mx = 0
        my = 0	

        if self.destNode is not None:
            d = self.destNode[0] * 32 - self.rect.center[0]
            mx = d
            d = self.destNode[1] * 32 - self.rect.center[1]
            my = d

        if mx == 0 and my == 0:
            self.destNode = self.nextNode()
            if self.destNode is None:
                return
            else:
                self.lastNode = self.destNode

        mx = clamp(mx, -self.speed, self.speed)
        my = clamp(my, -self.speed, self.speed)

        self.rect.move_ip(mx, my)

 

class Obstacle(Element):
	def __init__(self, img):
		super().__init__(img) 
		self.setPos(400,300)


	

enemies = []
N_ENEMIES = 5
for i in range(N_ENEMIES):
	enemies.append(Enemy())

mapFromAscii = False #para mapas feitos em https://textik.com/

MAP = []
f = open("map_1.txt")
lines = f.readlines()
if('+' in lines[0]):
	mapFromAscii = True

for line in lines:
	if mapFromAscii:	
		line = re.sub(r"[^\s]", '1', line) #troca por '1' tudo que nao for espaco		                                   
		line = line.replace(' ', '0') #troca ' ' por 0
	row = []
	l = list(line)
	for c in l:
		if(c == '0'):
			row.append(0)
		if(c == '1'):
			row.append(1)
	if(len(row) > 3):
		MAP.append(list(row))

#transposta, para acessar no modelo MAP[x][y]
MAP = [[row[i] for row in MAP] for i in range(len(MAP[0]))]
    

px = len(MAP) -2
py = len(MAP[0])-2
P1 = Player()
P1.setNode(px, py)
MAP[px][py] = 0

# Screen information
SCREEN_WIDTH = len(MAP) * 32 - 32
SCREEN_HEIGHT = len(MAP[0]) * 32 - 32
 
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Crab")

background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
backImg = pygame.image.load("sand.png")
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



obstacles = []
nodes = []
i = 0
j = 0
while i < len(MAP):
	while j < len(MAP[0]):
		if(MAP[i][j] == 1):
			e = Element('block.png')
			e.setPos(i*32,j*32)
			obstacles.append(e)
		j = j + 1
	i = i + 1
	j=0



elements = [P1] + enemies + obstacles

#pygame.mixer.music.load("sound.mp3")
#pygame.mixer.music.play(-1)

paused = False

while True:	 
    for event in pygame.event.get():			  
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # Check if the ESC key was pressed
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            paused = not paused  # Toggle the pause state

    # If the game is paused, do not update the game logic
    if paused:
        # Display pause message on the screen, if desired
        font = pygame.font.Font(None, 36)
        text = font.render("Game Paused. Press ESC to resume.", True, (255, 255, 255))
        DISPLAYSURF.blit(text, (200, 250))
        pygame.display.flip()
        continue

    player_pos = P1.getNodePos()  # Current position of the player
    for e in elements:
        if isinstance(e, Enemy) and not isinstance(e, Player):
            e.update(player_pos)  # Pass the player's position to the enemies
        else:
            e.update()  # Update the player without passing the position


    DISPLAYSURF.blit(background, (0, 0))

    for e in elements:
        e.draw(DISPLAYSURF)

    l = P1.getRect().collidelistall(enemies)
    if len(l) > 0:
        time.sleep(2)
        P1.setNode(px, py)
        for i in range(N_ENEMIES):
            enemies[i].setNode(1, 1)

    pygame.display.update()
    FramePerSec.tick(FPS)


