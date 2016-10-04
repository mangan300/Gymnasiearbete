#!usr/bin/env python
# -*- coding: utf-8 -*-
'''
Namn: Magnus Bergkvist
Klass: Te14
Datum:

<skriv in programmets funktion>

'''

import pygame, sys
from pygame.locals import *

bif = "bg.png"
mif = "mousec.png"

pygame.init()

screen = pygame.display.set_mode((1920, 1080))

background = pygame.image.load(bif).convert()
mouse_c = pygame.image.load(mif).convert_alpha()


while True:

    for event in pygame.event.get():

'''
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    screen.blit(background, (0,0))

    x , y = pygame.mouse.get_pos()
    x -= mouse_c.get_width()/2
    y -= mouse_c.get_width()/2

    screen.blit(mouse_c, (x,y))

    def shoot(image, From, direction, velocity):


    pygame.display.update()
'''