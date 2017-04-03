from bge import logic, events
from mathutils import Matrix
from math import floor
from random import random

from particle import Particle
import acidbase


mouse = logic.mouse
keyboard = logic.keyboard
gdict = logic.globalDict
ACTIVE = logic.KX_INPUT_JUST_ACTIVATED


def saveObject(newobject,free=True):
    if free:
        gdict["free"][newobject.name].add(newobject)
    if "doubles" in newobject:
        gdict["cations"].add(newobject)
    gdict["atoms"].add(newobject)
    
    
def addObject(newobject,object,velocity=None):
    
    newobject = scene.addObject(newobject,object)
    newobject["bonds"] = set()
    if newobject.name in ["Carbon","Oxygen","Nitrogen"]:
        newobject["doubles"] = set()
        newobject["triple"] = None
    if velocity != None: 
        newobject.localLinearVelocity = velocity
    particle = Particle(newobject)
    
    return particle  


def addChild(child,parent,position):
    
    newobject = addObject(child,parent)
    
    # translate into local position
    newobject.worldTransform = newobject.worldTransform * Matrix.Translation(position)
    
    if "bonds" in parent:
        newobject.link(parent)
    if newobject.name != "Lone Pair":
        saveObject(newobject)
        
    return newobject


def main(cont):
    global camera, scene    
    scene = logic.getCurrentScene()

    camera = cont.owner 
    
    ###main controls###
    if keyboard.events[events.TKEY] == ACTIVE:
        camera["laser"] = True
    elif keyboard.events[events.TKEY] == 0:
        camera["laser"] = False
    if mouse.events[events.LEFTMOUSE] == ACTIVE:
        logic.sendMessage("pop","","Camera")
        fire_primary()
    elif mouse.events[events.RIGHTMOUSE] == ACTIVE:
        logic.sendMessage("pop","","Camera")
        newobject = addObject("Carbon",camera,[0,0,-100])
        saveObject(newobject)
        newobject.add_glow()
    elif keyboard.events[events.SPACEKEY] == ACTIVE:
        newobject = addObject("Antimatter",camera,[0,0,-500])
    elif keyboard.events[events.RKEY] == ACTIVE:
        scene.restart()
        return
        
    ## numkeys ##
    elif keyboard.events[events.ONEKEY] == ACTIVE:
        change_primary("Hydrogen")
    elif keyboard.events[events.TWOKEY] == ACTIVE:
        change_primary("Oxygen")
    elif keyboard.events[events.THREEKEY] == ACTIVE:
        change_primary("Nitrogen")
    elif keyboard.events[events.FOURKEY] == ACTIVE:
        change_primary("Bromine")
    elif keyboard.events[events.FIVEKEY] == ACTIVE:
        change_primary("Hydroxide")
    elif keyboard.events[events.SIXKEY] == ACTIVE:
        change_primary("Hydron")
        
        
def change_primary(type):
    gdict["primary"] = type
    primary_text = gdict["prim_text"]
    primary_text.text = type
    primary_text.visible= True
    primary_text.sensors["Delay"].delay = 200
    primary_text.sensors["Delay"].reset()
    
    
def fire_primary():
    
    type = gdict["primary"]
    
    if type == "Hydrogen":
        newobject = addObject("Hydrogen",camera,[0,0,-100])
        saveObject(newobject)
    elif type == "Oxygen":
        newobject = addObject("Oxygen",camera,[0,0,-180])
        newobject.add_glow()
        addChild("Lone Pair",newobject,[10,0,0])
        addChild("Lone Pair",newobject,[-10,0,0])
        saveObject(newobject)
        newobject.molecule.undamp()
    elif type == "Nitrogen":
        newobject = addObject("Nitrogen",camera,[0,0,-100])
        saveObject(newobject)
        newobject.add_glow()
        addChild("Lone Pair",newobject,[10,0,0])
        newobject.molecule.undamp()
    elif type == "Bromine":
        newobject = addObject("Bromine",camera,[0,0,-100])
        saveObject(newobject)
    elif type == "Hydroxide":
        newobject = addObject("Oxygen",camera,[0,0,-180])
        saveObject(newobject)
        newobject.add_glow()
        addChild("Lone Pair",newobject,[13,7.5,0])
        addChild("Lone Pair",newobject,[-13,7.5,0])
        addChild("Lone Pair",newobject,[0,-15,0])
        hydrogen = addChild("Hydrogen",newobject,[0,0,30])
        acidbase.hydroxide(newobject)
        newobject.molecule.undamp()
    elif type == "Hydron":
        newobject = addObject("Hydrogen",camera,[0,0,-100])
        acidbase.hydron(newobject)
        newobject.add_glow()
        saveObject(newobject,False)
        
        
# for opening scene        
def auto_spawn(cont):
    
    global scene
    scene = logic.getCurrentScene()
    
    if "free" not in gdict:
        return
    obj = cont.owner
    num = floor(random()*5)
    x = floor(random()*10) - 5
    y = floor(random()*10) - 5
    
    if num > 0:
        newobject = addObject("Hydrogen",obj,[x,y,50])
        saveObject(newobject)
    elif num == 0:
        newobject = addObject("Carbon",obj,[x,y,50])
        saveObject(newobject)
        newobject.add_glow()         