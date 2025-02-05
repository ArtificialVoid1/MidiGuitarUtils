import guitarpro
import mido

from functools import partial

import tkinter as tk
from tkinter import filedialog

#-------------------------------------------------------------

window = tk.Tk()

window.geometry('500x700')
window.resizable(width=False, height=False)

window.title('Keyswitch Generator')
window.iconbitmap("KeyswitchGenerator\Icon.ico")

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
stack = []

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




createMidi = tk.Button(window, text='Generate', command=GenMidi)
createMidi.place(x=400, y=400)

#-------------------------------------------------------------
window.mainloop()