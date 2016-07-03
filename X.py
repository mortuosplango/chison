# -*- coding: utf-8 -*-

# debug flag
DEBUG = False

basepath = os.path.dirname(os.path.abspath(__file__))

# helper functions
def identity(*args):
    if len(args) == 1:
        return args[0]  
    return args

def assoc(_d, key, value):
    from copy import deepcopy
    d = deepcopy(_d)
    d[key] = value
    return d


# spatialisation
import math
from numpy import linalg

halfpi = (0.5 * math.pi)

def angle2d(x1, y1,x2, y2):
        return halfpi - math.atan2(y1 - y2, x1 - x2)

def elevation(eye, point):
        return angle2d(eye[1], eye[2],
                       point[1],point[2])

def azimuth(eye, point):
        return angle2d(eye[0], eye[2],
                       point[0],point[2])

def calculate_position(eye, point,distance_offset=0):
        # distance shouldn't become 0 for ambisonics
        distance = max(0.01, linalg.norm(point-eye) + distance_offset)
        az = azimuth(eye, point)
        ele = elevation(eye, point)
        return distance, az, ele


# osc
import simpleOSC
simpleOSC.initOSCClient(port=57120)
def send_osc(addr, *args):
        return simpleOSC.sendOSCMsg(addr, args)     

# sound object management
"""
Abstract sound objects, the sound server (e.g., SuperCollider) decides what to do with them

/obj/new id sound_type
/obj/modify id attribute_name attribute_value
/obj/delete id
"""

# count up ids used to sync between python and sound server
id = 0

def load_sample(oid, path):
        if(oid == None):
                global id
                oid = id
                id += 1
        send_osc("/sample/new", oid, path)
        return dict(id=oid, path=path)

def make_sound_object(oid, type, *args):
        if(oid == None):
                global id
                oid = id
                id += 1
        send_osc("/obj/new", oid, type, *args)
        return dict(id=oid, type=type)

def modify_sound_object(obj, *args):
        send_osc("/obj/modify", obj['id'], *args)
        for i in range(int(len(args)/2)):
            attr = args[i]
            val = args[i+1]
            obj = assoc(obj, attr, val)
        return obj

def delete_sound_object(obj):
        send_osc("/obj/delete", obj['id'])
        return True

def position_sound_object(obj, dist, az, ele):
        obj = modify_sound_object(obj, "dist", dist, "az", az, "ele", ele)
        return obj

def reset_sound_objects():
    send_osc("/obj/reset")

def set_decoder(name):
    print("setting decoder to " + name)
    send_osc("/decoder/set", name)

def set_volume(volume):
    send_osc("/volume/set", volume)


# chimera -> sonification mapping
import chimera
import numpy as np

import functools as ft

ch_calculate_position = ft.partial(calculate_position, distance_offset=(-24))

def m_test(models, objects):
        # init mapping
        if(len(objects) == 0):
                for model in models.list(modelTypes=[chimera.Molecule]):
                        objects[model.id] = dict()
                        for i,r in enumerate(model.residues):
                                objects[model.id][i] = make_sound_object(None, "atom")
        # update positions
        viewer = chimera.viewer
        camera = viewer.camera
        realEye = chimera.Point(*camera.center)
        realEye[2] = camera.eyeZ()
        
        for model in models.list(modelTypes=[chimera.Molecule]):
                for i,r in enumerate(model.residues):
                        if(objects[model.id].has_key(i)):
                                coords = r.atoms[0].xformCoord()
                                dist, az, ele = ch_calculate_position(realEye, coords)
                                if((i == 0) and DEBUG):
                                        print(dist, az, ele)
                                objects[model.id][i] = position_sound_object(objects[model.id][i], dist, az, ele)
        return objects


