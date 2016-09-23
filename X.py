# -*- coding: utf-8 -*-

# debug flag
DEBUG = False

basepath = os.path.dirname(os.path.abspath(__file__))
import threading


import utils
reload(utils)
from utils import *

import spatialisation
reload(spatialisation)
from spatialisation import *

import sound_objects
reload(sound_objects)
from sound_objects import *

import chimera_utils
reload(chimera_utils)
from chimera_utils import *

import interaction
reload(interaction)

import sonification_settings
reload(sonification_settings)

cleanup_fn = identity

import chimera_global as cg

grains = False

def m_none(models, objects):
        # init mapping
        if(len(objects) == 0):
                interaction.grain_maker_fn = interaction.default_grain
                interaction.grains = False
                objects[0] = None

        return objects


tFrame = 'new frame'

def m_bfactors_cleanup():
    print("cleaning up bfactors")

    for model in chimera.openModels.list(modelTypes=[chimera.Molecule]):
        for i,atom in enumerate(model.atoms):
            try:
               atom.color = atom.origColor
            except:
                pass
    try:
            chimera.triggers.deleteHandler(tFrame, hFrame)
    except:
            pass

# cutoff for betafactors    
cutoff = 80.0


def m_bfactors_animation(trigger, additional, frameNo):
    onFrame = 0
    offFrame = 1
    for key, sobj in cg.mapping_objects.iteritems():
        obj = chimera.openModels.list(id=sobj['ch_model_id'])[0].residues[
            sobj['ch_residue']]
        if sobj['anim']:    
                lenAnim = sobj['len_anim']
                posAnimF = (frameNo % lenAnim)
                #posAnim = posAnimF/lenAnim

                if((onFrame == posAnimF) or (offFrame == posAnimF)):
                    if(onFrame == posAnimF):
                        modify_sound_object(sobj, "gate", 1)
                        if animate:
                            set_color(obj, chimera.MaterialColor(1,0.5,0.2))
                    else:
                        modify_sound_object(sobj, "gate", 0)
                        if animate:
                            restore_color(obj)

animate = False
    
def bfactor_for_res(res):
    bfactors = list()
    for a in res.atoms:
        bfactors.append(a.bfactor)
    arr = np.array(bfactors)
    return arr.mean(), arr.min(), arr.max()
        

def m_bfactors_grain(obj, dist, az, ele, level, maxLevel):
        bfactor, bmin, bmax = bfactor_for_res(obj)
        return make_sound_object(None, "bfactor2Grain",
                                 "dist", dist, "az", az, "ele", ele,
                                 "amp", (1.5 - (float(level)/max(maxLevel, 1))),
                                 "midinote", 55 + ((bfactor - cutoff) * 0.15) )


def m_bfactors(models, objects):
        # init mapping
        if(len(objects) == 0):
                interaction.grain_maker_fn = m_bfactors_grain
                interaction.grains = True

                # permanently display top 20% of bfactor values
                global cutoff
                bfs = list()
                for model in chimera.openModels.list(modelTypes=[chimera.Molecule]):
                        for i,res in enumerate(model.residues):
                                bfactor, bmin, bmax = bfactor_for_res(res)
                                bfs.append(bfactor)
                bfa = np.array(bfs)
                bfa.sort()
                cutoff = bfa[len(bfa) * 0.8]
                
                for model in models.list(modelTypes=[chimera.Molecule]):
                        for i,res in enumerate(model.residues):
                                bfactor, bmin, bmax = bfactor_for_res(res)
                                if(bfactor > cutoff):
                                    rhfreq = ((bmax - cutoff) / 40 + 1)/20.0
                                    sobj = make_sound_object(None, "bfactor")
                                    sobj = modify_sound_object(sobj,
                                                               "rhfreq", rhfreq,
                                                               "midinote", 55 + ((bfactor - cutoff) * 0.15))
                                    sobj['len_anim'] =  max(1, int(round(15/rhfreq))) * 2
                                    sobj['ch_model_id'] = model.id
                                    sobj['ch_residue'] = i
                                    sobj['anim'] = bmax > cutoff
                                    res.sobj = [sobj['id']]
                                    objects[sobj['id']] = sobj
                #global hFrame
                #hFrame = chimera.triggers.addHandler(tFrame,m_bfactors_animation, None)

                #global cleanup_fn
                #cleanup_fn = m_bfactors_cleanup

        # update positions
        real_eye = ch_get_real_eye()

        for key, sobj in objects.iteritems():
                obj = chimera.openModels.list(id=sobj['ch_model_id'])[0].residues[
                    sobj['ch_residue']]
                coords = get_coords(obj)
                dist, az, ele = ch_calculate_position(real_eye, coords)
                sobj = modify_sound_object(sobj,
                            "amp", np.interp(dist, [0,500], [0.8,0.01]))
                objects[key] = position_sound_object(sobj, dist, az, ele)
        return objects
    

