import guitarpro
import guitarpro.gp5
import mido
from mido import Message as m

from functools import partial
import os
import math

import tkinter as tk
from tkinter import filedialog, ttk

import LookupTables

#-------------------------------------------------------------

window = tk.Tk()

window.geometry('550x400')
window.resizable(width=False, height=False)

window.title('Keyswitch Generator')
window.iconbitmap("KeyswitchGenerator/Icon.ico")
#-------------------------------------------------------------
#----------------------- PRESETS -----------------------------
#-------------------------------------------------------------

DefaultPresets = {
'Empty':'''String 8:0:X
String 7:0:X
String 6:0:X
String 5:0:X
String 4:0:X
String 3:0:X
String 2:0:X
String 1:0:X
sustain:0:X
palm mute:0:X
dead note:0:X
tap:0:X
slap:0:X
pop:0:X
nat. harm.:0:X
art. harm.:0:X
Hammer-On:0:X
Pull-Off:0:X''',

'Eurobass 3':'''String 8:0:X
String 7:0:X
String 6:0:X
String 5:103:G8
String 4:102:F#8
String 3:101:F8
String 2:100:E8
String 1:99:D#8
Sustain:24:C2
Palm mute:17:F1
Dead note:27:D#2
Tap:34:A#2
Slap:28:E2
Pop:30:F#2
Nat. Harm.:32:G#2
Art. Harm.:0:X
Hammer-On:33:A2
Pull-Off:33:A2
''',

'Ample TR6':'''String 8:0:X
String 7:0:X
String 6:0:X
String 5:12:C1
String 4:13:C#1
String 3:14:D1
String 2:15:D#1
String 1:16:E1
Sustain:24:C2
Palm mute:26:D2
Dead note:0:X
Tap:32:G#2
Slap:30:F#2
Pop:31:G2
Nat. Harm.:25:C#2
Art. Harm.:0:X
Hammer-On:0:X
Pull-Off:0:X
''',


}



#-------------------------------------------------------------
#-------------------------------------------------------------


ErrorFlags = {
    1 : True,
    2 : True,
}

usedData = {
    'UsedPathGP' : '',
    'UsedTrackGP' : 0,
    'UsedTrackNameGP' : '',
    'Transpose' : 0,
}

keyswitches = {
    'String 8' : (0, 'X', tk.Label()),
    'String 7' : (0, 'X', tk.Label()),
    
    'String 6' : (0, 'X', tk.Label()),
    'String 5' : (0, 'X', tk.Label()),
    'String 4' : (0, 'X', tk.Label()),
    'String 3' : (0, 'X', tk.Label()),
    'String 2' : (0, 'X', tk.Label()),
    'String 1' : (0, 'X', tk.Label()),
    
    'Sustain' : (0, 'X', tk.Label()),
    'Palm mute' : (0, 'X', tk.Label()),
    'Dead note' : (0, 'X', tk.Label()),
    'Tap' : (0, 'X', tk.Label()),
    'Slap' : (0, 'X', tk.Label()),
    'Pop' : (0, 'X', tk.Label()),
    
    'Nat. Harm.' : (0, 'X', tk.Label()),
    'Art. Harm.' : (0, 'X', tk.Label()),
    
    'Hammer-On' : (0, 'X', tk.Label()),
    'Pull-Off' : (0, 'X', tk.Label()),
}



#-------------------------------------------------------------

def openFilePicker():
    filepath = filedialog.askopenfilename(defaultextension='.gp5', filetypes=[('Guitar Pro 5', '.gp5'), ('All Files', '*.*')])
    if filepath:
        ErrorFlags[2] = False
        
        filename = filepath.split('/')[-1]
        
        if filename.endswith('.gp5') or filename.endswith('.gp4'):
            gpfile_picker['text'] = filename
            gperror['text'] = ''
            usedData["UsedPathGP"] = filepath
            ErrorFlags[1] = False
            
            file = guitarpro.parse(filepath)
            newoptions = []
            
            for track in file.tracks:
                newoptions.append(track.name)
            
            selectTrack_dropdown['values'] = newoptions

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
        Notename = dropdown.get()
        midiValue = LookupTables.midi_lookup[Notename]
        
        keyswitches[keyswitch_id] = (midiValue, Notename, keyswitches[keyswitch_id][2])
        keyswitches[keyswitch_id][2].config(text=(Notename + ' :'))
        
        popup.destroy()
        
    
    popup = tk.Toplevel(window)
    popup.title(keyswitch_id)
    popup.geometry('200x200')
    
    label = tk.Label(popup, text='Enter Note:')
    label.pack(pady=5)
    
    dropdown = ttk.Combobox(popup, values=LookupTables.midi_keys, width=5, state="readonly")
    dropdown.pack(pady=5)
    
    button = tk.Button(popup, text="Cancel", command=popup.destroy)
    button.pack(pady=5)
    
    button = tk.Button(popup, text="Accept", command=setNote)
    button.pack(pady=5)


