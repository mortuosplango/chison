import chimera
from chimera import selection, Molecule
from chimera.baseDialog import ModelessDialog
import Tkinter, Pmw

import prefs
reload(prefs)

import ShowAttr
#from ShowAttr import *

from prefs import prefs, TARGET, \
	ATTRS_ATOMS, ATTRS_RESIDUES, ATTRS_MOLECULES, ATTRS_SEGREGIONS, \
	COLORS, COLOR_ATOMS, COLOR_RIBBONS, COLOR_SURFACES, SCALING,\
	ATOM_STYLE, ATOM_RADII, NOVAL_RADIUS, WORM_RADII, NOVAL_WORM, \
	WORM_STYLE, RESTRICT, NOVAL_PITCH, PITCH_RANGE

import interaction
reload(interaction)

import chimera_utils
reload(chimera_utils)

import sonification_settings
reload(sonification_settings)

import sound_objects as so

def GUI_grain(obj, dist, az, ele, level, maxLevel):
    if("gvalue" in dir(obj)):
        return so.make_sound_object(None, obj.gtype, "midinote", obj.gvalue,
                                 "dist", dist, "az", az, "ele", ele,
                                 "amp", (1.0 - (float(level)/maxLevel)) * 0.5 )
    else:
        return None


class SonifyAttrDialog(ShowAttr.ShowAttrDialog):
	title = "Sonify by Attribute"
	buttons = ('OK', 'Apply', 'Close')
	provideStatus = True
	name = "sonify attrs"


	def fillInUI(self, parent):

		super(SonifyAttrDialog, self).fillInUI(parent)

		#self.modeNotebook = Pmw.NoteBook(parent,raisecommand=self._pageChangeCB,tabpos=None)

                # Pitch Markers
		self.renderPitchMarkers = self.renderHistogram.addmarkers(
			newcolor='pink', activate=False, coordtype='relative')
		if len(prefs[PITCH_RANGE]) == 1:
			self.renderPitchMarkers.append(((0.5, 0.0), None))
		else:
			self.renderPitchMarkers.extend(map(lambda e: ((e[0] /
				float(len(prefs[PITCH_RANGE]) - 1), 0.0),
				None), enumerate(prefs[PITCH_RANGE])))
		for i, rad in enumerate(prefs[PITCH_RANGE]):
			self.renderPitchMarkers[i].radius = rad


		
		#self.renderNotebook = Pmw.NoteBook(renderFrame, tabpos=None)
		
		self.renderNotebook.add("Pitch")


		# Pitch tab
		f = self.renderNotebook.page("Pitch")
		self.pitchWarning = Tkinter.Label(f, text=
			"pitch can only be used with\n"
			"atom, residue or molecule attributes.")
		self.pitchWarning.grid() # for later setnaturalsize

		self.pitchFrame = Tkinter.Frame(f)
		from chimera.tkoptions import EnumOption, BooleanOption, FloatOption
		
		class SonificationOption(FloatOption):
			min = 0.001
		class WormStyleOption(EnumOption):
			values = ["smooth", "segmented", self.dewormLabel]
		self.doNoValuePitch = BooleanOption(self.pitchFrame, 1,
			"Play no-value residues", False, None, balloon=
			"Play something for residues not having\n"
			"this attribute or leave them silent")
		self.noValuePitch = SonificationOption(self.pitchFrame, 2,
			"No-value pitch", prefs[NOVAL_PITCH], None,
			balloon="Residues without this attribute will\n"
			"be given this pitch")
		
		self.renderNotebook.selectpage("Pitch")

		self.targetMenu.invoke(attrsPrefMap[prefs[TARGET]].menuName)
		


	def _applyPitch(self):
		markers, marker = self.renderHistogram.currentmarkerinfo()
		if marker is not None:
			self._setRadius(marker)
		noValRadius = self.noValueRadii.get()
		doNoVal = self.doNoValueRadii.get()
		prefs[ATOM_RADII] = map(lambda m: m.radius,
						self.renderPitchMarkers[:])
		prefs[ATOM_STYLE] = self.atomStyle.get()

		target = revAttrsLabelMap[self.targetMenu.getvalue()]

		self.status("Setting atomic radii", blankAfter=0)

		restrict = prefs[RESTRICT]
		if restrict:
			curSel = selection.currentAtoms(asDict=True)
			if not curSel:
				restrict = False
		if restrict:
			restrict = curSel
		from operator import add
		style = prefs[ATOM_STYLE]
		attrMenu = self.renderAttrsMenu[target]
		if restrict:
			items = target.objectsInModels(target.selectedObjects(),
										self.models)
		else:
			items = target.modelObjects(self.models)
		attrName = attrMenu.getvalue()
		if len(attrName) == 1:
			doSubitems = False
		else:
			doSubitems = True
		attrName = attrName[-1]
		radMarkers = self.renderPitchMarkers
		radMarkers['coordtype'] = 'absolute'
		for item in items:
			if doSubitems:
				# an average/sum
				vals = []
				for sub in target.childObjects(item):
					try:
						val = getattr(sub, attrName)
					except AttributeError:
						continue
					if val is not None:
						vals.append(val)
				if vals:
					val = reduce(add, vals)
					if not summableAttrName(attrName):
						val /= float(len(vals))
				else:
					val = None
			else:
				try:
					val = getattr(item, attrName)
				except AttributeError:
					val = None

			if val is None:
				if doNoVal:
					target.setRadius(item, noValRadius,
							 style, restrict)
				continue
			if len(radMarkers) == 0:
				continue
			for i, marker in enumerate(radMarkers):
				if val <= self._markerVal(marker):
					break
			else:
				i = len(radMarkers)
			if i == 0:
				rad = radMarkers[0].radius
			elif i == len(radMarkers):
				rad = radMarkers[-1].radius
			elif len(radMarkers) > 1:
				left, right = map(self._markerVal,
						radMarkers[i-1:i+1])
				if right == left:
					pos = 0.5
				else:
					pos = (val - left) / float(right - left)
				rad = radMarkers[i-1].radius * (1 -
					pos) + radMarkers[i].radius * pos
			else:
				rad = radMarkers[0].radius
			#target.setRadius(item, rad, style, restrict)
			
			item.sobj = None
			item.gtype = "bfactor2Grain"
			item.gvalue = rad
			
		interaction.set_grain_maker_fn(GUI_grain)
		interaction.grains = True
		radMarkers['coordtype'] = 'relative'
		self.status("Done setting pitch")

	def _raisePageCB(self, page):
		if page != "Pitch":
			super(SonifyAttrDialog, self)._raisePageCB(page)
		else:
 			entryFrame = self.renderHistogram.component('widgetframe')
 			markers = self.renderPitchMarkers
 			self.radiusEntry.component('label').configure(
						text='Pitch')
 			self.renderHistogram.configure(colorwell=False)
 			self.radiusEntry.grid(row=1, column=self.entryColumn)
 			entryFrame.columnconfigure(self.entryColumn, weight=2)
 			self.renderHistogram.activate(markers)
 			self._renderGUI()

	def _renderGUI(self):
		target = revAttrsLabelMap[self.targetMenu.getvalue()]
		page = self.renderNotebook.getcurselection()
		if page == "Worms":
			if hasattr(target, 'setWormRadius'):
				self.wormsWarning.grid_forget()
				self.wormsFrame.grid()
				self._renderOkApply = True
			else:
				self.wormsFrame.grid_forget()
				self.wormsWarning.grid()
				self._renderOkApply = False
		elif page == "Radii":
			if hasattr(target, 'setRadius'):
				self.radiiWarning.grid_forget()
				self.radiiFrame.grid()
				self._renderOkApply = True
			else:
				self.radiiFrame.grid_forget()
				self.radiiWarning.grid()
				self._renderOkApply = False
		elif page == "Pitch":
			if hasattr(target, 'setRadius'):
				self.pitchWarning.grid_forget()
				self.pitchFrame.grid()
				self._renderOkApply = True
			else:
				self.pitchFrame.grid_forget()
				self.pitchWarning.grid()
				self._renderOkApply = False
		else:
			self._renderOkApply = True
		self.renderNotebook.setnaturalsize()
		state = 'normal' if self._attrOkApply[self.modeNotebook.getcurselection()] and self._renderOkApply else 'disabled'
		self.buttonWidgets['OK'].configure(state=state)
		self.buttonWidgets['Apply'].configure(state=state)
		self.colorKeyButton.configure(state=state)
		self.reverseColorsButton.configure(state=state)
		self.paletteMenu.component('menubutton').config(state=state)


chimera_utils.redisplay(SonifyAttrDialog)