######### docking
"""
Run only once: FindHBonds
    
chimera.runCommand("hbond intermodel 1 intramodel 0 reveal 1 showdist 1")
        
    """
"""
def m_docking_grain(obj, dist, az, ele, level, maxLevel):
        return make_sound_object(None, "hbondGrain",
                                 "freq", 110 * (level+1 ),
                                 "dist", dist, "az", az, "ele", ele,
                                 "amp", (1.0 - (float(level)/max(maxLevel, 1))) * 0.5 )

def m_docking_grain(obj, dist, az, ele, level, maxLevel):
        bfactor, bmin, bmax = bfactor_for_res(obj)
        rhfreq = (bfactor - cutoff) / 10 + 1
        return make_sound_object(None, "bfactor2Grain",
                                 "dist", dist, "az", az, "ele", ele,
                                 "amp", (1.0 - (float(level)/max(maxLevel, 1))),
                                 "rhfreq", rhfreq,
                                 "freq", 440 + ((bfactor - cutoff) * 10) * 0.5)
"""


def m_docking(models, objects):
        # init mapping
        if(len(objects) == 0):
                interaction.grain_maker_fn = m_bfactors_grain
                interaction.grains = True
                for model in models.list(modelTypes=[chimera.Molecule]):
                        if model.display and is_ligand(model):
                                for i,r in enumerate(model.atoms):
                                        midinote = ((r.molecule.dockGridVdw + 50) * 30.0/100) + 55
                                        mfreq = ((r.charge + 1) * 0.5) * 200
                                        #print(midinote, mfreq)
                                        sobj = make_sound_object(None, "hbond1",
                                                                 "midinote", midinote,
                                                                 "mfreq", mfreq,
                                                                )
                                        sobj['ch_model_id'] = model.id
                                        sobj['ch_model_subid'] = model.subid
                                        sobj['ch_atom'] = i
                                        objects[sobj['id']] = sobj
                                        r.sobj = [sobj['id']]
                                        for j,b in enumerate(r.pseudoBonds):
                                            sobj = make_sound_object(None, "hbond")
                                            sobj['ch_model_id'] = model.id
                                            sobj['ch_model_subid'] = model.subid
                                            sobj['ch_atom'] = i
                                            sobj['ch_pseudoBond'] = j
                                            objects[sobj['id']] = sobj
                                            r.sobj.append(sobj['id'])
        # update positions
        real_eye = ch_get_real_eye()
        
        for key, sobj in objects.iteritems():
            model = chimera.openModels.list(id=sobj['ch_model_id'], subid=sobj['ch_model_subid'])[0]
            if(model.display):
                obj = model.atoms[sobj['ch_atom']]
                coords = obj.xformCoord()
                objects[key] = ch_position_sound_object(sobj, real_eye, coords)
        return objects





def stop_mapping(objects):
        # double stop. probably one can go in the future
        for key, sobj in objects.iteritems():
                if(sobj != None) and sobj.has_key('id'):
                        delete_sound_object(sobj)
        reset_sound_objects()   
        cleanup_fn()
        return dict()

def set_mapping(new_map_fn):
    cg.mapping_objects = stop_mapping(cg.mapping_objects)
    global mapping_fn
    mapping_fn = new_map_fn
    global cleanup_fn
    cleanup_fn = identity
    cg.mapping_objects = mapping_fn(chimera.openModels, cg.mapping_objects)


# clean the slate both on client and on sound server

reset_sound_objects()

mapping_fn = m_none



# chimera
import chimera

ch_models = dict()