#-------------------------------------------------------------

def estimate(ticks):
    if ticks % 10 >= 5:
        return math.ceil(ticks)
    else:
        return math.floor(ticks)


def getMidiFromTab(value : int, string : int, tuning : list[int] = [64, 59, 55, 50, 45, 40, 35, 30]) -> int:
    try:
        return tuning[string - 1] + value + int(Transpose.get())
    except ValueError:
        return tuning[string - 1] + value

def duration_to_ticks(duration):
    """Converts a Duration object to MIDI ticks."""
    ticks = (480 * 4) / duration.value
    if duration.isDotted:
        ticks *= 1.5
    if duration.tuplet:
        ticks *= duration.tuplet.times / duration.tuplet.enters
    return estimate(ticks)

def GenMidi():
    for ErrorFlag in ErrorFlags:
        if ErrorFlags[ErrorFlag] == True:
            gperror.config(text='Please Select a .gp5')
            return
    progresslabel.config(text='Reading File...')
    Gpfile = guitarpro.parse(usedData["UsedPathGP"])
    newmidi = mido.MidiFile()
            
    newtrack = mido.MidiTrack()
    newmidi.tracks.append(newtrack)
            
    TicksPerBeat = 480
    Tune = 0
            
    newtrack.append(mido.MetaMessage('time_signature'))
            
    BeatStartTime = 0
    BeatEndTime = 0
            
    currentTimeSig = (4, 4)
    track = Gpfile.tracks[usedData["UsedTrackGP"]]
    Tune = []
    
    nextbeat = None
    nextMeasure = None
    isAtEnd = False
    lastbeatlen = 0
    
    for string in track.strings:
        Tune.append(string.value)
    
    for m_i, measure in enumerate(track.measures):
        
        try:
            nextMeasure = track.measures[m_i + 1]
        except IndexError:
            isAtEnd = True
        for voice in measure.voices:
            for b_i, beat in enumerate(voice.beats):
                if beat.status == guitarpro.BeatStatus.empty:
                    continue
                BeatTickLen = duration_to_ticks(beat.duration)
                tiesInNextBeat = []
                NoEffect = True
                String = 0
                
                try:
                    nextbeat = voice.beats[b_i + 1]
                    for note in nextbeat.notes:
                        if note.type == guitarpro.NoteType.tie:
                            tiesInNextBeat.append(note)
                except IndexError:
                    if isAtEnd == False and nextMeasure != None:
                        for v in nextMeasure.voices:
                            for b in v.beats:
                                for note in b.notes:
                                    if note.type == guitarpro.NoteType.tie:
                                        tiesInNextBeat.append(note)
                
                if beat.status == guitarpro.BeatStatus.rest or beat.notes == []:
                    BeatStartTime += BeatTickLen
                else:
                    for note in beat.notes: #note_on loop
                        String = note.string
                            
                        if note.type == guitarpro.NoteType.normal:
                            noteMidi = getMidiFromTab(note.value, note.string, Tune)
                            newtrack.append(m('note_on', note=noteMidi, velocity=note.velocity, time=BeatStartTime))
                            BeatStartTime = 0
                            
                            if note.effect.palmMute == True and keyswitches['Palm mute'][1] != 'X' and NoEffect:
                                newtrack.append(m('note_on', note=keyswitches['Palm mute'][0], velocity=95, time=BeatStartTime))
                                NoEffect = False
                                
                                
                            elif beat.effect.slapEffect.value == 1:
                                newtrack.append(m('note_on', note=keyswitches['Tap'][0], velocity=95, time=BeatStartTime))
                                NoEffect = False
                            elif beat.effect.slapEffect.value == 2:
                                newtrack.append(m('note_on', note=keyswitches['Slap'][0], velocity=95, time=BeatStartTime))
                                NoEffect = False
                            elif beat.effect.slapEffect.value == 3:
                                newtrack.append(m('note_on', note=keyswitches['Pop'][0], velocity=95, time=BeatStartTime))
                                NoEffect = False
                        
                        elif note.type == guitarpro.NoteType.dead:
                            noteMidi = getMidiFromTab(note.value, note.string, Tune)
                            newtrack.append(m('note_on', note=noteMidi, velocity=note.velocity, time=BeatStartTime))
                            
                            if keyswitches["Dead note"][1] != 'X' and NoEffect:
                                newtrack.append(m('note_on', note=keyswitches["Dead note"][0], velocity=95, time=BeatStartTime))
                                NoEffect = False
                            BeatStartTime = 0
                        
                        
                        if note.effect.staccato == True:
                            newnote = beat.notes.pop(beat.notes.index(note))
                            beat.notes.insert(newnote, 0)
                    
                    if keyswitches["Sustain"][1] != 'X' and NoEffect:
                                newtrack.append(m('note_on', note=keyswitches["Sustain"][0], velocity=95, time=BeatStartTime))
                    
                    if len(beat.notes) == 1:
                        newtrack.append(m('note_on', note=keyswitches[LookupTables.strings[String]][0], velocity=95, time=BeatStartTime))
                    
                    BeatEndTime = BeatTickLen
                    NoEffect = True
                    
                    
                    for note in beat.notes: #note_off loop
                        noteMidi = getMidiFromTab(note.value, note.string, Tune)
                        ignoreNote = False
                        
                        if not isAtEnd:
                            for tiedNote in tiesInNextBeat:

                                if tiedNote.string == note.string:
                                    ignoreNote = True
                        
                        
                            if note.type == guitarpro.NoteType.normal or note.type == guitarpro.NoteType.tie:
                                if note.effect.staccato == True:
                                    newtrack.append(m('note_off', note=noteMidi, velocity=note.velocity, time=estimate(BeatEndTime / 2.0)))
                                    BeatStartTime += int(BeatEndTime / 2.0)
                                else:
                                    newtrack.append(m('note_off', note=noteMidi, velocity=note.velocity, time=BeatEndTime))
                                BeatEndTime = 0
                                
                                if note.effect.palmMute == True and keyswitches['Palm mute'][1] != 'X' and NoEffect:
                                    newtrack.append(m('note_off', note=keyswitches['Palm mute'][0], velocity=95, time=BeatEndTime))
                                    NoEffect = False
                                    
                                    
                                elif beat.effect.slapEffect.value == 1:
                                    newtrack.append(m('note_off', note=keyswitches['Tap'][0], velocity=95, time=BeatEndTime))
                                    NoEffect = False
                                elif beat.effect.slapEffect.value == 2:
                                    newtrack.append(m('note_off', note=keyswitches['Slap'][0], velocity=95, time=BeatEndTime))
                                    NoEffect = False
                                elif beat.effect.slapEffect.value == 3:
                                    newtrack.append(m('note_off', note=keyswitches['Pop'][0], velocity=95, time=BeatEndTime))
                                    NoEffect = False
                            #---------------------------------------------------------------------------------------------------------
                            elif note.type == guitarpro.NoteType.dead:
                                newtrack.append(m('note_off', note=noteMidi, velocity=note.velocity, time=BeatEndTime))
                                BeatEndTime = 0
                                
                                if keyswitches["Dead note"][1] != 'X' and NoEffect:
                                    newtrack.append(m('note_off', note=keyswitches["Dead note"][0], velocity=95, time=BeatEndTime))
                                    NoEffect = False
                    if keyswitches["Sustain"][1] != 'X' and NoEffect:
                        newtrack.append(m('note_off', note=keyswitches["Sustain"][0], velocity=95, time=BeatEndTime))
                    
                    if len(beat.notes) == 1:
                        newtrack.append(m('note_off', note=keyswitches[LookupTables.strings[String]][0], velocity=95, time=BeatEndTime))             
                lastbeatlen = BeatTickLen
                
    progresslabel.config(text='Midi Generated!')
            
    newfilepath = filedialog.asksaveasfilename(defaultextension='.mid', filetypes=[('Midi File', '.mid')])
    newmidi.save(newfilepath)

