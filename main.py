import math
import numpy
import pygame
import random
import copy

shapes = [
"""
	###
	H##
	H##
	HH#
""",
"""
	H##
	H##
	H##
	H##
""",
"""
	HH#
	HH#
	###
	###
""",
"""
	HH#
	H##
	H##
	###
""",
"""
	H##
	HH#
	#H#
	###
""",
"""
	###
	###
	#H#
	HHH
"""
]

class graphicHandler:
	
	def __init__(self):
		pygame.init()
		pygame.display.set_caption("Tetris")
		#pygame.display.set_icon()
		
		pygame.key.set_repeat(200, 50)
		
		self.clock = pygame.time.Clock()
		self.width = 401
		self.height = 801
		self.screen = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
		self.virtualWidth = 10
		self.virtualHeight = 20
		self.virtualScreen = pygame.Surface([self.virtualWidth, self.virtualHeight])
		self.deltaTime = 0.016
		self.FPS = 60
		self.targetFPS = 60
		self.running = False
		
		self.clearMask = pygame.surfarray.array2d(self.virtualScreen)
		self.prevMask = self.clearMask[:]
		self.currMask = None
		self.diffMask = None
	
		self.board = board()
		
		file = "pathToTetrisTheme.wav"
		pygame.mixer.init(48000)
		pygame.mixer.music.load(file)
		pygame.mixer.music.set_volume(0.1)
		pygame.mixer.music.play(loops = -1)

	def start(self):
		self.render()
	
	def stop(self):
		self.running = False
	
	def render(self):
		self.running = True
		
		while self.running:
			self.input()
			
			self.board.update(self.deltaTime)
			shapes = self.board.drawShapes()
			
			for shape in shapes:
				for point in shape.rectangles:
					pygame.draw.rect(self.virtualScreen, shape.color, [point, [1, 1]])
					
			self.screen.blit(pygame.transform.scale(self.virtualScreen, (self.width, self.height)), (0, 0))

			self.updateMask()
			
			if self.diffMask != []:
				pygame.display.update(self.diffMask)
				
			self.clock.tick(self.targetFPS)
			self.deltaTime = self.clock.get_time() / 1000.0
			self.FPS = self.clock.get_fps()
			
			self.virtualScreen.fill((0, 0, 0))

	def updateMask(self):
		self.currMask = pygame.surfarray.array2d(self.virtualScreen)
		self.diffMask = []
		
		w = self.width / self.virtualWidth
		h = self.height / self.virtualHeight

		for y in range(self.virtualHeight):
			for x in range(self.virtualWidth):
				if self.currMask[x][y] != self.prevMask[x][y]:
					self.diffMask.append(pygame.Rect((x * w), (y * h), w * 2, h * 2))
		
		self.prevMask = self.currMask[:]
	
	def input(self):
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				self.stop()
				pygame.quit()
			elif event.type == pygame.VIDEORESIZE:
				self.width = event.dict['size'][0]
				self.height = event.dict['size'][1]
				self.screen = pygame.display.set_mode(event.dict['size'], pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
				
				pygame.display.update()
				self.prevMask = self.clearMask[:]

		self.board.input(events)

class piece():
	def __init__(self, shape):
		self.shape = shape
		self.position = [0.0, 0.0]
		self.rectangles = []
		self.color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
		
		self.rectanglesFromShape()
		self.movePosition([0, 0])
		
	def rectanglesFromShape(self, sideSize = 4):
		lines = self.shape.splitlines()
		y = 0
		for line in lines:
			x = 0
			if line != "":
				for char in line:
					if char != "\t":
						if char == "H":
							self.rectangles.append([x, y])
						x += 1
				y += 1

		self.position = self.rectangles[0]
		
	def movePosition(self, pos):
		diffX = pos[0] - self.position[0]
		diffY = pos[1] - self.position[1]
		self.position = pos

		for i in range(len(self.rectangles)):
			self.rectangles[i][0] += diffX
			self.rectangles[i][1] += diffY

	def drawShape(self):
		return self.rectangles
	
		
class board():
	def __init__(self):
		self.board = []
		
		self.currentPiece = self.getRandomPiece()
		self.board.append(self.currentPiece)
		self.downCounter = 0.75

	def getRandomPiece(self):
		shape = random.choice(shapes)
		return piece(shape)
		
	def movePiece(self, pos):
		newPositions = []
		
		diffX = pos[0] - self.currentPiece.position[0]
		diffY = pos[1] - self.currentPiece.position[1]
		
		for i in range(len(self.currentPiece.rectangles)):
			x = self.currentPiece.rectangles[i][0] + diffX
			y = self.currentPiece.rectangles[i][1] + diffY
			newPositions.append([x, y])
			
		if self.collisionCheck(newPositions, pos):
			self.currentPiece.movePosition(pos)

	def collisionCheck(self, newShape, newPos):
		for shape in self.board:
			if shape != self.currentPiece:
				for rect in shape.rectangles:
					for newRect in newShape:
						if rect == newRect:
							if self.currentPiece.position[1] < newPos[1]:
								self.placePiece()
								self.checkBoard()
							return False
			
		for rect in newShape:
			if rect[0] < 0 or rect[0] >= 10:
				return False
			
			if rect[1] < 0:
				return False
			
			if rect[1] >= 20:
				self.placePiece()
				self.checkBoard()
				return False
			
		return True
	
	def drawShapes(self):
		return self.board
	
	def placePiece(self):
		self.board.remove(self.currentPiece)
		self.board.append(copy.deepcopy(self.currentPiece))
		self.currentPiece = self.getRandomPiece()
		self.board.append(self.currentPiece)
		
	def checkBoard(self):
		counter = 0
		
		for i in range(20):
			for j in range(10):
				for shape in self.board:
					for rect in shape.rectangles:
						if rect == [j, i]:
							counter += 1
			if counter == 10:
				self.removePiecesAt(i)
				
			counter = 0
			
			
	def removePiecesAt(self, pos):
		for i in range(len(self.board)):
			for j in range(len(self.board[i].rectangles)-1, -1, -1):
				if self.board[i].rectangles[j][1] == pos:
					self.board[i].rectangles.pop(j)
					
		self.moveEverythingOver(pos)
		
	def moveEverythingOver(self, pos):
		for i in range(len(self.board)):
			for j in range(len(self.board[i].rectangles)-1, -1, -1):
				if self.board[i].rectangles[j][1] < pos:
					self.board[i].rectangles[j][1] += 1
	
	def update(self, deltaTime):
		self.downCounter -= deltaTime
		
		if self.downCounter <= 0:
			self.movePiece([self.currentPiece.position[0], self.currentPiece.position[1] + 1])
			self.downCounter = 0.75
			
	def input(self, events):
		for event in events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					self.movePiece([self.currentPiece.position[0] -1, self.currentPiece.position[1]])
				elif event.key == pygame.K_RIGHT:
					self.movePiece([self.currentPiece.position[0] + 1, self.currentPiece.position[1]])
				elif event.key == pygame.K_UP:
					pass
				#self.movePiece([self.currentPiece.position[0], self.currentPiece.position[1] - 1])
				elif event.key == pygame.K_DOWN:
					self.movePiece([self.currentPiece.position[0], self.currentPiece.position[1] + 1])

					
	def rotate(self, radian):
		s = math.sin(radian)
		c = math.cos(radian)
		
		center = self.getCenter()
		
		for i in range(len(self.currentPiece.rectangles)):
			self.currentPiece.rectangles[i][0] -= center[0]
			self.currentPiece.rectangles[i][1] -= center[1]
			
			xnew = self.currentPiece.rectangles[i][0] * c - self.currentPiece.rectangles[i][1] * s
			ynew = self.currentPiece.rectangles[i][0] * s + self.currentPiece.rectangles[i][1] * c
			
			self.currentPiece.rectangles[i][0] = round(xnew + center[0])
			self.currentPiece.rectangles[i][1] = round(xnew + center[1])
			
	def getCenter(self):
		x = [p[0] for p in self.currentPiece.rectangles]
		y = [p[1] for p in self.currentPiece.rectangles]
		centroid = (sum(x) // len(self.currentPiece.rectangles), sum(y) // len(self.currentPiece.rectangles))
		return centroid
			
		
# CHECK WIN STATE
# REMOVE RECTS FROM PIECES
# FALL DOWNWARDS AFTER CLEAR
# TETRIS MUSIC
# MOVE AUTOMATICALLY DOWNWARDS
# ROTATE PIECE

if __name__ == '__main__':
	
	g = graphicHandler()
	g.start()
