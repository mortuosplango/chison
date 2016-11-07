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

def m_earcons(models, objects):
        # cutoff for betafactors
        cutoff = 60.0

        # init mapping
        if(len(objects) == 0):
                objects["sample"] = load_sample(None, basepath + "/samples/creak.wav")
                for model in models.list(modelTypes=[chimera.Molecule]):
                        for i,atom in enumerate(model.atoms):
                                if(atom.bfactor > cutoff):
                                        sobj = make_sound_object(None, "sample",
                                                                 "freq", 440 + ((atom.bfactor - cutoff) * 10),
                                                                 "sample", objects["sample"]["id"]
                                                                 )
                                        sobj['ch_model_id'] = model.id
                                        sobj['ch_atom'] = i
                                        objects[sobj['id']] = sobj
        # update positions
        real_eye = ch_get_real_eye()
        
        for key, sobj in objects.iteritems():
            if(key != "sample"):
                obj = chimera.openModels.list(id=sobj['ch_model_id'])[0].atoms[
                    sobj['ch_atom']]
                coords = obj.xformCoord()
                dist, az, ele = ch_calculate_position(real_eye, coords)
                sobj = modify_sound_object(sobj,
                                           "sample", objects["sample"]["id"],
                                           "amp", np.interp(dist, [0,500], [0.8,0.01]))
                objects[key] = position_sound_object(sobj, dist, az, ele)
        return objects

