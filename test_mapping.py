

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
