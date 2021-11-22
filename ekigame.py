# Author: Muhammad Nur Farizky
# Year: 2019
# Description: 
# This program shows the equipotential of four charged particles using Pygame

import Charge as chg
import pygame, sys
import numpy as np
from pygame.locals import *

pygame.init() 

#Deterimining width and height of the window (as well as the image resolution)
WIDTH = 400 
HEIGHT = 300 

DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption('Equipotential Lines') 

#Defining colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

DISPLAYSURF.fill(WHITE) 

ballr = 20
ball = [chg.charge(270, 80, ballr, 2), chg.charge(120, 80, ballr, 2), chg.charge(270, 200, ballr, 2), chg.charge(120, 200, ballr, 2)]

potential = 0 

#Scaling
scale = 0.01
colorrange = 13
colorscale = 10

for i in range(0, HEIGHT):
    for j in range(0, WIDTH):
        for k in range(0, len(ball)):
            potential = potential + ball[k].getPotential(j, i)
        for l in range(-colorscale, colorscale):
            if potential >= l*scale and potential < (l+1)*scale:
                pygame.draw.circle(DISPLAYSURF, (colorscale*(l+colorrange), colorscale*(l+colorrange), colorscale*(l+colorrange)), (j, i), 1, 0)
        potential = 0

for i in range(0, len(ball)):
    pygame.draw.circle(DISPLAYSURF, BLUE, (ball[i].getX(), ball[i].getY()), ball[i].getR(), 0)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        pygame.display.update()