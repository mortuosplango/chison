import functools

import threading

import time

fns = chimera.mousemodes.functionCallables("rotate")               

def get_neighbors(obj):
        if 'bondedResidues' in dir(obj):
           return obj.bondedResidues()
        else:
           return obj.primaryNeighbors()


def color_element(obj, level, maxLevel):        
        #print(obj, level, maxLevel)
        if(not obj.doneC):
                wait_time = 0.15
                col = 1.0 - (float(level)/maxLevel * 0.8)
                set_color(obj, chimera.MaterialColor(col, col, col))
                obj.doneC = True
                real_eye = ch_get_real_eye()
                coords = get_coords(obj)
                has_sobj = False
                sobjs = list()
                amp = (1.0 - (float(level)/maxLevel))
                if 'sobj' in dir(obj):
                        for sid in obj.sobj:
                                if sid in mapping_objects:
                                        has_sobj = True
                                        sobjs.append(mapping_objects[sid])
                                        
                if has_sobj:
                        for sobj in sobjs:
                                modify_sound_object(sobj, "gate", amp, "t_trig", amp)
                elif grains:
                        real_eye = ch_get_real_eye()
                        coords = get_coords(obj)
                        dist, az, ele = ch_calculate_position(real_eye, coords)
                        sobjs.append(grain_maker_fn(obj, dist, az, ele, level, maxLevel))
                                
                time.sleep(wait_time)
                if(level < maxLevel):
                        neighbors = list()
                        for r in get_neighbors(obj):
                                t = threading.Thread(target=color_element,
                                                     args=(r, level +1, maxLevel))
                                t.start()
                time.sleep(wait_time*4)
                for sobj in sobjs:
                        modify_sound_object(sobj, "gate", 0)
                restore_color(obj) 


def cb2(v,e,ofn):
        #print("mouse 3", v, e)
        obj = v.pick(e.x,e.y)
        # do it twice to be sure
        obj = v.pick(e.x,e.y)
        if len(obj) > 0:
                target = obj[0]
                if 'halfbond' in dir(target):
                        target = target.atoms[0]
                if not 'molecule' in dir(target):
                        target = target.atoms[0]
                for a in target.molecule.atoms:
                        a.doneC = False
                
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