#-------------------------------------------------------------

gplabel = tk.Label(window, text='Guitar Pro File:')
gplabel.place(x=10, y=50)
tracklabel = tk.Label(window, text='Track Select:')
tracklabel.place(x=10, y=100)

voidstuff = tk.Label(window, text='Developed By ArtificialVoid1')
voidstuff.place(x=10, y=0)

progresslabel = tk.Label(window, text='', foreground='green')
progresslabel.place(x=450, y=50)

gperror = tk.Label(window, text='')
gperror.config(foreground='dark red')
gperror.place(x=10, y=75)

gpfile_picker = tk.Button(window, text='Choose File', command=openFilePicker)
gpfile_picker.place(x=100, y=48)

def selectTrack(_):
    selected = selectTrack_dropdown.get()
    if selected != '---':
        usedData["UsedTrackGP"] = selectTrack_dropdown["values"].index(selected)
        
tracks = ['---']

selectTrack_dropdown = ttk.Combobox(window, values=tracks, width=20, state="readonly")
selectTrack_dropdown.bind("<<ComboboxSelected>>", selectTrack)
selectTrack_dropdown.place(x=100, y=120)

xLevel = 300
minusIndicies = 0
for index, keyswitch in enumerate(keyswitches):
    
    if index == keyswitches.__len__() / 2:
        xLevel += 150
        minusIndicies = index
    
    keyswitch_btn = tk.Button(window, text=keyswitch, command=partial(SetKeyswitchOption, keyswitch))
    keyswitch_btn.place(x=xLevel, y=48 + (30 * ((index - minusIndicies) + 1)))
    
    key_label = tk.Label(window, text='None :')
    key_label.place(x=xLevel - 50, y=50 + (30 * ((index - minusIndicies) + 1)))
    keyswitches[keyswitch] = (0, 'X', key_label)


