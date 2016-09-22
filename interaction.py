
# interactivity

import functools

import threading

import time

import chimera

import chimera_global as cg

import chimera_utils
reload(chimera_utils)
from chimera_utils import *

import sound_objects as so

fns = chimera.mousemodes.functionCallables("rotate")               

grains = False

def default_grain(obj, dist, az, ele, level, maxLevel):
        return so.make_sound_object(None, "grain", "freq", 220 * (level+1 ),
                                 "dist", dist, "az", az, "ele", ele,
                                 "amp", (1.0 - (float(level)/maxLevel)) * 0.5 )

grain_maker_fn = default_grain

levels = 5

speed = 0.25

stagger = True

def set_grain_maker_fn(fn):
        print("setting grain maker fn")
        global grain_maker_fn
        grain_maker_fn = fn


def set_levels(new_level):
        global levels
        levels = new_level

def set_speed(new_speed):
        global speed
        speed = new_speed

def set_stagger(new_stagger):
        global stagger
        stagger = new_stagger

def color_element(obj, level, maxLevel):        
        #print(obj, level, maxLevel)
        if(not obj.doneC):
                wait_time = speed
                col = (float(level)/max(maxLevel, 1) )
                #print level, obj, "coloring"
                set_color(obj, chimera.MaterialColor(1.0, col, col))
                obj.doneC = True
                real_eye = ch_get_real_eye()
                coords = get_coords(obj)
                has_sobj = False
                sobjs = list()
                amp = (1.0 - (float(level)/max(maxLevel, 1)))
                #print(grain_maker_fn)
                if hasattr(obj, 'sobj') and (obj.sobj != None):
                        for sid in obj.sobj:
                                if sid in cg.mapping_objects:
                                        has_sobj = True
                                        sobjs.append(cg.mapping_objects[sid])
                                        
                if has_sobj:
                        for sobj in sobjs:
                                so.modify_sound_object(sobj, "gate", amp, "t_trig", 1)
                elif grains:
                        real_eye = ch_get_real_eye()
                        coords = get_coords(obj)
                        dist, az, ele = ch_calculate_position(real_eye, coords)
                        sobj = grain_maker_fn(obj, dist, az, ele, level, maxLevel)
                        if (sobj != None):
                            sobjs.append(sobj)

                if(level == 0) or not stagger:
                        time.sleep(wait_time)
                else:
                        time.sleep(wait_time * 2)
                if(level < maxLevel):
                        neighbors = list()
                        for i,r in enumerate(get_neighbors(obj)):
                                t = threading.Thread(target=color_element,
                                                     args=(r, level +1, maxLevel))
                                t.start()
                                if (level == 0) and (i == 0) and stagger:
                                        time.sleep(wait_time)
                time.sleep(wait_time*4)
                for sobj in sobjs:
                        so.modify_sound_object(sobj, "gate", 0)
                #print level, obj, "restoring"
                restore_color(obj) 


def interaction_callback(v,e,ofn):
        #print("mouse 3", v, e)
        obj = v.pick(e.x,e.y)
        # do it twice to be sure
        obj = v.pick(e.x,e.y)
        if len(obj) > 0:
                target = obj[0]
                if hasattr(target, 'halfbond'):
                        target = target.atoms[0]
                if not hasattr(target, 'molecule'):
                        target = target.atoms[0]
                for a in target.molecule.atoms:
                        a.doneC = False
                
                if hasattr(target, 'residue') and not is_ligand(target.molecule):
                        target = target.residue
                if hasattr(target.molecule, 'residues'):
                   for r in target.molecule.residues:
                        r.doneC = False
                t = threading.Thread(target=color_element,
                                     args=(target, 0, levels))
                t.start()
        else:
                print("failed")
        ofn(v,e)

        
# get current button function
fns = chimera.mousemodes.functionCallables("rotate")

chimera.mousemodes.addFunction("ison", (functools.partial(interaction_callback,ofn=fns[0]),
                                 fns[1],
                                 fns[2]))

chimera.mousemodes.setButtonFunction('1', (), "ison", isDefault=True)

