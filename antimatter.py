from bge import logic
import types
from mathutils import Vector
from math import ceil
from random import random
from particle import Particle


gdict = logic.globalDict


def antimatter(cont):
    #module called by stars and antimatter
    particle = cont.owner
    if particle.name != "Antimatter":
        particle = Particle(particle)
    particle.annihilate = types.MethodType(annihilate,particle)
    particle.collisionCallbacks.append(particle.annihilate)


def annihilate(self,atom):
    #sever bonds
    if "bonds" not in atom:
        #not matter
        if self.name == "Antimatter":
            self.endObject()
        return

    ### in state 2, it executes self_destruct safely without other controllers
    atom.self_destruct()
    ##stars and floor also annihilate things
    if self.name == "Antimatter":
        for i in range(0,100):
            photon = self.scene.addObject("Photon",atom,ceil(100 * random()))
            photon.applyForce(Vector([random() ,random(),random()]) * 5000 - Vector([2500,2500,2500]))
        
        self.scene.addObject("Explosion_sound",self)
        self.endObject()
        

def self_destruct(cont):
    atom = cont.owner
    for adjacent in atom.get_bonds():
        if adjacent.invalid:
            continue
        if adjacent.name == "Lone Pair":
            adjacent.endObject()
        else:
            atom.unlink(adjacent)
    type = atom.name
    if atom in gdict["atoms"]:
        gdict["atoms"].remove(atom)
        gdict["cations"].discard(atom)
        gdict["free"][type].discard(atom)
    atom.endObject()
    
    

        
