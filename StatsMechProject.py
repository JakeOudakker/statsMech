# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 15:17:36 2023

@author: jaket
"""

from Particle import Particle
import math
from tkinter import *


window_h_w = 700
particles = []

def initialize_lattice():
    for i in range(0, 16):
        particles.append(Particle((2*(i%4 + 1), 2*(math.trunc(i/4) + 1)), (0,0)))
    for part in particles:
        print(part)

def show_system(particles):
    window = Tk()
    window.title('Hello Python')
    window.geometry( str(window_h_w)+"x" + str(window_h_w) + "+10+10")
    window.mainloop()
    return ""
