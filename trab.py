import pygame
import sys
from pygame.locals import *
import time
import copy
import threading

white = (255,255,255)
black = (0,0,0)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)
down = 3
up = -4
left = -3
right = 3

class Element:
    def setSize(self, nSize):
        self.size = nSize
        if image == None:
            self.image = image
        else:
            for i in range(len(image)):
                self.image[0][i] = pygame.transform.scale(self.image[0][i], (self.size[0], self.size[1]))
                self.image[1][i] = pygame.transform.flip(pygame.transform.scale(self.image[0][i], (self.size[0], self.size[1])), True, False)

    def __init__(self, code, families, pos, size, base, direction, move, inObject, image, color):
        self.code = code
        self.pos = pos
        self.direction = direction
        self.size = size
        self.color = color
        self.base = base
        self.families = families
        self.inObject = inObject
        self.remove = False
        self.power = 0
        self.jump = 0
        self.action = 0

        self.lastDirection = [0, 0]
        if direction[0] > 0:
            self.lastDirection[0] = 1
        else:
            self.lastDirection[0] = 0
        if direction[1] > 0:
            self.lastDirection[1] = 1
        else:
            self.lastDirection[1] = 0

        self.move = move
        
        if image == None:
            self.image = image
        else:
            self.image = [[],[]]
            for i in image:
                self.image[0].append(pygame.transform.scale(i, (self.size[0], self.size[1])))
                self.image[1].append(pygame.transform.flip(pygame.transform.scale(i, (self.size[0], self.size[1])), True, False))

class FrameProcessor(object):
    def __init__(self, name, size, backgroundImage):
        pygame.init()
        self.size = size
        self.cont = 0
        self.events = None
        self.displacement = [0, 0]
        self.els = []
        self.screen = pygame.display.set_mode((size[0], size[1]), 0, 32)
        pygame.display.set_caption(name)
        self.screen.fill((white))
        self.backgroundImage = pygame.transform.scale(pygame.image.load(backgroundImage).convert_alpha(), (self.size[0], self.size[1]))
        pygame.display.update()

    def updateScreen(self):
        def getPosY(el):
            return el.pos[1]

        self.screen.fill(white)

        self.els.sort(key=getPosY, reverse=True)

        self.screen.blit(self.backgroundImage, (0, 0))

        for i in range(len(self.els)):
            i = len(self.els)-i-1
            if self.els[i].image == None:
                pygame.draw.rect(self.screen, (self.els[i].color), (self.els[i].pos[0]+self.displacement[0], self.els[i].pos[1]+self.displacement[1], self.els[i].size[0], self.els[i].size[1]))
            else:
                flipOrNot = 0 if(self.els[i].lastDirection[0] > 0) else 1
                self.screen.blit(self.els[i].image[flipOrNot][self.els[i].action], (self.els[i].pos[0]+self.displacement[0], self.els[i].pos[1]+self.displacement[1]))

        pygame.display.update()
        time.sleep(0.01)

    def treatEvents(self):
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit();
 
    def inObj(self, newPos):
        ret = False
        for i in range(len(self.els)):
            if newPos.code == self.els[i].code:
                continue
            if (newPos.pos[0]+newPos.size[0] > self.els[i].pos[0] and newPos.pos[0] < self.els[i].pos[0]+self.els[i].size[0]) and (newPos.pos[1]+newPos.size[1] > self.els[i].pos[1]+self.els[i].size[1]-self.els[i].base and newPos.pos[1]+newPos.size[1]-newPos.base < self.els[i].pos[1]+self.els[i].size[1]):
                aux = self.getEl(newPos.code)
                if callable(aux.inObject):
                    aux.inObject(self, self.els[i], aux)
                if callable(self.els[i].inObject):
                    self.els[i].inObject(self, aux, self.els[i]);
                ret = True
        return ret 

    def treatPos(self):
        for i in range(len(self.els)):
            newPos = Element(self.els[i].code, self.els[i].families, [int(self.els[i].pos[0]+self.els[i].direction[0]), self.els[i].pos[1]], self.els[i].size, self.els[i].base, self.els[i].direction, self.els[i].move, self.els[i].inObject, None if(self.els[i].image == None) else self.els[i].image[0], self.els[i].color)
            newPos.pos[0] = self.els[i].pos[0]+self.els[i].direction[0]
            if not self.inObj(newPos):
                if newPos.pos[0] >= -self.displacement[0] and newPos.pos[0]+newPos.size[0] <= self.size[0]-self.displacement[0]:
                    if self.els[i].families[0] == "player":
                            if self.els[i].pos[0] >= self.size[0]/2-self.displacement[0] and self.els[i].direction[0] > 0:
                                self.displacement[0] -= self.els[i].direction[0]
                            self.els[i].pos[0] = newPos.pos[0]
                    else:
                        self.els[i].pos[0] = newPos.pos[0]
                else:
                    if callable(self.els[i].inObject):
                        self.els[i].inObject(self, None, self.els[i])

            newPos.pos[0] = self.els[i].pos[0]
            newPos.pos[1] = int(self.els[i].pos[1]+self.els[i].direction[1])
            if not self.inObj(newPos):
                if newPos.pos[1] >= 0 and newPos.pos[1]+newPos.size[1] <= self.size[1]:
                    self.els[i].pos[1] = newPos.pos[1]
                else:
                    self.els[i].remove = True
                    if self.els[i].families[0] == "player":
                        def dead():
                            time.sleep(2)
                            sys.exit()
                        pygame.mixer.music.load("dead.wav")
                        pygame.mixer.music.play()
                        x = threading.Thread(target=dead(), args=())

                    if callable(self.els[i].inObject):
                        self.els[i].inObject(self, None, self.els[i])

    def move(self):
        self.cont += 1
        for i in self.els:
            if callable(i.move):
                i.move(self, i) 

    def getEl(self, el):
        for i in range(len(self.els)):
            if self.els[i].code == el:
                return self.els[i]
        return None

    def addElement(self, el):
        self.els.append(el)

    def removeElements(self):
        for i in self.els:
            if i.remove:
                self.els.remove(i)

    def nextFrame(self):
        if __name__ == '__main__':
            self.treatEvents()
            self.treatPos()
            self.removeElements()
            self.updateScreen()
            self.move()


