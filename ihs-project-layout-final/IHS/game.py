import pygame
import os, sys
from fcntl import ioctl
from tiles import *
from spritesheet import Spritesheet
from player import Player

def fixTo6(str1):
    if(len(str1) == 5):
        str1 = str1[:2] + "0" + str1[2:]
    if(len(str1) == 4):
        str1 = str1[:2] + "00" + str1[2:]
    if(len(str1) == 3):
        str1 = str1[:2] + "000" + str1[2:]    
    return str1

# ioctl commands defined at the pci driver
RD_SWITCHES   = 24929
RD_PBUTTONS   = 24930
WR_L_DISPLAY  = 24931
WR_R_DISPLAY  = 24932
WR_RED_LEDS   = 24933
WR_GREEN_LEDS = 24934

################################# LOAD UP A BASIC WINDOW AND CLOCK #################################
pygame.init()
DISPLAY_W, DISPLAY_H = 640, 480
canvas = pygame.Surface((DISPLAY_W,DISPLAY_H))
window = pygame.display.set_mode(((DISPLAY_W,DISPLAY_H)))
running = True
clock = pygame.time.Clock()
font = pygame.font.SysFont("comicsansms", 20)
TARGET_FPS = 60

if len(sys.argv) < 2:
        print("Error: expected more command line arguments")
        print("Syntax: %s </dev/device_file>"%sys.argv[0])
        exit(1)

fd = os.open(sys.argv[1], os.O_RDWR)

data = 0xFFFFFFFF;
ioctl(fd, WR_L_DISPLAY)
retval = os.write(fd, data.to_bytes(4, 'little'))

data = 0xFFFFFFFF;
ioctl(fd, WR_R_DISPLAY)
retval = os.write(fd, data.to_bytes(4, 'little'))

data = 0x0;
ioctl(fd, WR_GREEN_LEDS)
retval = os.write(fd, data.to_bytes(4, 'little'))

data = 0xFFFFFFFF;
ioctl(fd, WR_RED_LEDS)
retval = os.write(fd, data.to_bytes(4, 'little'))

ioctl(fd, RD_PBUTTONS)

################################# START MUSIC #################################
#if pygame.mixer:
#        pygame.mixer.music.load('sound.mp3')
#        pygame.mixer.music.play(-1)

################################# LOAD PLAYER AND SPRITESHEET###################################
spritesheet = Spritesheet('spritesheet.png')
player = Player()
flagWin, flagBoard, flagAux = 0, 0, 1
#################################### LOAD THE LEVEL #######################################
map = TileMap('mapacsv.csv', spritesheet)
player.position.x, player.position.y = map.start_x, map.start_y

################################# GAME LOOP ##########################
while running:
    dt = clock.tick(60) * .001 * TARGET_FPS
    ################################# CHECK PLAYER INPUT #################################

    red = os.read(fd, 4);
    val = fixTo6(bin(red[0]))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
       
    if(val[2] == '0'):
        player.UP_KEY = True
    if(val[3] == '0'):
        player.DOWN_KEY = True
    if(val[4] == '0'):
        player.facing = 1
        player.LEFT_KEY = True
    if(val[5] == '0'):
        player.facing = -1
        player.RIGHT_KEY = True    

    if(val[2] == '1'):
        player.UP_KEY = False
    if(val[3] == '1'):
        player.DOWN_KEY = False
    if(val[4] == '1'):
        player.LEFT_KEY = False
    if(val[5] == '1'):
        player.RIGHT_KEY = False

    ################################# UPDATE/ Animate SPRITE #################################
    player.update(dt, map.tiles, player.facing)
    if(player.position.y < map.end_y and flagAux == 1):
        flagWin = 1
        flagBoard = 1

    ################################# UPDATE BOARD #################################
    if(flagBoard == 1):
        flagBoarD = 0
        data = 0x08080808;
        ioctl(fd, WR_R_DISPLAY)
        retval = os.write(fd, data.to_bytes(4, 'little'))

        data = 0x08080808;
        ioctl(fd, WR_L_DISPLAY)
        retval = os.write(fd, data.to_bytes(4, 'little'))

        data = 0x0
        ioctl(fd, WR_RED_LEDS)
        retval = os.write(fd, data.to_bytes(4, 'little'))

        data = 0xFFFFFFFF
        ioctl(fd, WR_GREEN_LEDS)
        retval = os.write(fd, data.to_bytes(4, 'little'))


    ################################# UPDATE WINDOW AND DISPLAY #################################
    if(flagWin == 1):
        flagAux = 0
        # Fill background
        canvas = pygame.Surface(window.get_size())
        canvas = canvas.convert()
        canvas.fill((255, 255, 255))

        # Display some text
        text = font.render("Parabéns pelo tempo perdido! :)", 1, (10, 10, 10))
        textpos = text.get_rect()
        textpos.centerx = canvas.get_rect().centerx
        textpos.centery = canvas.get_rect().centery
        canvas.blit(text, textpos)

    if(flagWin == 0):
        canvas.fill((64,73,115)) # Fills the entire screen with light blue
        map.draw_map(canvas)
        player.draw(canvas)

    window.blit(canvas, (0,0))
    pygame.display.update()