def m_bfactors(models, objects):
        # cutoff for betafactors
        cutoff = 40.0
        # init mapping
        if(len(objects) == 0):
                for model in models.list(modelTypes=[chimera.Molecule]):
                        objects[model.id] = dict()
                        for i,atom in enumerate(model.atoms):
                                if(atom.bfactor > cutoff):
                                        sobj = make_sound_object(None, "bfactor")
                                        sobj = modify_sound_object(sobj,
                                                                   "rhfreq", (atom.bfactor - cutoff) / 10 + 1,
                                                                   "freq", 440 + ((atom.bfactor - cutoff) * 10))
                                        objects[model.id][i] = sobj
        # update positions
        viewer = chimera.viewer
        camera = viewer.camera
        realEye = chimera.Point(*camera.center)
        realEye[2] = camera.eyeZ()
        
        for model in models.list(modelTypes=[chimera.Molecule]):
                for i,r in enumerate(model.atoms):
                        if(objects[model.id].has_key(i)):
                                coords = r.xformCoord()
                                dist, az, ele = ch_calculate_position(realEye, coords)
                                if((i == 0) and DEBUG):
                                        print(dist, az, ele)
                                objects[model.id][i] = modify_sound_object(
                                    objects[model.id][i],
                                    "amp", np.interp(dist, [0,500], [0.8,0.01]))
                                objects[model.id][i] = position_sound_object(
                                    objects[model.id][i],
                                    dist, az, ele)
        return objects


def m_earcons(models, objects):
        # cutoff for betafactors
        cutoff = 60.0

        # init mapping
        if(len(objects) == 0):
                objects["sample"] = load_sample(None, basepath + "/samples/creak.wav")
                for model in models.list(modelTypes=[chimera.Molecule]):
                        objects[model.id] = dict()
                        for i,atom in enumerate(model.atoms):
                                if(atom.bfactor > cutoff):
                                        sobj = make_sound_object(None, "sample",
                                                                 "freq", 440 + ((atom.bfactor - cutoff) * 10),
                                                                 "sample", objects["sample"]["id"]
                                                                 )
                                        objects[model.id][i] = sobj
        # update positions
        viewer = chimera.viewer
        camera = viewer.camera
        realEye = chimera.Point(*camera.center)
        realEye[2] = camera.eyeZ()
        
        for model in models.list(modelTypes=[chimera.Molecule]):
                for i,r in enumerate(model.atoms):
                        if(objects[model.id].has_key(i)):
                                coords = r.xformCoord()
                                dist, az, ele = ch_calculate_position(realEye, coords)
                                if((i == 0) and DEBUG):
                                        print(dist, az, ele)
                                objects[model.id][i] = modify_sound_object(objects[model.id][i],
                                                                           "sample", objects["sample"]["id"],
                                                                           "amp", np.interp(dist, [0,500], [0.8,0.01]))
                                objects[model.id][i] = position_sound_object(
                                    objects[model.id][i],
                                    dist, az, ele)
        return objects



def stop_mapping(objects):
        # double stop. probably one can go in the future
        for objs in objects.values():
                if(objs.has_key('id')):
                        delete_sound_object(objs)
                else:
                        for subobject in objs.values():
                                delete_sound_object(subobject)
        reset_sound_objects()
        return dict()

def set_mapping(new_map_fn):
    global mapping_fn
    mapping_fn = new_map_fn
    global mapping_objects
    mapping_objects = stop_mapping(mapping_objects)
    mapping_objects = mapping_fn(chimera.openModels, mapping_objects)


# clean the slate both on client and on sound server
mapping_objects = dict()
reset_sound_objects()

mapping_fn = m_test
mapping_fn = m_bfactors


# chimera
import chimera

ch_models = dict()

def ch_add_model(model):
        return ch_delete_model(0)

def ch_modify_model():
        pass    

def ch_delete_model(id):
        objects = stop_mapping(mapping_objects)
        objects = mapping_fn(chimera.openModels, objects)
        return objects

def ch_change_view(viewer, models):
        objects = mapping_fn(chimera.openModels, mapping_objects)
        return objects


# chimera triggers
modelTrigger = u'Model'
viewerTrigger = u'Viewer'

try:
        chimera.triggers.deleteHandler(modelTrigger, modelHandler)
        chimera.triggers.deleteHandler(viewerTrigger, viewerHandler)
except:
        pass


def viewer_changed(trigger, additional, atomChanges):
        if DEBUG:
                print("triggered viewer changed")
        global mapping_objects
        mapping_objects = ch_change_view(chimera.viewer, chimera.openModels)
                                

openModelIds = set()

