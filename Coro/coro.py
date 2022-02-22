#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Miguel Aybar

import time
import RPi.GPIO as GPIO
import pygame, sys, os
from datetime import datetime
from kbrd import kbrd
import Tkinter
import tkMessageBox
from pygame.locals import *
import psutil

CIRCLE_ICON = 0
SQUARE_ICON = 1
TRIANGLE_ICON = 2
X_ICON = 3
UP_ICON = 4
DOWN_ICON = 5


inicio_de_tiempo = datetime.now()
state = "STOP"
cmd = (kbrd.NO_KEY, False)

file_selected = 0
audio_lst = []
message = ("", time.time())   # text, Timer
vol = 90
board = 0


def check_if_process_name_exist(name_process, num):
    list_pid = psutil.pids()
    found = False
    count = 0
    last_pid = 0
    for pid in list_pid:
        try:
            process = psutil.Process(pid)
            CL = process.cmdline()
            for word in CL:
                if name_process in word:
                    count+=1
                    if count == num:
                        print "SUP> " + name_process+ " is running! Status: PID: "+ str(pid)

                        found = True
                        break
                    last_pid = pid
        except (psutil.ZombieProcess, psutil.AccessDenied, psutil.NoSuchProcess):
            print "except checking process "+ name_process

        if found:
            break
    return found, last_pid, process


def get_list_audio():
    global audio_lst
    dir = '/home/pi/Documents/Scripts/Coro'
    contenido = os.listdir(dir)
    audio_lst = []
    for fichero in contenido:
        if os.path.isfile(os.path.join(dir, fichero)) and fichero.endswith('.wav'):
            audio_lst.append(fichero)


def list_process():
    global file_selected
    global state
    ret = False
    if cmd[0] == kbrd.X_KEY:
        state = "STOP"
        ret = True
    elif cmd[0] == kbrd.L_KEY:
        file_selected = file_selected + 1
        if file_selected == len(audio_lst):
            file_selected = 0
        ret = True
    elif cmd[0] == kbrd.R_KEY:
        if file_selected > 0:
            file_selected = file_selected - 1
        else:
            file_selected = len(audio_lst) - 1
        ret = True
    elif cmd[0] == kbrd.TRIANGLE_KEY:
        state = "SELECTED"
        ret = True
    return ret

def selected_process():
    global file_selected
    global state
    global inicio_de_tiempo
    global message
    global board
    ret = False
    if cmd[0] == kbrd.X_KEY:
        state = "LIST"
        ret = True
    elif cmd[0] == kbrd.TRIANGLE_KEY:
        try:
            audio_file = "/home/pi/Documents/Scripts/Coro/" + audio_lst[file_selected]
            pop =  "/usr/bin/aplay -D plughw:0 --vumeter=mono -i " + audio_file + "&"
            os.system(pop)
            # process = psutil.Popen(pop)
            time.sleep(1)
            found, pid, process = check_if_process_name_exist('aplay', 1)
            if found:
                state = "PLAYING"
                inicio_de_tiempo = datetime.now()
                board = 0
            else:
                message = ("Can not play using Board 0", time.time())

        except Exception as e:
            print str(e)
            message = ("Error playing", time.time())
        ret = True
    elif cmd[0] == kbrd.SQUARE_KEY:
        try:
            audio_file = "/home/pi/Documents/Scripts/Coro/" + audio_lst[file_selected]
            pop =  "/usr/bin/aplay -D plughw:1 --vumeter=mono -i " + audio_file + "&"
            os.system(pop)
            time.sleep(1)
            found, pid, process = check_if_process_name_exist('aplay', 1)
            if found:
                state = "PLAYING"
                inicio_de_tiempo = datetime.now()
                board = 1
            else:
                message = ("Can not play using Board 1", time.time())

        except Exception as e:
            print str(e)
            message = ("Error playing", time.time())
        ret = True
    elif cmd == (kbrd.CIRCLE_KEY, True):
        try:
            audio_file = "/home/pi/Documents/Scripts/Coro/" + audio_lst[file_selected]
            pop =  "rm " + audio_file + "&"
            os.system(pop)
            time.sleep(1)
            get_list_audio()
            state = "LIST"
            message = ("File deleted !", time.time())
            _refresh = True

        except Exception as e:
            print str(e)
            message = ("Error deleting", time.time())
        ret = True
    return ret

    