processor = FrameProcessor("Mario Bros", [1000, 600], "background.png")

image = []
image.append(pygame.image.load("Mario/mario_stop.png").convert_alpha())
image.append(pygame.image.load("Mario/mario_step_1.png").convert_alpha())
image.append(pygame.image.load("Mario/mario_step_2.png").convert_alpha())
image.append(pygame.image.load("Mario/mario_jump_up.png").convert_alpha())
image.append(pygame.image.load("Mario/mario_jump_down.png").convert_alpha())

imageGoomba = []
imageGoomba.append(pygame.image.load("Goomba/goomba_step_1.png").convert_alpha())
imageGoomba.append(pygame.image.load("Goomba/goomba_step_2.png").convert_alpha())
imageGoomba.append(pygame.image.load("Goomba/goomba_step_3.png").convert_alpha())
imageGoomba.append(pygame.image.load("Goomba/goomba_step_4.png").convert_alpha())
imageGoomba.append(pygame.image.load("Goomba/goomba_step_5.png").convert_alpha())
imageGoomba.append(pygame.image.load("Goomba/goomba_step_6.png").convert_alpha())
imageGoomba.append(pygame.image.load("Goomba/goomba_step_7.png").convert_alpha())
imageGoomba.append(pygame.image.load("Goomba/goomba_step_8.png").convert_alpha())

block = pygame.image.load("block.jpg").convert()
floor = pygame.image.load("floor.jpg").convert_alpha()
block2 = pygame.image.load("block_2.jpeg").convert_alpha()
mushroom = pygame.image.load("mushroom.png").convert_alpha()
flag = pygame.image.load("flag.png").convert_alpha()

