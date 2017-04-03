from bge import logic, render
from naming import name
gdict = logic.globalDict


def move_text(cont):
    this = cont.owner
    if this.text:
        this.worldPosition = this["molecule"].center.worldPosition + gdict["camera"].getAxisVect((1,1,0)) * 20
        
        
class Molecule:

    def __init__(self,particle):
        self.damped = True
        self.atoms = {particle}
        
        self.text = particle.scene.addObject("name",particle)
        self.text["molecule"] = self
        self.center = particle
        
        gdict["molecules"].add(self)
        gdict["text"].text = str(len(gdict["molecules"]))
        self.refresh()
        
    def delete(self):
        self.text.endObject()
        gdict["molecules"].remove(self)
        gdict["text"].text = str(len(gdict["molecules"]))
        
    def draw_text(self):
        if self.text.text:
            render.drawLine(self.center.worldPosition,
                            self.text.worldPosition,[1,1,1])
            
    # adding and removing atoms              
    def add(self,particle):
        self.damp()
        self.atoms.add(particle)
        particle.molecule = self
        self.refresh()
        
    def remove(self,particle):
        self.atoms.discard(particle)
        particle.molecule = None
        if not self.atoms:
            self.delete()
            return
        if particle is self.center:
            self.center = next(iter(self.atoms))
        self.refresh()
        
    # molecule functions
    def split(self,particle,other):
        for atom in self.atoms.copy():
            self.remove(atom)
        #create new molecules if any
        if other.get_bonds():
            other.molecule = Molecule(other)
            other.molecule.update()
        if particle.get_bonds() and not particle.molecule:
            particle.molecule = Molecule(particle)
            particle.molecule.update()
            
    def update(self):
        # puts all the atoms in the molecule
        particle = next(iter(self.atoms))
        searching = {particle}
        searched = {particle}
        while searching:
            copy = searching.copy()
            searching = set()
            for atom in copy:
                for bond in atom.get_bonds():
                    if bond not in searched:
                        searched.add(bond)
                        bond.molecule = self
                        if "doubles" in bond:
                            searching.add(bond)
        self.atoms = searched
        self.refresh()
        
    def merge(self,other):
        self.damp()
        center = self.center
        self.update()
        other.delete()
        self.refresh()
        
    def refresh(self):
        # name self and update bond forces in atoms
        name(self)
        for atom in self.atoms:
            if "doubles" in atom:
                atom.charge = atom.get_charge()
                atom.formalCharge = atom.get_formal_charge()
            self.update_bonds(atom)
            
    def update_bonds(self,particle):
        
        i = 0  # counts how many degrees of seperation
        searching = {particle}  # list of all atoms to search
        searched = {particle}  # atoms already searched
        particle["near_bonds"] = set()
        
        while searching:
            i += 1
            copy = searching.copy()
            searching.clear()
            for atom in copy:
                for bond in atom.get_bonds():
                    if bond not in searched:
                        searched.add(bond)
                        if i == 2 or i == 3:
                            particle["near_bonds"].add(bond)
                        if "doubles" in bond:
                            searching.add(bond)
        # everything else
        total_atoms = self.atoms
        particle["far_bonds"] = total_atoms.difference(particle["near_bonds"],
                                                        particle.get_bonds(),
                                                        {particle})
                                                        
    # damping
    def undamp(self):
        for atom in self.atoms:
            atom.damping = 0
        self.damped = False
        
    def damp(self):
        if not self.damped:
            for atom in self.atoms:
                atom.damping = 20
            
        
        
        

