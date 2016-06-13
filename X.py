# -*- coding: utf-8 -*-
import chimera
import simpleOSC

import math
halfpi = (0.5 * math.pi)

simpleOSC.initOSCClient(port=57120)

try:
        chimera.triggers.deleteHandler(u'Model', modelHandler)
        chimera.triggers.deleteHandler(u'Viewer', viewerHandler)
except:
        pass

def angle2d(p1, p2):
        return halfpi - math.atan2(p1.y - p2.y, p1.x - p2.x)

def elevation(eye, point):
        return angle2d(chimera.Point(eye.y, eye.z,0),
                       chimera.Point(point.y,point.z,0))

def azimuth(eye, point):
        return angle2d(chimera.Point(eye.x, eye.z,0),
                       chimera.Point(point.x,point.z,0))


def viewer_changed(trigger, additional, atomChanges):
        om = chimera.openModels
        lensView = chimera.viewer
        camera = lensView.camera
        realEye = chimera.Point(*camera.center)
        realEye[2] = camera.eyeZ()

        for model in om.list():
                for i,r in enumerate(model.residues):
                        coords = r.atoms[0].xformCoord()
                        # distance shouldn't become 0 for ambisonics
                        distance = max(0.01, realEye.distance(coords) - 24)
                        az = azimuth(realEye, coords)
                        ele = elevation(realEye, coords)
                        simpleOSC.sendOSCMsg("/atom", [model.id, i, distance, az, ele])
                        if(i == 0):
                                print(model.id, i, distance, az,ele)
                                


openModelIds = set()


def models_changed(trigger, additional, changes):
        
        global openModelIds
        for i in changes.modified:
                print("triggered modified", changes.modified, changes.reasons)
                simpleOSC.sendOSCMsg("/model/modified", [i.id] + list(changes.reasons))
        for i in changes.created:
                try:
                        print("triggered create", changes.created, changes.reasons)
                        simpleOSC.sendOSCMsg("/model/created", [i.id, len(i.residues)] + list(changes.reasons))
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
                simpleOSC.sendOSCMsg("/model/deleted",
                                     list(openModelIds.difference(newOpenModelIds)))
                openModelIds = newOpenModelIds                
        global g3
        
        g3 = [trigger, additional, changes]

viewerHandler = chimera.triggers.addHandler( u'Viewer',viewer_changed, None)
modelHandler = chimera.triggers.addHandler( u'Model', models_changed, None)
