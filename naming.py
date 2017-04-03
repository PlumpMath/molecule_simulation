from collections import Counter

from itertools import count

prefixes = {     1: "Meth",
                2: "Eth",
                3: "Prop",
                4: "But",
                5: "Pent",
                6: "Hex",
                7: "Sept",
                8: "Oct",
                9: "Non",
                10: "Dec"
}
def name(molecule):
    for atom in molecule.atoms:
        if "doubles" in atom and atom.get_charge() != 0:
            # no octet
            molecule.text.text = ""
            return
    ##names molecule by composition
    counter = Counter([atom.name for atom in molecule.atoms])
    
    keys = counter.keys()
    
    text = ""
    
    ###hydrocarbons
    if {"Hydrogen","Carbon"} == keys:
        carbons = counter.get("Carbon")
        hydrogens = counter.get("Hydrogen")
        
        #alkanes
        if hydrogens == 2 * carbons + 2:
            text = prefixes[carbons] + "ane"
            
        #alkenes
        elif hydrogens == 2 * carbons:
            for atom in molecule.atoms:
                if "doubles" in atom:
                    if atom["doubles"]:
                        text = prefixes[carbons] + "ene"
                        break
            ##cycloalkane
            if "ene" not in text:
                text = "Cyclo" + prefixes[carbons].lower() + "ane"
        ##alkynes
        elif hydrogens == 2 * carbons - 2:
            text = prefixes[carbons] + "yne"
        ##benzene
        if carbons == 6 and hydrogens == 6:
            text = "Benzene"
            
       
    ##other
    elif {"Hydrogen","Oxygen","Lone Pair"} == keys:
        if counter.get("Hydrogen") == 2 and counter.get("Oxygen") == 1:
            text = "Water"
    elif {"Carbon","Oxygen","Lone Pair"} == keys:
        if counter.get("Oxygen") == 2 and counter.get("Carbon") == 1:
            text = "Carbon Dioxide"
    elif {"Hydrogen"} == keys:
        text = "Hydrogen gas"
    elif {"Bromine"} == keys:
        text = "Bromine"
    molecule.text.text = text
