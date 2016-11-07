# -*- coding: utf-8 -*-
#
# Copyright 2016 Holger Ballweg
#
# This file is part of chison.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from osc import *

from utils import *

# sound object management
"""
Abstract sound objects, the sound server (e.g., SuperCollider) decides what to do with them

Add new object with id and sound type:
/obj/new id sound_type [attribute_name attribute_value]*

Modify existing object by id:
/obj/modify id [attribute_name attribute_value]*

Delete object by id:
/obj/delete id

Reset everything (delete all sound objects and samples):
/reset

Load sample at path to this id:
/sample/new id path

Switch HRTF decoder:
/decoder/set name

Set global volume between 0 and 1.0:
/volume/set volume
"""

# count up ids used to sync between python and sound server
id = 0

sound_objs = dict()

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
        obj = dict(id=oid, type=type)
        for i in range(0, len(args), 2):
            attr = args[i]
            val = args[i+1]
            obj = assoc(obj, attr, val)
        if(oid != -1):
            sound_objs[oid] = obj
        send_osc("/obj/new", oid, type, *args)
        return obj

def modify_sound_object(obj, *args):
        if(obj['id'] != -1):
                send_osc("/obj/modify", obj['id'], *args)
                for i in range(0, len(args), 2):
                    attr = args[i]
                    val = args[i+1]
                    obj = assoc(obj, attr, val)
                sound_objs[obj['id']] = obj
        return obj

def delete_sound_object(obj):
        if(obj['id'] != -1):
                send_osc("/obj/delete", obj['id'])
                sound_objs.pop(obj['id'])
        return True

def position_sound_object(obj, dist, az, ele):
        obj = modify_sound_object(obj, "dist", dist, "az", az, "ele", ele)
        return obj

def reset_sound_objects():
    global sound_objs
    sound_objs = dict()
    send_osc("/reset")

def set_decoder(name):
    print("setting decoder to " + name)
    send_osc("/decoder/set", name)

def set_volume(volume):
    send_osc("/volume/set", volume)


import itertools

def obj_refresh_callback(path, tags, args, source):
    type = args[0]
    print("Triggered reload of sound objects of type " + type)
    for id, obj in sound_objs.iteritems():
            if(obj['type'] == type):
                    args = list(itertools.chain.from_iterable(obj.iteritems()))
                    sound_objs[id] = make_sound_object(id, type, *args)

server.addMsgHandler( "/obj/refresh",  obj_refresh_callback)

