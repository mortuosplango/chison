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
import chimera

halfpi = (0.5 * math.pi)


def angle2d(p1, p2):
        return halfpi - math.atan2(p1.y - p2.y, p1.x - p2.x)

def elevation(eye, point):
        return angle2d(chimera.Point(eye.y, eye.z,0),
                       chimera.Point(point.y,point.z,0))

def azimuth(eye, point):
        return angle2d(chimera.Point(eye.x, eye.z,0),
                       chimera.Point(point.x,point.z,0))

def calculate_position(eye, point):
        # distance shouldn't become 0 for ambisonics
        distance = max(0.01, eye.distance(point) - 24)
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

def make_sound_object(oid, type):
        if(oid == None):
                global id
                oid = id
                id += 1
        send_osc("/obj/new", oid, type)
        return dict(id=oid, type=type)

def modify_sound_object(obj, attr, val):
        send_osc("/obj/modify", obj['id'], attr, val)
        return assoc(obj, attr, val)

def delete_sound_object(obj):
        send_osc("/obj/delete", obj['id'])
        return True

def position_sound_object(obj, dist, az, ele):
        obj = modify_sound_object(obj, "dist", dist)
        obj = modify_sound_object(obj, "az", az)
        obj = modify_sound_object(obj, "ele", ele)
        return obj

def reset_sound_objects():
    send_osc("/obj/reset")

def set_decoder(name):
    print("setting decoder to ", name)
    send_osc("/decoder/set", name)


# chimera -> sonification mapping
import chimera
import numpy as np

def m_test(models, objects):
        # init mapping
        if(len(objects) == 0):
                for model in models:
                        objects[model.id] = dict()
                        for i,r in enumerate(model.residues):
                                objects[model.id][i] = make_sound_object(None, "atom")
        # update positions
        om = chimera.openModels.list()
        viewer = chimera.viewer
        camera = viewer.camera
        realEye = chimera.Point(*camera.center)
        realEye[2] = camera.eyeZ()
        
        for model in models:
                for i,r in enumerate(model.residues):
                        if(objects[model.id].has_key(i)):
                                coords = r.atoms[0].xformCoord()
                                dist, az, ele = calculate_position(realEye, coords)
                                if((i == 0) and DEBUG):
                                        print(dist, az, ele)
                                objects[model.id][i] = position_sound_object(objects[model.id][i], dist, az, ele)
        return objects


def m_bfactors(models, objects):
        # cutoff for betafactors
        cutoff = 40.0
        # init mapping
        if(len(objects) == 0):
                for model in models:
                        objects[model.id] = dict()
                        for i,atom in enumerate(model.atoms):
                                if(atom.bfactor > cutoff):
                                        sobj = make_sound_object(None, "bfactor")
                                        sobj = modify_sound_object(sobj, "rhfreq", (atom.bfactor - cutoff) / 10 + 1)
                                        sobj = modify_sound_object(sobj, "freq", 440 + ((atom.bfactor - cutoff) * 10))
                                        objects[model.id][i] = sobj
        # update positions
        om = chimera.openModels.list()
        viewer = chimera.viewer
        camera = viewer.camera
        realEye = chimera.Point(*camera.center)
        realEye[2] = camera.eyeZ()
        
        for model in models:
                for i,r in enumerate(model.atoms):
                        if(objects[model.id].has_key(i)):
                                coords = r.xformCoord()
                                dist, az, ele = calculate_position(realEye, coords)
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
                for model in models:
                        objects[model.id] = dict()
                        for i,atom in enumerate(model.atoms):
                                if(atom.bfactor > cutoff):
                                        sobj = make_sound_object(None, "sample")
                                        sobj = modify_sound_object(sobj, "freq", 440 + ((atom.bfactor - cutoff) * 10))
                                        sobj = modify_sound_object(sobj, "sample", objects["sample"]["id"])
                                        objects[model.id][i] = sobj
        # update positions
        om = chimera.openModels.list()
        viewer = chimera.viewer
        camera = viewer.camera
        realEye = chimera.Point(*camera.center)
        realEye[2] = camera.eyeZ()
        
        for model in models:
                for i,r in enumerate(model.atoms):
                        if(objects[model.id].has_key(i)):
                                coords = r.xformCoord()
                                dist, az, ele = calculate_position(realEye, coords)
                                if((i == 0) and DEBUG):
                                        print(dist, az, ele)
                                objects[model.id][i] = modify_sound_object(objects[model.id][i], "sample", objects["sample"]["id"])
                                objects[model.id][i] = modify_sound_object(
                                    objects[model.id][i],
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
    mapping_objects = mapping_fn(chimera.openModels.list(), mapping_objects)


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
        objects = mapping_fn(chimera.openModels.list(), objects)
        return objects

def ch_change_view(viewer, models):
        objects = mapping_fn(chimera.openModels.list(), mapping_objects)
        return objects


# chimera triggers
try:
        chimera.triggers.deleteHandler(u'Model', modelHandler)
        chimera.triggers.deleteHandler(u'Viewer', viewerHandler)
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
        global g3
        
        g3 = [trigger, additional, changes]

viewerHandler = chimera.triggers.addHandler( u'Viewer',viewer_changed, None)
modelHandler = chimera.triggers.addHandler( u'Model', models_changed, None)


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


class DecoderDialog(ModelessDialog):    
    name = "decoder dialog"

    buttons = ("Apply", "Close")

    title = "Set Ambisonics Decoder"

    def fillInUI(self, parent):

        global decoder

        decoder = Tkinter.StringVar(parent)
        decoder.set(decoders[3])

        decoderLabel = Tkinter.Label(parent, text='Ambisonic Decoder')
        decoderLabel.grid(column=0, row=0)
        
        # Create the menu button and the option menu that it brings up.
        decoderButton = Tkinter.Menubutton(parent, indicatoron=1,
                                        textvariable=decoder, width=16,
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
                                        textvariable=mapping, width=16,
                                        relief=Tkinter.RAISED, borderwidth=2)
        mappingButton.grid(column=1, row=1)
        mappingMenu = Tkinter.Menu(mappingButton, tearoff=0)
        
        #    Add radio buttons for all possible choices to the menu.
        for mapname in mappings.keys():
            mappingMenu.add_radiobutton(label=mapname, variable=mapping, value=mapname)
            
        #    Assigns the option menu to the menu button.
        mappingButton['menu'] = mappingMenu

    def Apply(self):
        set_decoder(decoder.get())
        set_mapping(mappings[mapping.get()])

if(chimera.dialogs.find(DecoderDialog.name) == None):
    chimera.dialogs.register(DecoderDialog.name, DecoderDialog)
else:
    chimera.dialogs.reregister(DecoderDialog.name, DecoderDialog)

chimera.dialogs.display(DecoderDialog.name)
