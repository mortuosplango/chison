
# GUI
import chimera

import Tkinter

from chimera.baseDialog import ModelessDialog

import sound_objects
import chimera_utils

# last selected decoder
decoder = None  

# available decoders
decoders = [
    'KEMAR binaural 1',
    'KEMAR binaural 2',
    'UHJ stereo',
    'synthetic binaural',
]

default_volume = 0.5
volume = None

class DecoderDialog(ModelessDialog):    
    name = "decoder dialog"

    buttons = ("Apply", "Close")

    title = "Sonification settings"

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

        global volume

        volume = Tkinter.DoubleVar(parent)
        volume.set(default_volume)

        label = Tkinter.Label(parent, text='Volume')
        label.grid(column=0,row=2)

        scale = Tkinter.Scale(parent, from_=0, to=1.0, width=width,
                              resolution=0.01, orient=Tkinter.HORIZONTAL,
                              variable=volume, showvalue=0,
                              command=lambda self: sound_objects.set_volume(volume.get()))
        scale.grid(column=1, row=2)

    def Apply(self):
        sound_objects.set_decoder(decoder.get())

chimera_utils.redisplay(DecoderDialog)
