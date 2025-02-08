import guitarpro
import mido

from functools import partial
import os

import tkinter as tk
from tkinter import filedialog

#-------------------------------------------------------------

window = tk.Tk()

window.geometry('500x700')
window.resizable(width=False, height=False)

window.title('Keyswitch Generator')
window.iconbitmap("KeyswitchGenerator\Icon.ico")
#-------------------------------------------------------------
#----------------------- PRESETS -----------------------------
#-------------------------------------------------------------

DefaultPresets = {
    'default' : {
        'string 8': (0, "X"),
        'string 7': (0, "X"),
        'string 6': (0, "X"),
        'string 5': (0, "C0"),
        'string 4': (0, "X"),
        'string 3': (0, "X"),
        'string 2': (0, "X"),
        'string 1': (0, "X"),
        'sustain': (0, "X"),
        'palm mute': (0, "X"),
        'dead note': (0, "X"),
        'tap': (0, "X"),
        'slap': (0, "X"),
        'pop': (0, "X"),
        'nat. harm.': (0, "X"),
        'art. harm.': (0, "X")
    }
}



#-------------------------------------------------------------
#-------------------------------------------------------------

midi_lookup = {
    "C0": 0,
    "C#0": 1,
    "D0": 2,
    "D#0": 3,
    "E0": 4,
    "F0": 5,
    "F#0": 6,
    "G0": 7,
    "G#0": 8,
    "A0": 9,
    "A#0": 10,
    "B0": 11,
    "C1": 12,
    "C#1": 13,
    "D1": 14,
    "D#1": 15,
    "E1": 16,
    "F1": 17,
    "F#1": 18,
    "G1": 19,
    "G#1": 20,
    "A1": 21,
    "A#1": 22,
    "B1": 23,
    "C2": 24,
    "C#2": 25,
    "D2": 26,
    "D#2": 27,
    "E2": 28,
    "F2": 29,
    "F#2": 30,
    "G2": 31,
    "G#2": 32,
    "A2": 33,
    "A#2": 34,
    "B2": 35,
    "C3": 36,
    "C#3": 37,
    "D3": 38,
    "D#3": 39,
    "E3": 40,
    "F3": 41,
    "F#3": 42,
    "G3": 43,
    "G#3": 44,
    "A3": 45,
    "A#3": 46,
    "B3": 47
}

Note_options = ["C0", "C#0", "D0", "D#0", "E0", "F0", "F#0", "G0", "G#0", "A0", "A#0", "B0", "C1", "C#1", "D1", "D#1", "E1", "F1", "F#1", "G1", "G#1", "A1", "A#1", "B1", "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2", "C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", "A3", "A#3", "B3"]

ErrorFlags = {
    1 : True,
    2 : True,
}

usedFilepath : str = ''

keyswitches = {
    'String 8 (F#)' : (0, 'X', tk.Label()),
    'String 7 (B)' : (0, 'X', tk.Label()),
    
    'String 6 (E)' : (0, 'X', tk.Label()),
    'String 5 (A)' : (0, 'X', tk.Label()),
    'String 4 (D)' : (0, 'X', tk.Label()),
    'String 3 (G)' : (0, 'X', tk.Label()),
    'String 2 (b)' : (0, 'X', tk.Label()),
    'String 1 (e)' : (0, 'X', tk.Label()),
    
    'Sustain' : (0, 'X', tk.Label()),
    'Palm mute' : (0, 'X', tk.Label()),
    'Dead note' : (0, 'X', tk.Label()),
    'Tap' : (0, 'X', tk.Label()),
    'Slap' : (0, 'X', tk.Label()),
    'Pop' : (0, 'X', tk.Label()),
    
    'Nat. Harm.' : (0, 'X', tk.Label()),
    'Art. Harm.' : (0, 'X', tk.Label()),
}

#-------------------------------------------------------------

def openFilePicker():
    filepath = filedialog.askopenfilename()
    if filepath:
        ErrorFlags[2] = False
        
        filename = filepath.split('/')[-1]
        
        if filename.endswith('.gp5'):
            gpfile_picker['text'] = filename
            gperror['text'] = ''
            usedFilepath = filepath
            ErrorFlags[1] = False

        else:
            gperror['text'] = 'Please select a .gp5 file'
            ErrorFlags[1] = True

    else:
        gperror['text'] = 'File path does not exist!'
        ErrorFlags[2] = True