def state_machine():
    global state
    global cmd
    global inicio_de_tiempo
    global vol
    global board
    global message
    _refresh = False

    if message[0] != "":
        cur_time = time.time()
        if (cur_time - message[1]) > 2.0:
            message = ("", cur_time)
            _refresh = True
    elif state == "STOP":
        if cmd[0] == kbrd.CIRCLE_KEY and cmd[1] == True:
            try:
                pop = "/home/pi/Documents/Scripts/Coro/start_record.sh"
                os.system(pop)
                state = "RECORDING"
                inicio_de_tiempo = datetime.now()
            except Exception as e:
                print "Error sarting recording"
                message = ("Error starting recording!", time.time())
            _refresh = True
        elif cmd[0] == kbrd.TRIANGLE_KEY:
            get_list_audio()
            state = "LIST"
            _refresh = True
        elif cmd[0] == kbrd.X_KEY and cmd[1] == True:
            print "Exit X"
            kbrd.stop()
            pygame.quit()
            sys.exit()
    
    elif state == "RECORDING":
        if cmd[0] == kbrd.SQUARE_KEY:
            state = "STOP"
            found, pid, process = check_if_process_name_exist('arecord', 1)
            if found:
                process.terminate()
                time.sleep(1)
                # process.kill()
            
        _refresh = True
    elif state == "LIST":
            _refresh = list_process()
    elif state == "SELECTED":
        _refresh = selected_process()
    elif state == "PLAYING":
        found, pid, process = check_if_process_name_exist('aplay', 1)
        if not found:
            state = "SELECTED"
        elif cmd[0] == kbrd.SQUARE_KEY:
            process.terminate()
            time.sleep(1)
            state = "SELECTED"
        elif cmd[0] == kbrd.R_KEY:
            vol += 1
            if vol > 100:
                vol = 100
            try:
                if board == 0:
                    pop = "amixer -c 0 -- sset Headphone playback " + str(vol) + "%"
                else:
                    pop = "amixer -c 1 -- sset PCM playback " + str(vol) + "%"
                os.system(pop)
                _refresh = True
            except Exception as e:
                print str(e)
                message = ("error setting volume", time.time())

        elif cmd[0] == kbrd.L_KEY:
            vol -= 1
            if vol < 50:
                vol = 50
            try:
                if board == 0:
                    pop = "amixer -c 0 -- sset Headphone playback " + str(vol) + "%"
                else:
                    pop = "amixer -c 1 -- sset PCM playback " + str(vol) + "%"
                os.system(pop)
                _refresh = True
            except Exception as e:
                print str(e)
                message = ("error setting volume", time.time())

        _refresh = True
    return _refresh


def segToMin(inputSeg):
    local_minu = int(inputSeg / 60)
    local_seg = int(inputSeg - (local_minu * 60))
    return str(local_minu) + ":" + str(local_seg)


