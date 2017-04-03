from bge import types
from bge import logic
from mathutils import Vector
from bond import Bond
from molecule import Molecule
gdict = logic.globalDict




valence = {"Oxygen":6,
            "Nitrogen": 5,
            "Carbon": 4
}


class Particle(types.KX_GameObject):
    
    def __init__(self,obj):
        self.damping = 20
        if self.name == "Lone Pair":
            self.repulsionfactor = 1.25
            self.lengthfactor = 10
        else:
            self.repulsionfactor = 1
            self.lengthfactor = 20
        self.maxdistance = 100
        self.distancefactor = 100
        self.strengthfactor = 100
        self.totalforce = Vector([0,0,0])
        
        ##from bond.py
        self.bond = Bond(self)
        
        self.molecule = None
        if "doubles" in self:
            self.charge = self.get_charge()
            self.formalCharge = self.get_formal_charge()
            
    ########linking and unlinking
    def self_destruct(self):
        self.state = 2 
        
    def get_charge(self):
        return 4 - (len(self["bonds"]) + 2 * len(self["doubles"]) + 3 * bool(self["triple"]))
    
    def get_formal_charge(self):
        lonepairs = [bond.name for bond in self["bonds"]].count("Lone Pair")
        return valence[self.name] - (len(self["bonds"]) + 2 * len(self["doubles"]) + 3 * bool(self["triple"])) - lonepairs

    def add_glow(self,type = 1):
        if type == 1:
            type = "Glow"
        else:
            type = "Glow2"
        self["glow"] = self.scene.addObject(type,self)
        self["glow"].setParent(self)
        
    def remove_glow(self):
        self["glow"].endObject()
        del self["glow"]

            
    #links               
    def unlink(self,other): 
        if other in self["bonds"]:
            self.remove_bond(other,"bonds")
        elif "doubles" in self:
            if other in self["doubles"]:
                self.remove_bond(other,"doubles")
            elif other is self["triple"]:
                self.remove_bond(other,"triple")
        self.molecule.split(self,other)
        
    def link(self,other):
        self.add_bond(other,"bonds")
        self.form_molecule(other)
        
    #molecules    
    def form_molecule(self,other):
        if self.molecule:
            if other.molecule:
                if other.molecule != self.molecule:
                    self.molecule.merge(other.molecule)
                return
            self.molecule.add(other)    
        elif other.molecule:
            other.molecule.add(self)
        else:
            self.molecule = Molecule(self)
            self.molecule.add(other)
            
    #more linking       
    def remove_bond(self,other,type):
        if type is not "triple":
            self[type].discard(other)
            other[type].discard(self)
        else:
            self[type] = None
            other[type] = None     
                  
    def add_bond(self,other,type):
        if type is not "triple":
            self[type].add(other)
            other[type].add(self)
        else:
            self[type] = other
            other[type] = self
                
    def get_bonds(self):
        bonds = self["bonds"].copy()
        if "doubles" in self:
            bonds.update(self["doubles"])
            if self["triple"]:
                bonds.add(self["triple"])
        return bonds
    
    
    ####bond forces   
    def reset(self):
        self.totalforce.zero()

    def get_repulsion(self,other):
        #repel force
        if other.name == "Lone Pair":
            repulsion = other.repulsionfactor
        else:
            repulsion = self.repulsionfactor
        distance,uvector,lvector = self.getVectTo(other)  
        distance /= self.distancefactor 
        return uvector *  repulsion /pow(distance,2) 
    
    def spring_force(self,other):
        #spring with damping
        if other.name == "Lone Pair":
            length = other.lengthfactor
        else:
            length = self.lengthfactor
        distance,uvector,lvector = self.getVectTo(other)     
        velocity = self.getLinearVelocity().project(uvector)
        return uvector *(distance - length) * self.strengthfactor - velocity * self.damping
    
    def repel_p_bond(self,other):
        distance,uvector,lvector = self.getVectTo(other)
        if not other.bond.inverted:
            pbond = other.getAxisVect((0,1,0))
        else:
            pbond = other.getAxisVect((1,0,0))
        vector = distance * uvector
        
        projection = vector.project(pbond) 

        return projection 
    
    def repel_p_bond2(self,other):
        distance,uvector,lvector = self.getVectTo(other)
        pbond = other.getAxisVect((0,0,1))
        vector = distance * uvector
        projection = vector.project(pbond)
        return vector - projection
    
    
    ####formation
    def find_atoms(self,type):
        for other in gdict["free"][type]:
            if other is self:
                continue
            elif other in self.get_bonds():
                ##see if you can double or triple bond
                if self.multiply_bonds(other):
                    return True  
                continue
            distance = self.getDistanceTo(other)
            if distance < self.maxdistance:
                self.link(other)
                if self.get_charge() == 0:
                    return True     
                 
    def form_bonds(self):
        for type in ["Hydrogen","Carbon","Oxygen","Bromine"]:
            if self.find_atoms(type):
                return
                    
    def multiply_bonds(self,other):
        
        if self["triple"]:
            return
        try:        
            min_charge = min(other.get_charge(),self.get_charge())
        except KeyError:
            return
        if min_charge == 1:
            ##single to double
            if other in self["bonds"]:
                self.remove_bond(other,"bonds")
                self.add_bond(other,"doubles")
            #double to triple
            elif other in self["doubles"]:
                self.remove_bond(other,"doubles")
                self.add_bond(other,"triple")
        #single to triple
        elif min_charge > 1 and other in self["bonds"]:
            self.remove_bond(other,"bonds")
            self.add_bond(other,"triple")
        self.molecule.refresh()
        if self.get_charge() == 0:
            return True  #charge gone
    