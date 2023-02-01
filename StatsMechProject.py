# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 15:17:36 2023

@author: jaket
"""

from Particle import Particle, r0, r0_w, window_h_w
import math
from tkinter import Tk, Canvas
import time
import random
#import msvcrt
import matplotlib.pyplot as plt
import copy
import seaborn as sns
from tqdm import trange, tqdm



#window_h_w = 700 # window height and width
#r0 = 40 # scale factor of lattice
#r0_w = window_h_w/r0
pr = 10*(r0/70)  #point radius
dt = .001 #time step
speed_bin_size = 0.001


######### Calculations Functions ##############

def calc_forces(particles):
    forces = [(0,0) for p in particles]
    for i in range(0, len(particles)):
        for j in range(i+1, len(particles)):
            if j != i:
                dif_x = particles[i].pos[0] - particles[j].pos[0]
                dif_y = particles[i].pos[1] - particles[j].pos[1]
                if dif_x > r0_w/2:
                   dif_x -= r0_w
                elif dif_x < -r0_w/2:
                    dif_x += r0_w
                if dif_y > r0_w/2:
                    dif_y -= r0_w
                elif dif_y < -r0_w/2:
                    dif_y += r0_w
                force_x = f_x((dif_x, dif_y))
                force_y = f_y((dif_x, dif_y))
                forces[i] = (forces[i][0] + force_x, forces[i][1] + force_y)
                forces[j] = (forces[j][0] - force_x, forces[j][1] - force_y)
    #print(forces[0])
    return forces
    #return [(0,0) for p in particles]
    
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


def calc_energy(particles, pprint = False):
    energies = [(0,0) for p in particles] # kinetic, potential
    for i in range(0, len(particles)):
        for j in range(i+1, len(particles)):
            if j != i:
                dif_x = abs(particles[i].pos[0] - particles[j].pos[0])
                dif_y = abs(particles[i].pos[1] - particles[j].pos[1])
                if dif_x > r0_w/2:
                   dif_x -= r0_w
                elif dif_x < -r0_w/2:
                    dif_x += r0_w
                if dif_y > r0_w/2:
                    dif_y -= r0_w
                elif dif_y < -r0_w/2:
                    dif_y += r0_w
                energies[i] = (energies[i][0], energies[i][1] + ((1/(dif_x**2+dif_y**2)**6) - 2*(1/(dif_x**2+dif_y**2)**3)))
        energies[i] = ((particles[i].vel[0]**2 + particles[i].vel[1]**2)/2 , energies[i][1])
    total_energy = 0
    for e in energies:
        total_energy += e[0] + e[1]
    if pprint:
        print(total_energy)
    return total_energy


########## Update Functions ##########

def verlet_update_position(particles):
    forces = calc_forces(particles)
    for i in range(0, len(particles)):
        p = particles[i]
        new_x = p.pos[0] + (p.vel[0] * dt) + ((forces[i][0]*(dt*dt))/2)
        new_y = p.pos[1] + (p.vel[1] * dt) + ((forces[i][1]*(dt*dt))/2)
        xc = new_x - p.pos[0] 
        yc = new_y - p.pos[1]
        p.update_pos((xc, yc))
    return particles

def verlet_update_velocity(curr_particles, next_particles):
    curr_forces = calc_forces(curr_particles)
    next_forces = calc_forces(next_particles)
    for i in range(0, len(curr_particles)):
        curr_p = curr_particles[i]
        new_vx = curr_p.vel[0] + ((next_forces[i][0] + curr_forces[i][0])*dt)/2
        new_vy = curr_p.vel[1] + ((next_forces[i][1] + curr_forces[i][1])*dt)/2
        next_particles[i].update_vel((new_vx, new_vy))
    return next_particles

def euler_update_position(particles):
    for i in range(0, len(particles)):
        p = particles[i]
        new_x = p.pos[0] + (p.vel[0] * dt)
        new_y = p.pos[1] + (p.vel[1] * dt)
        xc = new_x - p.pos[0] 
        yc = new_y - p.pos[1]
        p.update_pos((xc, yc))
    return particles
        
def euler_update_velocity(curr_particles, next_particles):
    curr_forces = calc_forces(curr_particles)
    for i in range(0, len(curr_particles)):
        curr_p = curr_particles[i]
        new_vx = curr_p.vel[0] + curr_forces[i][0]*dt
        new_vy = curr_p.vel[1] + curr_forces[i][1]*dt
        next_particles[i].update_vel((new_vx, new_vy))
    return next_particles

def euler_update_all(particles):
    curr_particles = particles.copy()
    particles = euler_update_position(particles)
    particles = euler_update_velocity(curr_particles, particles)
    return particles
            

def verlet_update_all(particles):
    curr_particles = particles.copy()
    particles = verlet_update_position(particles)
    particles = verlet_update_velocity(curr_particles, particles)
    return particles

def hybrid_1_update_all(particles):
    curr_particles = particles.copy()
    particles = euler_update_position(particles)
    particles = verlet_update_velocity(curr_particles, particles)
    return particles

def hybrid_2_update_all(particles):
    curr_particles = particles.copy()
    particles = verlet_update_position(particles)
    particles = euler_update_velocity(curr_particles, particles)
    return particles

def find_speed(particles, speed_dict):
    for p in particles:
        speed = p.vel[0]**2 + p.vel[1]**2
        bin_number = math.trunc(speed/speed_bin_size)
        if bin_number in speed_dict:
            speed_dict[bin_number] += 1
        else:
            speed_dict[bin_number] = 1 
    return speed_dict
    
######## Simulate and Run (Slow) ###########

def show_system(particles, pause=False, steps = 40000):
    window = Tk()
    c = Canvas(master=window, bg='black',height=window_h_w, width=window_h_w)
    c.pack()
    window.title('Lattice')
    window.geometry( str(window_h_w)+"x" + str(window_h_w) + "+10+10")
    #frame = 0
    #Elist = []
    #dtlist = []
    plist = []
    #speed_dict = dict()
    time_step = 0
    run = True
    while run:
        #print(frame)
        id_list = [0 for i in particles]
        for i in range(0, len(particles)):
            p = particles[i]
            id_list[i] = Point(c, p.pos)
        window.update_idletasks()
        window.update()
        #time.sleep(0.00001)
        #for p in id_list:
          #  c.delete(p)
        c.delete('all')
        #print(len(particles))
        #Elist.append(calc_energy(particles))
        #dtlist.append(time_step)
        #speed_dict = find_speed(particles, speed_dict)
        copyofparticles = copy.deepcopy(particles)
        plist.append(copyofparticles)
        #print(particles[0])
        if pause:
            [print(p) for p in particles]
            inp = input()
            if inp == 'y':
                pause = False
        if time_step > steps:
            run = False
            window.destroy()
        particles = hybrid_1_update_all(particles)
        #frame +=1
        time_step+=1
    return plist #Elist, dtlist, speed_ct

########## Visuals ###########

class Point():
    def __init__(self, canvas, pos, color='red'):
        self.canvas = canvas
        self.xpos = int (r0 * pos[0])
        self.ypos = int (r0 * pos[1])
        self.color = color
        self.id = canvas.create_oval(self.xpos-pr,self.ypos-pr,self.xpos+pr,self.ypos+pr, fill=color)
    def draw(self):
        self.canvas.move(self.id, 0, -1)


######### Main Functions ##########

def bake_sim(particles, steps = 40000):
    plist = []
    for i in trange(steps):
        copyofparticles = copy.deepcopy(particles)
        plist.append(copyofparticles)
        particles = hybrid_1_update_all(particles)
    return plist

def resimulate(plist):
    window = Tk()
    c = Canvas(master=window, bg='black',height=window_h_w, width=window_h_w)
    c.pack()
    window.title('Lattice')
    window.geometry( str(window_h_w)+"x" + str(window_h_w) + "+10+10")
    for particles in tqdm(plist):
        id_list = [0 for i in particles]
        for i in range(0, len(particles)):
            p = particles[i]
            id_list[i] = Point(c, p.pos)
        window.update_idletasks()
        window.update()
        c.delete('all')
        time.sleep(0.00000000001)
    window.destroy()
    return "Finished"

def initialize_lattice(edge, part_dist, vmag = 0):
    center = r0_w/2
    N = edge*edge
    particles = [0 for i in range(0,N)]
    lattice_width = (edge-1)*part_dist
    lw_half = lattice_width/2
    start = center - lw_half
    for i in range(0, N):
        particles[i] = Particle(((start + (part_dist*(i%edge))), (start + (part_dist*math.trunc(i/edge)))),(random.uniform(-1*vmag,vmag),random.uniform(-1*vmag, vmag)))
    for part in particles:
        print(part)
    return particles

###### Analysis #########

def plot_energy(plist, calc = True):
    if calc:
        Elist = []
        dtlist = []
        time_step = 0
        for particles in tqdm(plist):
            Elist.append(calc_energy(particles))
            dtlist.append(time_step)
            time_step += 1
    else:
        Elist = plist
    plt.scatter(dtlist, Elist)
    plt.title("Total Energy over Time")
    plt.ylabel("Energy (au)")
    plt.xlabel("Time Steps")
    return Elist

def distr_energy(Elist):
    fig = sns.displot(Elist, kind="hist", kde = True)
    fig.set_axis_labels('Total Energy (au)', 'Counts')
    
def distr_speed(plist):
    speeds = []
    for particles in tqdm(plist):
        for p in particles:
            speeds.append(p.vel[0]**2 + p.vel[1]**2)
    #plt.hist(speeds, 200)
    #plt.title("Speed Distribution")
    #plt.xlabel("Speed (au)")
    #plt.ylabel("Frequency")
    fig = sns.displot(speeds, kind='hist', kde=True)
    fig.set_axis_labels('Speed (au)', 'Counts')
    return speeds
    

###### Tests ##########
def test_1_static():
    ps = initialize_lattice(4, 2)
    plist = bake_sim(ps)
    return plist

def test_1_fast():
    ps = initialize_lattice(4, 2, vmag = 10)
    plist = bake_sim(ps)
    return plist

def test_2_static():
    ps = initialize_lattice(10, 1)
    plist = bake_sim(ps)
    return plist

def test_2_fast():
    ps = initialize_lattice(10, 1, vmag = 10)
    plist = bake_sim(ps)
    return plist
