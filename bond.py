from bge import logic, types, render
from mathutils import Vector, Matrix

gdict = logic.globalDict
# renders bonds between atoms




class Bond:
    # subclass for particle that manages bond rendering
    def __init__(self,particle):
        self.particle = particle
        self.inverted = False

    def draw_line(self,second,color):
        render.drawLine(self.particle.worldPosition,second.worldPosition,color)
        
    def draw_bonds(self,queue):
        self.queue = queue
        self.draw_singles()
        self.draw_doubles()
        self.draw_triples()     
        
    def draw_singles(self):
        particle = self.particle
        
        for bond in particle["bonds"]:
            
            # already had bonds drawn
            if bond not in self.queue:
                continue
            
            if bond.name == "Lone Pair":
                continue
            
            self.draw_line(bond,[1,1,1])
            
    def draw_doubles(self):
        # draw and align p bonds in doubles
        particle = self.particle
        
        if "doubles" in particle and particle["doubles"]:
            for i,bond in enumerate(particle["doubles"]):
                if bond in self.queue:
                    self.draw_line(bond,[0.5,1,1])  
 
                bondvector = bond.worldPosition - particle.worldPosition
                pos = particle.worldPosition
                
                
                for index,atom in enumerate(bond["doubles"]):
                    if particle is atom:
                        j = index
                if i == 0 and j == 0:
                    yaxis = particle.getAxisVect((0,1,0))
                    pbond = yaxis - yaxis.project(bondvector) 
                    bond.alignAxisToVect(pbond,1,0.1)
                    if len(particle["doubles"]) == 1:
                        # checks if pbonds are in y axis               
                        self.inverted = False
                else:
                    xaxis = particle.getAxisVect((1,0,0)) 
                    pbond = xaxis - xaxis.project(bondvector) 
                    bond.alignAxisToVect(pbond,0,0.1)
                    if len(particle["doubles"]) == 1:
                        self.inverted = True
                    
                render.drawLine(pos - pbond * 10,pos + pbond * 10,[0.5,1,1])            
                
    def draw_triples(self):
        particle = self.particle
        
        if "triple" in particle and particle["triple"]:
            
            bond = particle["triple"]
                
            if bond in self.queue:
                self.draw_line(bond,[0,1,1])

            bondvector = bond.worldPosition - particle.worldPosition
            pos = particle.worldPosition
             
            yaxis = particle.getAxisVect((0,1,0))
            pbond = yaxis - yaxis.project(bondvector) 
            bond.alignAxisToVect(pbond,1,0.1)
            render.drawLine(pos - pbond * 10,pos + pbond * 10,[0,1,1])
            
            xaxis = particle.getAxisVect((1,0,0))
            pbond2 = xaxis - xaxis.project(bondvector) 
            bond.alignAxisToVect(pbond,1,0.1)
            render.drawLine(pos - pbond2* 10,pos + pbond2 * 10,[0.5,1,1])

           

            
            
                