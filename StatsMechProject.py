# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 15:17:36 2023

@author: jaket
"""

from Particle import Particle
import math
from tkinter import Tk, Canvas
import time
import random


window_h_w = 700
s = 70
pr = 5
speed = 1



class Point():
    def __init__(self, canvas, pos, color='red'):
        self.canvas = canvas
        self.xpos = int(s * pos[0])
        self.ypos = int(s * pos[1])
        self.color = color
        self.id = canvas.create_oval(self.xpos-pr,self.ypos-pr,self.xpos+pr,self.ypos+pr, fill=color)
    def draw(self):
        self.canvas.move(self.id, 0, -1)

def initialize_lattice():
    particles = []
    for i in range(0, 16):
        particles.append(Particle((2*(i%4 + 1), 2*(math.trunc(i/4) + 1)), (0,0)))
    for part in particles:
        print(part)
    return particles

"""def update_position(particles):
    for p in particles:
        xr = random.random()
        yr = random.random()
        if xr > 0.66:
            xc = 0.01 * speed
        elif xr > 0.33:
            xc = 0
        else:
            xc = -0.01 * speed
        if yr > 0.66:
            yc = 0.01 * speed
        elif yr > 0.33:
            yc = 0
        else:
            yc = -0.01 * speed
        p.update_pos(p.pos, (xc, yc))
    return particles"""

def update_position(particles):
    return ""

def calc_forces(particles):
    forces = [0 for i in particles]
    for i in range(0, len(particles)):
        copy_particles = particles.copy()
        reduced_particles = copy_particles[:i] + copy_particles[i+1:]
        #print(len(reduced_particles))
        force_x = 0
        force_y = 0
        for rp in reduced_particles:
            dif_x = particles[i].pos[0] - rp.pos[0]
            dif_y = particles[i].pos[1] - rp.pos[1]
            force_x += f_x((dif_x, dif_y))
            force_y += f_y((dif_x, dif_y))
        forces[i] = (force_x, force_y)
    return forces
    
    
"""
Takes the difference in the x and y positions between 2 particles
"""
def f_x(pos):
    r2 = pos[0]**2 + pos[1]**2
    return 12*pos[0]*((1/r2**7) - (1/r2**4))


"""
Takes the difference in the x and y positions between 2 particles
"""
def f_y(pos):
    r2 = pos[0]**2 + pos[1]**2
    return 12*pos[1]*((1/r2**7) - (1/r2**4))

def update_all(particles):
    return ""

def show_system(particles):
    window = Tk()
    c = Canvas(master=window, bg='black',height=window_h_w, width=window_h_w)
    c.pack()

    window.title('Lattice')
    window.geometry( str(window_h_w)+"x" + str(window_h_w) + "+10+10")
    #frame = 0
    while True:
        #print(frame)
        id_list = [0 for i in particles]
        for i in range(0, len(particles)):
            p = particles[i]
            id_list[i] = Point(c, p.pos)
        window.update_idletasks()
        window.update()
        #time.sleep(0.0001)
        #for p in id_list:
          #  c.delete(p)
        c.delete('all')
        #print(len(particles))
        particles = update_position(particles)
        #frame +=1
    return "End"