def models_changed(trigger, additional, changes):
        global openModelIds
        global mapping_objects
        for i in changes.modified:
                # TODO
                print("triggered modified", changes.modified, changes.reasons)
                # send_osc("/model/modified", i.id, *changes.reasons)
        for i in changes.created:
                try:
                        print("triggered create", changes.created, changes.reasons)
                        mapping_objects = ch_add_model(i)
                        newOpenModelIds = set()
                        for model in chimera.openModels.list():
                                newOpenModelIds.add(model.id)
                        openModelIds = newOpenModelIds
                except:
                        pass
        for i in changes.deleted:
                print("triggered delete", changes.reasons)
                newOpenModelIds = set()
                
                for model in chimera.openModels.list():
                        newOpenModelIds.add(model.id)
                for id in openModelIds.difference(newOpenModelIds):
                        mapping_objects = ch_delete_model(id)
                openModelIds = newOpenModelIds


viewerHandler = chimera.triggers.addHandler(viewerTrigger,viewer_changed, None)
modelHandler = chimera.triggers.addHandler(modelTrigger, models_changed, None)


# GUI
import chimera

import Tkinter

from chimera.baseDialog import ModelessDialog

# last selected decoder
decoder = None

# available decoders
decoders = [
    'KEMAR binaural 1',
    'KEMAR binaural 2',
    'UHJ stereo',
    'synthetic binaural',
]

mapping = None

mappings = {
    'Test mapping': m_test,
    'Betafactors': m_bfactors,
    'Earcons': m_earcons,
}

default_volume = 0.5
volume = None


class DecoderDialog(ModelessDialog):    
    name = "decoder dialog"

    buttons = ("Apply", "Close")

    title = "Set Ambisonics Decoder"

    def fillInUI(self, parent):

        global decoder

        width = 16

        decoder = Tkinter.StringVar(parent)
        decoder.set(decoders[3])

        decoderLabel = Tkinter.Label(parent, text='Ambisonic Decoder')
        decoderLabel.grid(column=0, row=0)
        
        # Create the menu button and the option menu that it brings up.
        decoderButton = Tkinter.Menubutton(parent, indicatoron=1,
                                        textvariable=decoder, width=width,
                                        relief=Tkinter.RAISED, borderwidth=2)
        decoderButton.grid(column=1, row=0)
        decoderMenu = Tkinter.Menu(decoderButton, tearoff=0)
        
        #    Add radio buttons for all possible choices to the menu.
        for dec in decoders:
            decoderMenu.add_radiobutton(label=dec, variable=decoder, value=dec)
            
        #    Assigns the option menu to the menu button.
        decoderButton['menu'] = decoderMenu


        global mapping
        
        mapping = Tkinter.StringVar(parent)
        mapping.set(mappings.keys()[0])

        mappingLabel = Tkinter.Label(parent, text='Sonification Mapping')
        mappingLabel.grid(column=0, row=1)
        
        # Create the menu button and the option menu that it brings up.
        mappingButton = Tkinter.Menubutton(parent, indicatoron=1,
                                        textvariable=mapping, width=width,
                                        relief=Tkinter.RAISED, borderwidth=2)
        mappingButton.grid(column=1, row=1)
        mappingMenu = Tkinter.Menu(mappingButton, tearoff=0)
        
        #    Add radio buttons for all possible choices to the menu.
        for mapname in mappings.keys():
            mappingMenu.add_radiobutton(label=mapname, variable=mapping, value=mapname)
            
        #    Assigns the option menu to the menu button.
        mappingButton['menu'] = mappingMenu


        global volume

        volume = Tkinter.DoubleVar(parent)
        volume.set(default_volume)

        label = Tkinter.Label(parent, text='Volume')
        label.grid(column=0,row=2)

        scale = Tkinter.Scale(parent, from_=0, to=1.0, width=width,
                              resolution=0.01, orient=Tkinter.HORIZONTAL,
                              variable=volume, showvalue=0,
                              command=lambda self: set_volume(volume.get()))
        scale.grid(column=1, row=2)

    def Apply(self):
        set_decoder(decoder.get())
        print("setting mapping to " + mapping.get())
        set_mapping(mappings[mapping.get()])

if(chimera.dialogs.find(DecoderDialog.name) == None):
    chimera.dialogs.register(DecoderDialog.name, DecoderDialog)
else:
    chimera.dialogs.reregister(DecoderDialog.name, DecoderDialog)

chimera.dialogs.display(DecoderDialog.name)