def SavePresetButton():
    filetypes = [('Keyswitch Preset', '.ks')]
    filepath = filedialog.asksaveasfilename(defaultextension='.ks', filetypes=filetypes, title='Save As')
    with open(filepath, 'w') as file:
        for keyswitch in keyswitches:
            file.write(keyswitch + ':' + str(keyswitches[keyswitch][0]) + ':' + keyswitches[keyswitch][1])
            file.write('\n')

#----------------------------------------------------------------------------------------

def SetKeyswitchOption(keyswitch_id : str):
    
    def setNote():
        Notename = clicked.get()
        midiValue = midi_lookup[Notename]
        
        keyswitches[keyswitch_id] = (midiValue, Notename, keyswitches[keyswitch_id][2])
        keyswitches[keyswitch_id][2].config(text=(Notename + ' :'))
        
        popup.destroy()
        
    
    popup = tk.Toplevel(window)
    popup.title(keyswitch_id)
    popup.geometry('200x200')
    
    label = tk.Label(popup, text='Enter Note:')
    label.pack(pady=5)
    
    clicked = tk.StringVar()
    clicked.set("C0")
    
    dropdown = tk.OptionMenu(popup, clicked, *Note_options)
    dropdown.pack(pady=5)
    
    button = tk.Button(popup, text="Cancel", command=popup.destroy)
    button.pack(pady=5)
    
    button = tk.Button(popup, text="Accept", command=setNote)
    button.pack(pady=5)


#-------------------------------------------------------------

def GenMidi():
    for ErrorFlag in ErrorFlags:
        if ErrorFlag == True:
            return
        else:
            
            pass


#-------------------------------------------------------------

gplabel = tk.Label(window, text='Guitar Pro File:')
gplabel.place(x=10, y=50)

gperror = tk.Label(window, text='')
gperror.config(foreground='dark red')
gperror.place(x=10, y=70)

gpfile_picker = tk.Button(window, text='Choose File', command=openFilePicker)
gpfile_picker.place(x=100, y=48)


for index, keyswitch in enumerate(keyswitches):
    
    keyswitch_btn = tk.Button(window, text=keyswitch, command=partial(SetKeyswitchOption, keyswitch))
    keyswitch_btn.place(x=300, y=18 + (30 * (index + 1)))
    
    key_label = tk.Label(window, text='None :')
    key_label.place(x=250, y=20 + (30 * (index + 1)))
    keyswitches[keyswitch] = (0, 'X', key_label)


savepresetbtn = tk.Button(window, text='Save Preset', command=SavePresetButton)
savepresetbtn.place(x=200, y=10)

presets = ['Open preset']
default_presets_folder = "C:/Users/%USERPROFILE%/Documents/VoidDsp/Keyswitch Presets/"



if not os.path.exists(default_presets_folder):
    os.makedirs(default_presets_folder)

    for d_preset_name in DefaultPresets:
        with open(default_presets_folder + d_preset_name + '.ks', 'w') as file:
            for property in DefaultPresets[d_preset_name]:
                file.write(property + ':' + str(DefaultPresets[d_preset_name][property][0]) + ':' + DefaultPresets[d_preset_name][property][1])
                file.write('\n')



def loadpreset(filepath):
    with open(filepath, 'r') as file:
        fileLines = file.read().split('\n')
        for line in fileLines:
            lineparts = line.split(':')
            keyswitches[lineparts[0]] = (int(lineparts[1], lineparts[2], keyswitches[lineparts[0]][2])
            if lineparts[2] == 'X':
                keyswitches[lineparts[0]][2].config(text='None :')
            else:
                keyswitches[lineparts[0]][2].config(text=lineparts[2] + ' :')

def openpreset(selected):
    if selected == 'Open preset':
        filepath = filedialog.askopenfilename(initialdir=default_presets_folder, defaultextension='.ks', filetypes=[('Preset File', '.ks')])
        loadpreset(filepath)
    else:
        loadpreset(default_presets_folder + selected + '.ks')

presetSelected = tk.StringVar()
presetSelected.set('Select Preset')
openPreset_dropdown = tk.OptionMenu(window, presetSelected, *presets, command=openpreset)
openPreset_dropdown.place(x=300, y=10)


createMidi = tk.Button(window, text='Generate', command=GenMidi)
createMidi.place(x=400, y=400)

#-------------------------------------------------------------
window.mainloop()
