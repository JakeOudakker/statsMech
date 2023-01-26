# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 15:23:21 2023

@author: jaket
"""

class Particle():
    def __init__(self, pos, velocity):
        self.pos = pos
        self.vel = velocity
        
    def __str__(self):
        return "Position: (" + str((self.pos)[0]) + ", " + str((self.pos)[1]) + ")\nVelocity: (" + str((self.vel)[0]) + ", " + str((self.vel)[1]) + ")"