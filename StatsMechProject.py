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
import matplotlib.ticker as ticker
from matplotlib.colors import LogNorm, Normalize
from scipy.odr import ODR, Model, Data, RealData
import copy
import seaborn as sns
from tqdm import trange, tqdm
import numpy as np



#window_h_w = 700 # window height and width
#r0 = 40 # scale factor of lattice
#r0_w = window_h_w/r0
pr = 10*(r0/70)  #point radius
dt = .001 #time step
speed_bin_size = 0.001
R = 2


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

def scale_vel(particles):
    print("scale vel")
    for p in particles:
        p.update_vel((p.vel[0] * R, p.vel[1]*R))
    return particles
        
def scale_pos(particles, old_particles):
    print("scale pos")
    for i in range(len(particles)):
        p = particles[i]
        op = old_particles[i]
        p.update_pos(((p.pos[0] - R*(p.pos[0] - op.pos[0])),(p.pos[1] - R*(p.pos[1]-op.pos[1]))))
    return particles
        
    
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

def show_melt(particles, steps=100000):
    window = Tk()
    c = Canvas(master=window, bg='black',height=window_h_w, width=window_h_w)
    c.pack()
    window.title('Lattice')
    window.geometry( str(window_h_w)+"x" + str(window_h_w) + "+10+10")
    plist = []
    for i in trange(steps):
        id_list = [0 for k in particles]
        for j in range(0, len(particles)):
            p = particles[j]
            id_list[j] = Point(c, p.pos)
        window.update_idletasks()
        window.update()
        c.delete('all')
        copyofparticles = copy.deepcopy(particles)
        plist.append(copyofparticles)
        particles = hybrid_1_update_all(particles)
        #if (i+1) % 1000 == 0 and i < 5500:
            #particles = scale_vel(particles)
            #particles = scale_pos(particles, copyofparticles)
    window.destroy()
    return plist

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

def bake_melt(particles, steps = 40000):
    plist = []
    for i in trange(steps):
        copyofparticles = copy.deepcopy(particles)
        plist.append(copyofparticles)
        particles = hybrid_1_update_all(particles)
        if i % 10001 == 0:
            particles = scale_vel(particles)
            particles = scale_pos(particles, copyofparticles)
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
        #time.sleep(0.00000000001)
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

def show_frame(particles):
    window = Tk()
    c = Canvas(master=window, bg='black',height=window_h_w, width=window_h_w)
    c.pack()
    window.title('Lattice')
    window.geometry( str(window_h_w)+"x" + str(window_h_w) + "+10+10")
    while True:
        id_list = [0 for i in particles]
        for i in range(0, len(particles)):
            p = particles[i]
            id_list[i] = Point(c, p.pos)
        window.update_idletasks()
        window.update()

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
    plt.scatter(dtlist, Elist)
    plt.title("Total Energy over Time")
    plt.ylabel("Energy (au)")
    plt.xlabel("Time Steps")
    return Elist

def distr_energy(Elist):
    fig1 = sns.displot(Elist, kind="hist", kde = True, bins=100)
    #fig = sns.displot(Elist, kind="hist")#, bins = 100)
    fig1.set_axis_labels('Total Energy (au)', 'Counts')
    fig1.tick_params(axis='x', labelsize="small")
    fig1.set(title="Energy Distribution")
    
    
def distr_speed(plist):
    speeds = []
    for particles in tqdm(plist):
        for p in particles:
            speeds.append(math.sqrt(p.vel[0]**2 + p.vel[1]**2))
    #plt.hist(speeds, 200)
    #plt.title("Speed Distribution")
    #plt.xlabel("Speed (au)")
    #plt.ylabel("Frequency")
    fig = sns.displot(speeds, kind='hist', kde=True)
    fig.set_axis_labels('Speed (au)', 'Counts')
    fig.set(title="Speed Distribution")
    return speeds
    

def plot_temp(plist):
    KElist = []
    dtlist = []
    time_step = 0
    for particles in tqdm(plist):
        KEtotal = 0
        for p in particles:
            KEtotal += (p.vel[0]**2 + p.vel[1]**2)/2
        KElist.append(KEtotal/len(particles))
        dtlist.append(time_step)
        time_step += 1
    plt.scatter(dtlist, KElist)
    plt.title("Temperature over Time")
    plt.ylabel("Temperature (au)")
    plt.xlabel("Time Steps")
    
def distr_temp(plist):
    KElist = []
    dtlist = []
    time_step = 0
    for particles in tqdm(plist):
        KEtotal = 0
        for p in particles:
            KEtotal += (p.vel[0]**2 + p.vel[1]**2)/2
        KElist.append(KEtotal/len(particles))
        dtlist.append(time_step)
        time_step += 1
    fig = sns.displot(KElist, kind='hist', kde=True)
    fig.set_axis_labels('Temperature (au)', 'Counts')
    fig.set(title="Temperature Distribution")
    
