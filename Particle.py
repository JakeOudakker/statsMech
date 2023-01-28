# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 15:23:21 2023

@author: jaket
"""
def new_pos(pos, posc):
    if pos[0] + posc[0] > 10:
        xnew = pos[0] + posc[0] - 10
    elif pos[0] + posc[0] < 0:
        xnew = pos[0] + posc[0] + 10
    else:
        xnew = pos[0] + posc[0]
    if pos[1] + posc[1] >10:
        ynew = pos[1] + posc[1] -10
    elif pos[1] + posc[1] < 0:
        ynew = pos[1] + posc[1] + 10
    else:
        ynew = pos[1] + posc[1]
    return (xnew, ynew)

class Particle():
    def __init__(self, pos, velocity):
        self.pos = pos
        self.vel = velocity
        
    def __str__(self):
        return "Position: (" + str((self.pos)[0]) + ", " + str((self.pos)[1]) + ")\nVelocity: (" + str((self.vel)[0]) + ", " + str((self.vel)[1]) + ")"
    
    
    def update_pos(self, posc):
        pos_new = new_pos(self.pos, posc)
        self.pos = pos_new
        
    def update_vel(self, vel):
        self.vel = vel
        
    