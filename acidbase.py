from bge import logic
import types

gdict = logic.globalDict


def hydron(particle):
    particle.acid = types.MethodType(acid,particle)
    particle.collisionCallbacks.append(particle.acid)
def hydroxide(particle):
    particle.base = types.MethodType(base,particle)
    particle.collisionCallbacks.append(particle.base)


def acid(self,other):
    if "doubles" in other and other.get_charge() == 0:
        self.collisionCallbacks.remove(self.acid)
        self.remove_glow()
        other.link(self)
        electron_movement(other)
    elif other.name == "Lone Pair":
        self.scene.addObject("reaction_sound",self)
        bond = list(other["bonds"])[0]
        bond.unlink(other)
        other.self_destruct() # destroy lone pair
        self.link(bond)
        
        
def electron_movement(particle):
    
    if particle.name == "Oxygen":
        carbon = None
        for bond in particle.get_bonds():
            if bond.name == "Carbon":
                if carbon:
                    if carbons(bond) > carbons(carbon):
                        carbon = bond
                else:
                    carbon = bond
        # unlinks carbon with highest degree
        if carbon:
            particle.unlink(carbon)
            return
    if particle["doubles"]:
        particle.scene.addObject("fizzle_sound",particle)
        double = next(iter(particle["doubles"]))
        particle.unlink(double)
        return
    elif particle["triple"]:
        particle.scene.addObject("fizzle_sound",particle)
        particle.unlink(particle["triple"])
        return
    else:
        for bond in particle["bonds"]:
            if bond.name == "Hydrogen":
                # create another hydron
                particle.unlink(bond)
                bond.add_glow()
                return
    
   
def base(self,other):
    
    if other.name == "Hydrogen" and other not in self["bonds"]:
        self.scene.addObject("reaction_sound",self)
        self.molecule.damp()
        carbon = next(iter(other["bonds"]))
        for bond in iter(self["bonds"]):
            if bond.name == "Lone Pair":
                lonepair = bond
                break
        
        # acidbase
        carbon.unlink(other)
        self.unlink(lonepair)
        self.link(other)
        carbon.link(lonepair)
        
        # elimination
        for atom in carbon["bonds"]:
            if atom.name == "Carbon":
                for atom2 in atom["bonds"]:
                    if atom2.name == "Bromine":
                        atom.unlink(atom2)
                        carbon.unlink(lonepair)
                        # destroy lonepair
                        lonepair.self_destruct()
                        carbon.multiply_bonds(atom)
                        return 
            
        
        
        self.collisionCallbacks.remove(self.base)
      
        
