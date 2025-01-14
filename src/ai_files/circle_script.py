import pygame
import random
from pygame import display, time
pygame.init()
screen = display.set_mode((500, 500))
time.delay(100)
color = (random.randint(0,255),random.randint(0,255), random.randint(0,255))
pygame.draw.circle(screen, color, (250, 250), 100)  
display.update()
time.delay(3000) 
pygame.quit()
