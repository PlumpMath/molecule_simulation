from bge import logic
from bge import events
from bge import render
from mathutils import Vector

gdict = logic.globalDict


def carbons(this):
    count = 0
    for bond in this.get_bonds():
        if bond.name == "Carbon":
            count += 1
    return count


def form(cont):

    particle = cont.owner
    type = particle.name

    #look for bonds to form
    particle.form_bonds()
    
    if particle.charge <= 0:   
        gdict["free"][type].discard(particle)
        gdict["cations"].discard(particle)
        particle.remove_glow()
        cont.script = "formation.wait"


def wait(cont):
    particle = cont.owner
    if particle.charge > 0:
        type = particle.name
        gdict["free"][type].add(particle)
        gdict["cations"].add(particle)
        particle.add_glow()
        cont.script = "formation.form"      
    elif particle.formalCharge < 0:
        particle.add_glow(2)
        cont.script = "formation.attract"
        
        
def attract(cont):
    particle = cont.owner
    if particle.formalCharge >= 0:
        particle.remove_glow()
        cont.script = "formation.wait"
    else:
        total_force = Vector([0,0,0])
        for cation in gdict["cations"]:
            distance = particle.getDistanceTo(cation)
            if distance < 50:
                particle.scene.addObject("reaction_sound",particle)
                for bond in particle["bonds"]:
                    if bond.name == "Lone Pair":
                        particle.unlink(bond)
                        bond.self_destruct() #self destruct
                        particle.link(cation)
                        return
                        
            elif distance < 250:
                attraction = particle.get_repulsion(cation) * 100
                cation.applyForce(-attraction)
                total_force += attraction
        particle.applyForce(total_force)
            
        