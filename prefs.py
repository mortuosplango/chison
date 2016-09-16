# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: prefs.py 30806 2010-06-26 01:02:29Z goddard $

import chimera
from chimera import preferences

ATTRS_MOLECULES = "molecules"
ATTRS_RESIDUES = "residues"
ATTRS_ATOMS = "atoms"
ATTRS_SEGREGIONS = "segmentation regions"

TARGET = "target"
LAST_ATTR = "last attr"
COLORS = "colors"
COLOR_ATOMS = "color atoms"
COLOR_RIBBONS = "color ribbons"
COLOR_SURFACES = "color surfaces"
ATOM_STYLE = "atom style"
ATOM_RADII = "atom radii"
NOVAL_RADIUS = "no value radius"
WORM_RADII = "worm radii"
NOVAL_WORM = "no value tube radius"
PITCH_RANGE = "pitch range"
SOUND_STYLE = "sound style"
NOVAL_PITCH = "no value pitch"
SCALING = "scaling"
WORM_STYLE = "worm style"
RESTRICT = "restrict OK/Apply"

options = {
	TARGET: ATTRS_ATOMS,
	LAST_ATTR: {
		ATTRS_MOLECULES: None, ATTRS_RESIDUES: None, ATTRS_ATOMS: None,
                ATTRS_SEGREGIONS: None
	},
	COLORS: ['blue', 'white', 'red'],
	COLOR_ATOMS: True,
	COLOR_RIBBONS: True,
	COLOR_SURFACES: True,
	ATOM_STYLE: chimera.Atom.Sphere,
	ATOM_RADII: [1.0, 4.0],
	NOVAL_RADIUS: 0.5,
	WORM_RADII: [0.25, 2.0],
	NOVAL_WORM: 0.1,
        PITCH_RANGE: [48.0, 72.0],
        NOVAL_PITCH: 60,
        SOUND_STYLE: "sine",
	SCALING: "log",
	WORM_STYLE: "smooth",
	RESTRICT: False
}
prefs = preferences.addCategory("ShowAttr", preferences.HiddenCategory,
							optDict=options)