def draw():
    global label1
    global label_stop
    global label_rec
    global inicio_de_tiempo
    global message

    pygame.draw.line(DISPLAYSURF, BLACK, (0, 215), (320, 215), 2)

    if message[0] != "":
        txt_time = myfont.render(message[0], 1, BLACK)
        DISPLAYSURF.blit(txt_time, (10, 90))

    elif state == "STOP":
        DISPLAYSURF.blit(label1, (60, 10))
        DISPLAYSURF.blit(label2, (80, 60))
        show_option(0, CIRCLE_ICON, "REC", True)
        show_option(1, TRIANGLE_ICON, "LIST")

    elif state == "RECORDING":
        DISPLAYSURF.blit(label_recording, (100, 60))
        tiempo_final = datetime.now() 
        tiempo_transcurrido = tiempo_final - inicio_de_tiempo
        txt_time = myfont.render("Time = " + segToMin(tiempo_transcurrido.seconds), 1 , BLACK)
        DISPLAYSURF.blit(txt_time, (130, 120))
        show_option(0, SQUARE_ICON, "STOP")

    elif state == "LIST":
        first = 0
        if file_selected > 7:
            first = file_selected - 7
        last = first + 8
        if last > len(audio_lst):
            last = len(audio_lst)

        posy =10
        # myfont2 = pygame.font.SysFont("Consolas", 22)
        for x in range(first, last):
            item = audio_lst[x]
            label = myfont.render(str(x+1) + "."+ item, 1, BLACK)
            DISPLAYSURF.blit(label, (10, posy))
            posy = posy + 25

        posy = (10 + file_selected*25)
        if file_selected > 7:
            posy = (10 + 175)
        pygame.draw.rect(DISPLAYSURF, RED, (5, posy, 310, 25), 2)

        show_option(0, TRIANGLE_ICON, "SEL")
        show_option(1, UP_ICON, "UP")
        show_option(2, DOWN_ICON, "DOWN")
        show_option(3, X_ICON, "RETURN")
    elif state == "SELECTED":
        label = myfont.render(audio_lst[file_selected], 1, BLACK)
        DISPLAYSURF.blit(label, (10, 100))

        show_option(0, TRIANGLE_ICON, "PLAY1")
        show_option(1, SQUARE_ICON, "PLAY2")
        show_option(2, CIRCLE_ICON, "DEL", True)
        show_option(3, X_ICON, "RETURN")

    elif state == "PLAYING":
        label_song = myfont.render(audio_lst[file_selected], 1, BLACK)
        DISPLAYSURF.blit(label_song, (10, 20))
        DISPLAYSURF.blit(label_playing, (100, 60))
        tiempo_final = datetime.now()
        tiempo_transcurrido = tiempo_final - inicio_de_tiempo
        txt_time = myfont.render("Time = " + segToMin(tiempo_transcurrido.seconds), 1 , BLACK)
        DISPLAYSURF.blit(txt_time, (130, 120))
        txt_vol = myfont.render("Vol = " + str(vol) + "%", 1, BLACK)
        DISPLAYSURF.blit(txt_vol, (130, 140))
        show_option(0, SQUARE_ICON, "STOP")
        show_option(1, UP_ICON, "VOL+")
        show_option(2, DOWN_ICON, "VOL-")


    pygame.display.update()
    pygame.display.flip()


def show_option(pos_index, icon_index, text, long = False):
    myfont2 = pygame.font.SysFont("Consolas", 22)
    pos = [0, 80, 160, 240]
    img = [o_img, rec_img, tri_img, x_img, up_img, down_img]
    DISPLAYSURF.blit(img[icon_index], (pos[pos_index], 220))
    if long:
        c = RED
    else:
        c = BLACK
    label = myfont2.render(text, 1 , c)
    DISPLAYSURF.blit(label, (pos[pos_index]+20, 220))

  

os.putenv('SDL_FBDEV', '/dev/fb1')
os.system('cd /home/pi/Documents/Scripts/Coro')
pygame.init()
FPS = 30 # frames per second setting
fpsClock = pygame.time.Clock()

pygame.mouse.set_visible(False)
DISPLAYSURF = pygame.display.set_mode((320, 240), pygame.FULLSCREEN)   # , pygame.FULLSCREEN

keyboard = kbrd()
GPIO.setup(27,GPIO.OUT) 
 
# set up the colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

DISPLAYSURF.fill(WHITE)
pygame.display.update()
myfont = pygame.font.SysFont("Consolas", 30)
label1 = myfont.render("**DONOSTI ERESKI**", 1 , BLACK)
label2 = myfont.render("Concert recorder", 1 , BLACK)
label_recording = myfont.render("RECORDING...", 1 , BLACK)
label_playing = myfont.render("PLAYING...", 1 , BLACK)
label_error = myfont.render("ERROR", 1 , BLACK)

o_img= pygame.image.load('o.jpg')
rec_img= pygame.image.load('rec.jpg')
tri_img= pygame.image.load('tri.jpg')
x_img= pygame.image.load('x.jpg')
up_img= pygame.image.load('up.png')
down_img= pygame.image.load('down.png')

# set volume in board 0
try:
    pop = "amixer -q -c 0 -- sset Headphone playback 90%"
    os.system(pop)
    time.sleep(1)
except Exception as e:
    print str(e)

# set volume in board 1
try:
    pop = "amixer -q -c 1 -- sset PCM playback 90%"
    os.system(pop)
    time.sleep(1)
except Exception as e:
    print str(e)

GPIO.output(27, GPIO.HIGH)      # enable screen
draw()
try:
    while True:
        DISPLAYSURF.fill(WHITE)
        cmd = keyboard.get_key()
        
        refresh = state_machine()
        if refresh:
            draw()
            
        for event in pygame.event.get():
            if event.type == QUIT:
                print "QUIT"
                kbrd.stop()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print "ESCAPE"
                        kbrd.stop()
                        pygame.quit()
                        sys.exit()

        fpsClock.tick(FPS)

        
finally:
    GPIO.cleanup()








 