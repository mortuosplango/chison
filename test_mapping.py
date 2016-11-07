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

def m_test(models, objects):
        # init mapping
        if(len(objects) == 0):
                for model in models.list(modelTypes=[chimera.Molecule]):
                        for i,r in enumerate(model.residues):
                                sobj = make_sound_object(None, "atom")
                                sobj['ch_model_id'] = model.id
                                sobj['ch_residue'] = i  
                                objects[sobj['id']] = sobj
        # update positions
        real_eye = ch_get_real_eye()
        
        for key, sobj in objects.iteritems():
                obj = chimera.openModels.list(id=sobj['ch_model_id'])[0].residues[
                    sobj['ch_residue']]
                coords = obj.atoms[0].xformCoord()
                objects[key] = ch_position_sound_object(sobj, real_eye, coords)
        return objects
