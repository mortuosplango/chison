import functools

import threading

import time

fns = chimera.mousemodes.functionCallables("rotate")


def set_color(obj, color):
        if 'ribbonColor' in dir(obj):
                if (not 'origColor' in dir(obj)) or (obj.origColor == None):
                        obj.origColor = obj.ribbonColor
                obj.ribbonColor = color
                for a in obj.atoms:
                        if a.display:
                                set_color(a, color)
        elif 'color' in dir(obj):
                if (not 'origColor' in dir(obj)) or (obj.origColor == None):
                        obj.origColor = obj.color
                obj.color = color


def restore_color(obj):
        if 'ribbonColor' in dir(obj):
                obj.ribbonColor = obj.origColor
                for a in obj.atoms:
                        if a.display:
                                restore_color(a)
        elif 'color' in dir(obj):
                obj.color = obj.origColor

                

def color_element(obj, level, maxLevel):
        #print(obj, level, maxLevel)
        if(not obj.doneC):
                if True:
                        wait_time = 0.05
                        set_color(obj, chimera.MaterialColor(float(level)/maxLevel,0.5,0.1))
                        obj.doneC = True
                        real_eye = ch_get_real_eye()
                        coords = get_coords(obj)
                        dist, az, ele = ch_calculate_position(real_eye, coords)
                        sobj = make_sound_object(None, "grain", "freq", 110 * (level+1 ),
                                                 "dist", dist, "az", az, "ele", ele,
                                                 "amp", (1.0 - (float(level)/maxLevel)) * 0.5 )

                        time.sleep(wait_time)
                        if(level < maxLevel):
                                for r in obj.bondedResidues():
                                        t = threading.Thread(target=color_element,
                                                             args=(r, level +1, maxLevel))
                                        t.start()
                        time.sleep(wait_time*13)
                        restore_color(obj)


def get_neighbors(obj):
        if 'bondedResidues' in dir(obj):
           return obj.bondedResidues()
        else:
           return obj.primaryNeighbors()
        

grains = True

def make_grain(obj, dist, az, ele, level, maxLevel):
        return make_sound_object(None, grain_type, "freq", 110 * (level+1 ),
                                 "dist", dist, "az", az, "ele", ele,
                                 "amp", (1.0 - (float(level)/maxLevel)) * 0.5 )
grain_maker_fn = make_grain        

def color_element(obj, level, maxLevel):        
        #print(obj, level, maxLevel)
        if(not obj.doneC):
                if True:
                        wait_time = 0.05
                        set_color(obj, chimera.MaterialColor(float(level)/maxLevel,0.5,0.1))
                        obj.doneC = True
                        real_eye = ch_get_real_eye()
                        coords = get_coords(obj)
                        has_sobj = False
                        sobj = None
                        if('sobj' in dir(obj)) and (obj.sobj in mapping_objects):
                                has_sobj = True
                                sobj = mapping_objects[obj.sobj]                                
                        if has_sobj:
                                modify_sound_object(sobj, "gate", 1)
                        elif grains:
                                real_eye = ch_get_real_eye()
                                coords = get_coords(obj)
                                dist, az, ele = ch_calculate_position(real_eye, coords)
                                sobj = grain_maker_fn(obj, dist, az, ele, level, maxLevel)
                                        
                        time.sleep(wait_time)
                        if(level < maxLevel):
                                neighbors = list()
                                for r in get_neighbors(obj):
                                        t = threading.Thread(target=color_element,
                                                             args=(r, level +1, maxLevel))
                                        t.start()
                        time.sleep(wait_time*4)
                        if has_sobj or grains:
                                modify_sound_object(sobj, "gate", 0)
                        restore_color(obj) 


def cb2(v,e,ofn):
        #print("mouse 3", v, e)
        obj = v.pick(e.x,e.y)
        # do it twice to be sure
        obj = v.pick(e.x,e.y)
        if True:
                target = obj[0]
                for a in target.molecule.atoms:
                        a.doneC = False
                if 'halfbond' in dir(target):
                        target = target.atoms[0]
                if ('residue' in dir(target)) and not is_ligand(target.molecule):
                        target = target.residue
                if 'residues' in dir(target.molecule):
                   for r in target.molecule.residues:
                        r.doneC = False
                t = threading.Thread(target=color_element,
                                     args=(target, 0, 5))
                t.start()
        if False:
                print("failed")
                pass
        ofn(v,e)

        
# get current button function
fns = chimera.mousemodes.functionCallables("rotate")

chimera.mousemodes.addFunction("ison", (functools.partial(cb2,ofn=fns[0]),
                                 fns[1],
                                 fns[2]))

chimera.mousemodes.setButtonFunction('1', (), "ison", isDefault=True)