def ch_add_model(model):
        return ch_delete_model(0)

def ch_modify_model():
        pass    

def ch_delete_model(id):
        print("deleting model ", id)
        """
        for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
                for a in m.atoms:
                        a.doneC = False
                        a.origColor = a.color
                for r in m.residues:
                        r.doneC = False
                        r.origColor = r.ribbonColor
        """
        objects = stop_mapping(cg.mapping_objects)
        objects = mapping_fn(chimera.openModels, objects)
        return objects

def ch_change_view(viewer, models):
        objects = mapping_fn(chimera.openModels, cg.mapping_objects)
        return objects


# chimera triggers
modelTrigger = u'Model' 
viewerTrigger = u'Viewer'

try:
        chimera.triggers.deleteHandler(modelTrigger, modelHandler)
        chimera.triggers.deleteHandler(viewerTrigger, viewerHandler)
except:
        pass

# animation trigger
tFrame = 'new frame'
try:
        chimera.triggers.deleteHandler(tFrame, hFrame)
except:
        pass


def viewer_changed(trigger, additional, atomChanges):
        if DEBUG:
                print("triggered viewer changed")
        cg.mapping_objects = ch_change_view(chimera.viewer, chimera.openModels)
                                    

openModelIds = set()

def models_changed(trigger, additional, changes):
        global openModelIds
        for i in changes.modified:
                # TODO
                #print("triggered modified", changes.modified, changes.reasons)
                #print("triggered modified", changes.reasons)
                
                # send_osc("/model/modified", i.id, *changes.reasons)
                newOpenModelIds = set()
                if(u'display changed' in changes.reasons):
                        #print("triggered modified", changes.created, changes.reasons)
                        for model in chimera.openModels.list():
                                newOpenModelIds.add(model.id)
                        openModelIds = newOpenModelIds
                        cg.mapping_objects = ch_add_model(i)
        for i in changes.created:
                print("triggered create", changes.created, changes.reasons)
                cg.mapping_objects = ch_add_model(i)
                newOpenModelIds = set()
                for model in chimera.openModels.list():
                        newOpenModelIds.add(model.id)
                openModelIds = newOpenModelIds
        for i in changes.deleted:
                print("triggered delete", changes.reasons)
                newOpenModelIds = set()
                
                for model in chimera.openModels.list():
                        newOpenModelIds.add(model.id)
                for id in openModelIds.difference(newOpenModelIds):
                        cg.mapping_objects = ch_delete_model(id)
                openModelIds = newOpenModelIds


viewerHandler = chimera.triggers.addHandler(viewerTrigger,viewer_changed, None)
modelHandler = chimera.triggers.addHandler(modelTrigger, models_changed, None)


# GUI
import chimera

import Tkinter

from chimera.baseDialog import ModelessDialog

mapping = None

mappings = {
    #'Test mapping': m_test,
    'Docking': m_docking,
    'Betafactors': m_bfactors,
    'None': m_none,
    #'Earcons': m_earcons,
    #'none': identity
}


class MappingDialog(ModelessDialog):    
    name = "mapping dialog"

    buttons = ("Apply", "Close")

    title = "Mapping settings"

    def fillInUI(self, parent):

        global mapping
        
        width = 16
        
        mapping = Tkinter.StringVar(parent)
        mapping.set(mappings.keys()[0])

        mappingLabel = Tkinter.Label(parent, text='Sonification Mapping')
        mappingLabel.grid(column=0, row=0)
        
        # Create the menu button and the option menu that it brings up.
        mappingButton = Tkinter.Menubutton(parent, indicatoron=1,
                                        textvariable=mapping, width=width,
                                        relief=Tkinter.RAISED, borderwidth=2)
        mappingButton.grid(column=1, row=0)
        mappingMenu = Tkinter.Menu(mappingButton, tearoff=0)
        
        #    Add radio buttons for all possible choices to the menu.
        for mapname in mappings.keys():
            mappingMenu.add_radiobutton(label=mapname, variable=mapping, value=mapname)
            
        #    Assigns the option menu to the menu button.
        mappingButton['menu'] = mappingMenu



    def Apply(self):
        print("setting mapping to " + mapping.get())
        set_mapping(mappings[mapping.get()])

redisplay(MappingDialog)

