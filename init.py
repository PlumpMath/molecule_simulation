#init from camera
from bge import logic, render
from particle import Particle
from mathutils import Vector, Matrix


gdict = logic.globalDict



def draw():
    camera = scene.objects["Camera"]
    string = "BondCraft"
    ###draws bonds and changes text before frame load
    atoms = gdict["atoms"].copy()
    for atom in gdict["atoms"]:
        ###searches for everything connected to it and draws the bonds
        
        #prevents two line draws
        atoms.remove(atom)
        atom.bond.draw_bonds(atoms)
    for molecule in gdict["molecules"]:
        molecule.draw_text()
    for texture in gdict["textures"]:
        texture.refresh(True)
    if camera["laser"]:
        crosshairs = scene.objects["Crosshairs"]
        start = camera.worldPosition + camera.getAxisVect((1,-1,0))
        end = camera.worldPosition - camera.getAxisVect((0,0,1))
        
        render.drawLine(start,end,[0,1,0])
        obj,point, normal = camera.rayCast(crosshairs,None,2000)
        if obj:
            render.drawLine(point,point + normal * 10000,[0,1,0])
            obj.applyForce(-100 * normal)
 
            
def play(cont):
    scene.restart()
    gdict["play"] = True
    UI = cont.owner.scene
    UI.end()

    
def main(cont):
    global scene
    scene = logic.getCurrentScene() 
    scenes = logic.getSceneList()
    camera = cont.owner
    overlay = camera.actuators["Scene"]
    
    # camera state 2 is in the menu
    if camera.state == 2:
        if "play" not in gdict:
            # show menu
            cont.activate(overlay)
            render.showMouse(True)
            logic.setGravity([0,0,-9.8])
        else:
            # start game
            camera.state = 1
            render.showMouse(False)
            scene.objects["Floor"].endObject()
            scene.objects["Spawn"].endObject()
            logic.setGravity([0,0,0])
            scene.objects["Cube"].visible = True
            scene.objects["BondCraft"].visible = True
            return
    print("###############GAME START##################")
    
    
    gdict.clear()
    gdict["free"] = {   "Hydrogen": set(),
                        "Carbon": set(),
                        "Oxygen": set(),
                        "Nitrogen": set(),
                        "Bromine": set()
                     }
    gdict["cations"] = set()
    gdict["atoms"] = set()
    gdict["textures"] = []
    gdict["molecules"] = set()
    gdict["primary"] = "Hydrogen"
    gdict["camera"] = scene.objects["Camera"]
    
    gdict["prim_text"] = scene.objects["prim_text"]
    gdict["prim_text"].resolution = 16
    gdict["text"] = scene.objects["Text"]
    gdict["text"].resolution = 16
    #bind line drawing function
    scene.pre_draw = [draw]
    
    #slow down
    #fps =1000
    #logic.setLogicTicRate(fps)
    #logic.setPhysicsTicRate(fps)