savepresetbtn = tk.Button(window, text='Save Preset', command=SavePresetButton)
savepresetbtn.place(x=200, y=10)

presets = ['Open preset']
default_presets_folder = "Presets/"



if not os.path.exists(default_presets_folder):
    os.makedirs(default_presets_folder)

    for d_preset_name in DefaultPresets:
        with open(default_presets_folder + d_preset_name + '.ks', 'w') as file:
            file.write(DefaultPresets[d_preset_name])



def loadpreset(filepath):
    with open(filepath, 'r') as file:
        fileLines = file.read().split('\n')
        for line in fileLines:
            lineparts = line.split(':')
            keyswitches[lineparts[0]] = (int(lineparts[1]), lineparts[2], keyswitches[lineparts[0]][2])
            if lineparts[2] == 'X':
                keyswitches[lineparts[0]][2].config(text='None :')
            else:
                keyswitches[lineparts[0]][2].config(text=lineparts[2] + ' :')



def openPreset(_):
    selected = preset_dropdown.get()
    
    if selected == 'Import Preset':
        filepath = filedialog.askopenfilename(defaultextension='.ks', filetypes=[('Preset File', '.ks')]) #initialdir=default_presets_folder
        loadpreset(filepath=filepath)
    else:
        filepath = default_presets_folder + selected + '.ks'
        loadpreset(filepath=filepath)

preset_options = ['Import Preset']

for filename in os.listdir(default_presets_folder):
    preset_options.append(filename.removesuffix('.ks'))

preset_dropdown = ttk.Combobox(window, values=preset_options, width=10, state="readonly")
preset_dropdown.bind("<<ComboboxSelected>>", openPreset)
preset_dropdown.place(x=300, y=7)

def validateNumber(char):
    return char.isdigit()
validation = window.register(validateNumber)

Transpose = tk.StringVar()

TransposeBox = tk.Entry(window, validate='all', validatecommand=(validation, '%S'), textvariable=Transpose, width=10)
TransposeBox.place(x=40, y=200)
TransposeText = tk.Label(text='Tanspose:')
TransposeText.place(x=40, y=175)

createMidi = tk.Button(window, text='Generate Midi', command=GenMidi)
createMidi.place(x=450, y=10)

#-------------------------------------------------------------
window.mainloop()