def distr_vel(plist):
    vecs = {'x_comp':[], 'y_comp':[]}
    for particles in plist:
        for p in particles:
            vecs['x_comp'].append(p.vel[0])
            vecs['y_comp'].append(p.vel[1])
    #fig = sns.displot(vecs, x='x_comp', y='y_comp', cbar=True)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.hist2d(vecs['x_comp'], vecs['y_comp'], bins=100, cmap='RdBu_r', norm=LogNorm())
    ax.set_aspect('equal')
    ax.set_xlabel('$v_x (au)$')
    ax.set_ylabel('$v_y (au)$')
    plt.colorbar(label="Counts")
    plt.title("Velocity Distribution")
    
def plot_sq_dist(plist):
    p1 = 0
    p2 = int(len(plist[0])/2) - 1
    sq_dist = []
    mean_sq = []
    dtlist= []
    time_step=0
    for particles in tqdm(plist):
        dtlist.append(time_step)
        dif_x = abs(particles[p1].pos[0] - particles[p2].pos[0])
        dif_y = abs(particles[p1].pos[1] - particles[p2].pos[1])
        if dif_x > r0_w/2:
           dif_x -= r0_w
        elif dif_x < -r0_w/2:
            dif_x += r0_w
        if dif_y > r0_w/2:
            dif_y -= r0_w
        elif dif_y < -r0_w/2:
            dif_y += r0_w
        sq_dist.append(dif_x**2 + dif_y**2)
        mean_sq.append(np.mean(sq_dist))
        time_step += 1
    fig, axs = plt.subplots(2)
    axs[0].scatter(dtlist, sq_dist)
    axs[0].set_title("(Mean) Squared Distance over Time")
    axs[0].set_xlabel("Time Steps")
    axs[0].set_ylabel(r'$r^2$')
    axs[1].scatter(dtlist, mean_sq)
    #axs[1].set_title("Mean Squared Distance over Time")
    axs[1].set_xlabel("Time Steps")
    axs[1].set_ylabel(r'$\langle r^2 \rangle$')
    return sq_dist, mean_sq

def plot_mean_sq(plist):
    p1 = 0
    p2 = int(len(plist[0])/2)-5
    p1_0 = plist[0][p1]
    p2_0 = plist[0][p2]
    SD1 = []
    SD2 = []
    MSD1 = []
    MSD2 = []
    dtlist = []
    time_step = 0
    for particles in tqdm(plist):
        dtlist.append(time_step)
        time_step += 1
        p1_x = abs(particles[p1].pos[0] - p1_0.pos[0])
        p1_y = abs(particles[p1].pos[1] - p1_0.pos[1])
        SD1.append(p1_x**2 + p1_y**2)
        p2_x = abs(particles[p2].pos[0] - p2_0.pos[0])
        p2_y = abs(particles[p2].pos[1] - p2_0.pos[1])
        SD2.append(p2_x**2 + p2_y**2)
        MSD1.append(np.mean(SD1))
        MSD2.append(np.mean(SD2))
    fig, axs = plt.subplots(2)
    fig.suptitle("Mean Squared Displacement")
    axs[0].scatter(dtlist, MSD1)
    axs[0].set_title("Particle 1")
    axs[0].set_xlabel("Time Steps")
    axs[0].set_ylabel(r'$\langle r^2 \rangle$')
    axs[1].scatter(dtlist, MSD2)
    axs[1].set_title("Particle 2")
    axs[1].set_xlabel("Time Steps")
    axs[1].set_ylabel(r'$\langle r^2 \rangle$')
    plt.tight_layout()
    
    
def fit_MB(speeds):
    speed_dict = dict()
    bins = 100
    min_s = np.min(speeds)
    max_s = np.max(speeds)
    print(min_s, max_s)
    step = 1
    print(step)
    for i in range(bins):
        speed_dict[i*step] = 0
    for s in speeds:
        speed_dict[math.trunc(s/step)] += 1
        
    def func(x, a, b):
        return a*x**2*np.exp(b*x**2)
    xdata = list(speed_dict.keys())
    ydata = list(speed_dict.values())
    plt.scatter(xdata, ydata)
    model = Model(func)
    
    return speed_dict


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

def test_3_static():
    ps = initialize_lattice(10, 1)
    plist = show_melt(ps)
    return plist

def test_3_solid(ps):
    ps1 = ps.copy()
    plist = show_melt(ps1)
    return plist

def test_4_MB():
    ps = initialize_lattice(10, 3, vmag = 25)
    plist = show_melt(ps)
    return plist
