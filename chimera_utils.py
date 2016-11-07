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

# chimera -> sonification mapping
import chimera
import numpy as np

import spatialisation as sp
import sound_objects as so

import functools as ft

import datetime

def get_coords(obj):
        if hasattr(obj, 'atoms'):
                return obj.atoms[0].xformCoord()
        else:
                return obj.xformCoord()

def ch_get_real_eye():
        viewer = chimera.viewer
        camera = viewer.camera
        real_eye = chimera.Point(*camera.center)
        real_eye[2] = camera.eyeZ()
        return real_eye


ch_calculate_position = ft.partial(sp.calculate_position, distance_offset=(-24))

def ch_position_sound_object(sobj, real_eye, coords):
        dist, az, ele = ch_calculate_position(real_eye, coords)
        return so.position_sound_object(sobj, dist, az, ele)



def is_ligand(molecule):
    try:
        molecule.dockGridScore
        return True
    except AttributeError:
        return False


def save_orig_color():
        for molecule in chimera.openModels.list(modelTypes=[chimera.Molecule]):
                for a in molecule.atoms:
                        a.origColor = a.color
                if hasattr(molecule, 'residues'):
                        for r in molecule.residues:
                                r.origColor = r.ribbonColor


def set_color(obj, color):
        if hasattr(obj, 'ribbonColor'):
                if not hasattr(obj, 'origColor'):
                        obj.origColor = obj.ribbonColor
                obj.ribbonColor = color
                for a in obj.atoms:
                        if a.display:
                                set_color(a, color)
        elif hasattr(obj, 'color'):
                if not hasattr(obj, 'origColor'):
                        obj.origColor = obj.color
                obj.color = color


def restore_color(obj):
        if hasattr(obj, 'ribbonColor'):
                obj.ribbonColor = obj.origColor
                for a in obj.atoms:
                        if a.display:
                                restore_color(a)
        elif hasattr(obj, 'color'):
                obj.color = obj.origColor
        else:
                print("couldn't restore", obj)



def get_neighbors(obj):
        if hasattr(obj, 'bondedResidues'):
           return obj.bondedResidues()
        else:
           return obj.primaryNeighbors()



def redisplay(dialog):
        if(chimera.dialogs.find(dialog.name) == None):
            chimera.dialogs.register(dialog.name, dialog)
        else:
            chimera.dialogs.find(dialog.name).destroy()
            chimera.dialogs.reregister(dialog.name, dialog)

        chimera.dialogs.display(dialog.name)
