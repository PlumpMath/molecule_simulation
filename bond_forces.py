from bge import logic
from bge import events
from bge import render
from mathutils import Vector
from math import degrees
from molecule import Molecule

gdict = logic.globalDict



def align_p_bonds(this,other):
    # aligns nearby pbonds together e.g. in benzene
    if ("doubles" in this and len(this["doubles"]) == 1) or ("triple" in this and this["triple"]):
        axisvect = other.getAxisVect((0,1,0))
        this.alignAxisToVect(axisvect,1,0.1)


def calc_forces(cont):
    # first atoms are adjacent
    particle = cont.owner
    if not particle.molecule:
        if particle.name in {"Hydrogen","Bromine"} and "glow" not in particle:
            type = particle.name
            gdict["free"][type].add(particle)
            cont.script = "bond_forces.lone_" + type.lower()
        else:
            cont.script = "bond_forces.lone_atom"
        return
    
    # set total force to zero
    particle.reset() 
    for bond in particle["near_bonds"]:
        particle.totalforce -= particle.get_repulsion(bond)
    for bond in particle["far_bonds"]:
        if particle.getDistanceTo(bond) < 30:
            particle.bond.draw_line(bond,[0,1,0])
            particle.totalforce -= particle.get_repulsion(bond) * 0.5
    bonds = particle.get_bonds()   
       
    # SPRINGS
    for bond in bonds:
        particle.totalforce += particle.spring_force(bond)
        if "doubles" in bond:

            
            # P BONDS
            if bond["doubles"]:
                
                # p bonds cause a spring
                projection = particle.repel_p_bond(bond)
                
                # damps spring
                velocity = particle.getLinearVelocity().project(projection)
                
                particle.totalforce += projection * 10 - velocity * 2
                bond.applyForce(-projection * 10)
                
                align_p_bonds(particle,bond)

            elif "triple" in bond and bond["triple"]:
                projection = particle.repel_p_bond2(bond)
                
                velocity = particle.getLinearVelocity().project(projection)
                
                particle.totalforce += projection * 5 - velocity * 100
                bond.applyForce(-projection * 5)
                
                align_p_bonds(particle,bond)
            


        
    lindamp = 0.1 # makes molecules stay still
    velocity = particle.getLinearVelocity()
    force = particle.totalforce - velocity * lindamp
    sensor = cont.sensors["Bonds"]
    
    # check if at rest
    if force.magnitude > 0.1:
        sensor.frequency = 2
        particle.applyForce(force)
    else:
        particle.worldVelocity = Vector([0,0,0])
        sensor.frequency = 20
        

# don't do anything        
def lone_atom(cont):
    particle = cont.owner
    
    if particle.molecule:
        if particle.name == "Hydrogen" and "glow" in particle:
            particle.remove_glow()
        type = particle.name
        if type == "Hydrogen":
            gdict["free"][type].discard(particle)
        cont.script = "bond_forces.calc_forces"
       
# get hydrogens        
def lone_hydrogen(cont):
    particle = cont.owner
    
    if particle.molecule:
        gdict["free"]["Hydrogen"].discard(particle)
        bonds = particle["bonds"]
        if len(bonds) > 1:
            random = next(iter(bonds))
            particle.unlink(random)
            return
            
        cont.script = "bond_forces.calc_forces"
        return
    
    for other in gdict["free"]["Hydrogen"]:
        if other is particle:
            continue
        distance = particle.getDistanceTo(other)
        if distance < particle.maxdistance:
            particle.link(other)
            gdict["free"]["Hydrogen"].remove(particle)
            gdict["free"]["Hydrogen"].remove(other)
            cont.script = "bond_forces.calc_forces"
            return
        
        
        
def lone_bromine(cont):
    particle = cont.owner  
    type = particle.name
    
    if particle.molecule:
        bonds = particle["bonds"]
        gdict["free"][type].discard(particle)
        if len(bonds) > 1:
            random = next(iter(bonds))
            particle.unlink(random)
            return
            
        cont.script = "bond_forces.calc_forces"
        return
    
    for other in gdict["free"][type]:
        if other is particle:
            continue
        distance = particle.getDistanceTo(other)
        if distance < particle.maxdistance:
            particle.link(other)
            gdict["free"][type].remove(particle)
            gdict["free"][type].remove(other)
            cont.script = "bond_forces.calc_forces"
            return