def playerInObj(self, obj, player):
    if obj == None:
        return
    if(player.pos[1]+player.size[1] <= obj.pos[1]):
        player.jump = 0
    if obj.families[0] == "flag": 
        player.remove = True;
        def win():
            time.sleep(6)
            sys.exit()
        pygame.mixer.music.load("win.wav")
        pygame.mixer.music.play()
        x = threading.Thread(target=win(), args=())
    if obj.families[0] == "power":
        player.power = 1
        player.setSize([50, 50])
        player.pos[1] -= 25
        obj.remove = True
    if(obj.families[0] == "NPC" or obj.families[0] == "player"):
        if(player.pos[1]+player.size[1] <= obj.pos[1]):
            obj.remove = True
            return
        if player.power == 0:
            player.remove = True;
            def dead():
                time.sleep(2)
                sys.exit()
            pygame.mixer.music.load("dead.wav")
            pygame.mixer.music.play()
            x = threading.Thread(target=dead(), args=())
        else:
            player.power -= 1
            player.setSize([50, 25])
            obj.remove = True

def playerMove(self, player): 
    def fall(direction, jump):
        time.sleep(0.5)
        if(jump == player.jump):
            direction[1] = down

    if self.cont%5 == 0:
        player.action = (player.action)%2+1
        self.cont = 0

    if player.direction[0] == 0:
        player.action = 0
    if player.jump != 0:
        if player.direction[1] > 0:
            player.action = 4
        else:
            player.action = 3

    for event in self.events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.direction[0] = left
                player.lastDirection[0] = -1
            elif event.key == pygame.K_RIGHT:
                player.direction[0] =  right
                player.lastDirection[0] = 1
            elif event.key == pygame.K_DOWN:
                player.direction[1] =  down+1
            elif event.key == pygame.K_UP:
                if player.jump < 1:
                    pygame.mixer.Sound("jump.wav").play()
                    player.direction[1] = up
                    player.jump += 1
                    jump = player.jump
                    x = threading.Thread(target=fall, args=(player.direction, jump))
                    x.start()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player.direction[0] = 0
            if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                player.direction[1] = down

def goombaInObj(self, obj, goomba):
    if obj == None or obj.pos[1] < goomba.pos[1]+goomba.size[1]:
        goomba.direction[0] *= -1
        goomba.lastDirection[0] = goomba.direction[0]

def goombaMove(self, goomba):
    if self.cont%5 == 0:
        goomba.action = (goomba.action+1)%8

def blockInObj(self, obj, block):
    if obj == None: return
    if(block.pos[1]+block.size[1] <= obj.pos[1] and block.jump == 0):
        block.jump += 1
        self.addElement(Element(8, ["power"], [block.pos[0], block.pos[1]-50], [50, 50], 35, [1, 4], None, None, [mushroom], blue))

processor.addElement(Element(0, ["player" ], [0,    400], [50,     25],  50, [0,    down], playerMove, playerInObj,           image, blue))
processor.addElement(Element(1, ["terreno"], [0,    450], [1000,  150], 150, [0,       0],       None,        None,         [floor], blue))
processor.addElement(Element(2, ["terreno"], [200,  300], [35,     35],  35, [0,       0],       None,        None,         [block], blue))
processor.addElement(Element(3, ["terreno"], [235,  300], [35,     35],  35, [0,       0],       None,        None,         [block], blue))
processor.addElement(Element(4, ["NPC"    ], [900,  400], [35,     35],  35, [left, down], goombaMove, goombaInObj,     imageGoomba, blue))
processor.addElement(Element(5, ["NPC"    ], [450,  400], [35,     35],  35, [left, down], goombaMove, goombaInObj,     imageGoomba, blue))
processor.addElement(Element(6, ["terreno"], [1150, 450], [1000,  150], 150, [0,       0],       None,        None,         [floor], blue))
processor.addElement(Element(7, ["terreno"], [270,  300], [35,     35],  35, [0,       0],       None,  blockInObj,        [block2], blue))
processor.addElement(Element(8, ["flag"], [2090, 250], [80,    200],  35, [0,       0],       None,        None,          [flag], blue))

pygame.mixer.music.load("music.wav")
pygame.mixer.music.play(-1)

while True:
    processor.nextFrame()
