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


window_h_w = 700 # window height and width
s = 40 # scale factor of lattice
offset = 70*5-s*5 #offset of the lattice
pr = 5  #point radius
#speed = 5
dt = .005 #time step



class Point():
    def __init__(self, canvas, pos, color='red'):
        self.canvas = canvas
        self.xpos = int(s * pos[0] + offset)
        self.ypos = int(s * pos[1] + offset)
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
    forces = calc_forces(particles)
    for i in range(0, len(particles)):
        p = particles[i]
        new_x = p.pos[0] + (p.vel[0] * dt) + (forces[i][0]*(dt**2)/2)
        new_y = p.pos[1] + (p.vel[1] * dt) + (forces[i][1]*(dt**2)/2)
        xc = new_x - p.pos[0] 
        yc = new_y - p.pos[1]
        p.update_pos((xc, yc))
    return particles

def update_velocity(curr_particles, next_particles):
    curr_forces = calc_forces(curr_particles)
    next_forces = calc_forces(next_particles)
    for i in range(0, len(curr_particles)):
        curr_p = curr_particles[i]
        new_vx = curr_p.vel[0] + ((next_forces[i][0] + curr_forces[i][0])*dt)/2
        new_vy = curr_p.vel[1] + ((next_forces[i][1] + curr_forces[i][1])*dt)/2
        next_particles[i].update_vel((new_vx, new_vy))
    return next_particles

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


def calc_energy(particles):
    total_energy = 0
    for i in range(0, len(particles)):
        p = particles[i]
        copy_particles = particles.copy()
        reduced_particles = copy_particles[:i] + copy_particles[i+1:]
        pot_energy = 0
        for rp in reduced_particles:
            diff_x = p.pos[0] - rp.pos[0]
            diff_y = p.pos[1] - rp.pos[1]
            pot_energy += ((1/(diff_x**2+diff_y**2)**6) - (2/(diff_x**2+diff_y**2)**3))
        kin_energy = (p.vel[0]**2 + p.vel[1]**2)/2
        single_particle_energy = pot_energy + kin_energy
        total_energy += single_particle_energy
        #if i == 0:
            #print(single_particle_energy, pot_energy, kin_energy)
    print(total_energy)
            
            
            

def update_all(particles):
    curr_particles = particles.copy()
    particles = update_position(particles)
    particles = update_velocity(curr_particles, particles)
    return particles

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
        time.sleep(0.0001)
        #for p in id_list:
          #  c.delete(p)
        c.delete('all')
        #print(len(particles))
        calc_energy(particles)
        particles = update_all(particles)
        #frame +=1
    return "End"
