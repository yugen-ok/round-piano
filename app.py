from flask import Flask, render_template_string
import math

app = Flask(__name__)


@app.route('/')
def index():
    # Define the notes
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    # HTML template with JavaScript for the interactive visualization
    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Musical Octaves & Spiral</title>
        <style>
            body {
                background-color: #121212;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                font-family: 'Arial', sans-serif;
                color: #eee;
                overflow: hidden;
            }
            
            .frequency{
              position:absolute;
              color:#64ffda;
              font-size:12px;
              font-weight:bold;
              white-space:nowrap;
              pointer-events:none;
              opacity:0;
              transition:opacity .15s ease;
              /* centre horizontally, sit a little above the circle           */
              transform:translate(-50%,-250%);
            }
            
            .container {
                position: relative;
                width: 600px;
                height: 600px;
            }
            .note-circle {
                position: absolute;
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background-color: white;
                transform: translate(-50%, -50%);
                transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
                cursor: pointer;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .note-circle:hover {
                transform: translate(-50%, -50%) scale(1.2);
                box-shadow: 0 0 15px rgba(255, 255, 255, 0.8);
            }
            .note-circle.active {
                background-color: #64ffda;
                transform: translate(-50%, -50%) scale(1.3);
                box-shadow: 0 0 20px rgba(100, 255, 218, 0.8);
            }
            /* Style for notes that are in the selected scale */
            .note-circle.in-scale {
                background-color: #ff6464; /* Bright red color for scale notes */
                box-shadow: 0 0 15px rgba(255, 100, 100, 0.6);
            }
            .note-circle[data-octave="3"],
            .note-circle[data-octave="4"],
            .note-circle[data-octave="5"] {
                border: 1px solid transparent;
            }
            .active-octave {
                border-color: #64ffda !important;
            }
            .note-label {
                position: absolute;
                color: white;
                font-size: 14px;
                font-weight: bold;
                transform: translate(-50%, -50%);
                pointer-events: none;
            }
            .key-label {
                color: #000000;
                font-size: 10px;
                font-weight: bold;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                pointer-events: none;
                z-index: 10;
            }
            .status {
                position: absolute;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 14px;
                text-align: center;
            }
            /* New side panel styles */
            .control-panel {
                position: fixed;
                right: 0;
                top: 0;
                width: 270px;
                height: 100%;
                background-color: #1a1a1a;
                padding: 20px;
                box-shadow: -2px 0 10px rgba(0, 0, 0, 0.5);
                overflow-y: auto;
                z-index: 900;
            }
            .control-panel h3 {
                color: #64ffda;
                margin-top: 0;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px solid #333;
            }
            .control-group {
                margin-bottom: 20px;
            }
            .control-group label {
                display: block;
                margin-bottom: 8px;
                color: #bbb;
            }
            .control-group select,
            .control-group input[type="checkbox"] {
                width: 100%;
                padding: 8px;
                background-color: #2a2a2a;
                border: 1px solid #444;
                color: #eee;
                border-radius: 4px;
            }
            .control-group input[type="checkbox"] {
                width: auto;
                display: inline-block;
                margin-right: 8px;
            }
            .control-group select:focus {
                outline: none;
                border-color: #64ffda;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="status" id="status"></div>
        </div>

        <!-- Side control panel -->
        <div class="control-panel">
            <h3>Controls</h3>

            <div class="control-group">
                <label for="root-note">Root Note</label>
                <select id="root-note">
                    <option value="0">C</option>
                    <option value="1">C#</option>
                    <option value="2">D</option>
                    <option value="3">D#</option>
                    <option value="4">E</option>
                    <option value="5">F</option>
                    <option value="6">F#</option>
                    <option value="7">G</option>
                    <option value="8">G#</option>
                    <option value="9">A</option>
                    <option value="10">A#</option>
                    <option value="11">B</option>
                </select>
            </div>

            <div class="control-group">
                <label for="scale-pattern">Scale Pattern</label>
                <select id="scale-pattern">
                    <option value="major">Major [2,2,1,2,2,2,1]</option>
                    <option value="minor">Natural Minor [2,1,2,2,1,2,2]</option>
                    <option value="harmonicMinor">Harmonic Minor [2,1,2,2,1,3,1]</option>
                    <option value="melodicMinor">Melodic Minor [2,1,2,2,2,2,1]</option>
                    <option value="pentatonicMajor">Major Pentatonic [2,2,3,2,3]</option>
                    <option value="pentatonicMinor">Minor Pentatonic [3,2,2,3,2]</option>
                    <option value="blues">Blues [3,2,1,1,3,2]</option>
                    <option value="chromatic">Chromatic</option>
                    <option value="wholeTone">Whole Tone</option>
                    <option value="diminished">Diminished</option>
                </select>
            </div>

            <div class="control-group">
                <label for="mode">Mode</label>
                <select id="mode">
                    <option value="0">Ionian (I)</option>
                    <option value="1">Dorian (II)</option>
                    <option value="2">Phrygian (III)</option>
                    <option value="3">Lydian (IV)</option>
                    <option value="4">Mixolydian (V)</option>
                    <option value="5">Aeolian (VI)</option>
                    <option value="6">Locrian (VII)</option>
                </select>
            </div>

            <div class="control-group">
                <label><input type="checkbox" id="spiral-toggle"> Spiral Mode</label>
            </div>
        </div>

        <script>
            // ------- Global Constants & Variables -------
            const notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
            const keyboardLayout = ['1','2','3','4','5','6','7','8','9','0','q','w','e','r','t','y','u','i','o','p','a','s','d','f','g','h','j','k','l','z','x','c','v','b','n','m'];
            const noteKeyMappings = {};   // note-octave -> key
            const keyToNoteMapping = {};  // key -> {noteIndex, octave}

            let audioContext = null;
            let audioEnabled = false;
            const audioBuffers = {};
            const defaultOctave = 4; // visually highlight

            let spiralMode = false;
            const R0 = 100; // base radius for spiral

            // ------- Audio Helpers -------
            function initAudio() {
                try {
                    window.AudioContext = window.AudioContext || window.webkitAudioContext;
                    audioContext = new AudioContext();
                    if (audioContext.state === 'suspended') audioContext.resume();
                    // Pre-generate buffers for 3 octaves (3–5)
                    for (let octave of [3,4,5]) {
                        for (let i = 0; i < 12; i++) {
                            const freq = getFrequency(i, octave);
                            const key = `${i}-${octave}`;
                            audioBuffers[key] = createAudioBuffer(freq);
                        }
                    }
                    audioEnabled = true;
                    console.log("Audio ready");
                } catch(e) {
                    console.error("Audio init failed", e);
                }
            }
            function createAudioBuffer(freq, duration=.5) {
                if (!audioContext) return null;
                const sr = audioContext.sampleRate;
                const length = sr * duration;
                const buf = audioContext.createBuffer(1, length, sr);
                const data = buf.getChannelData(0);
                for (let i=0;i<length;i++) {
                    const t = i/sr;
                    const env = Math.min(1,10*t)*Math.max(0,1-3*(t-duration+0.3));
                    data[i] = env * Math.sin(2*Math.PI*freq*t);
                }
                return buf;
            }
            function getFrequency(noteIndex, octave) {
                const a4Index = 9 + 4*12;
                const noteIndex12 = noteIndex + octave*12;
                return 440 * Math.pow(2, (noteIndex12 - a4Index)/12);
            }
            function playNote(noteIndex, octave) {
                if (!audioEnabled) return;
                if (audioContext.state==='suspended') audioContext.resume();
                const src = audioContext.createBufferSource();
                src.buffer = audioBuffers[`${noteIndex}-${octave}`];
                const gain = audioContext.createGain();
                gain.gain.value = 0.3;
                src.connect(gain);
                gain.connect(audioContext.destination);
                src.start();
            }

            // ------- Keyboard Mapping -------
            function setupKeyboardMapping() {
                Object.keys(noteKeyMappings).forEach(k=>delete noteKeyMappings[k]);
                Object.keys(keyToNoteMapping).forEach(k=>delete keyToNoteMapping[k]);
                const allNotes = [];
                for (let octave=5;octave>=3;octave--) {
                    for (let i=11;i>=0;i--) {
                        allNotes.push({noteIndex:i, octave});
                    }
                }
                for (let i=0;i<Math.min(allNotes.length, keyboardLayout.length);i++) {
                    const {noteIndex, octave} = allNotes[i];
                    const keyChar = keyboardLayout[i];
                    noteKeyMappings[`${noteIndex}-${octave}`] = keyChar;
                    keyToNoteMapping[keyChar] = {noteIndex, octave};
                }
            }

            // ------- Scale Highlighting (unchanged) -------
            const scalePatterns = {
                major:[0,2,4,5,7,9,11],
                minor:[0,2,3,5,7,8,10],
                harmonicMinor:[0,2,3,5,7,8,11],
                melodicMinor:[0,2,3,5,7,9,11],
                pentatonicMajor:[0,2,4,7,9],
                pentatonicMinor:[0,3,5,7,10],
                blues:[0,3,5,6,7,10],
                chromatic:[0,1,2,3,4,5,6,7,8,9,10,11],
                wholeTone:[0,2,4,6,8,10],
                diminished:[0,2,3,5,6,8,9,11]
            };
            let currentScaleNotes = [];
            function updateScaleNotes() {
                const rootNote = +document.getElementById('root-note').value;
                const scaleType = document.getElementById('scale-pattern').value;
                const modeIndex = +document.getElementById('mode').value;
                const basePattern = scalePatterns[scaleType];
                let pattern = [...basePattern];
                if (modeIndex>0 && basePattern.length>modeIndex) {
                    pattern = [...basePattern.slice(modeIndex), ...basePattern.slice(0,modeIndex).map(n=>n+12)];
                    const first = pattern[0];
                    pattern = pattern.map(n=> (n-first)%12);
                }
                currentScaleNotes = pattern.map(p=>(rootNote+p)%12);
                document.querySelectorAll('.note-circle').forEach(el=>{
                    el.classList.toggle('in-scale', currentScaleNotes.includes(+el.dataset.note));
                });
            }

            // ------- Visualization Helpers -------
            function clearNotes() {
                document.querySelectorAll('.note-circle, .note-label').forEach(el=>el.remove());
            }

            function createNoteCircle(i, octave, x, y) {
                const container = document.querySelector('.container');
                const noteCircle = document.createElement('div');
                noteCircle.className='note-circle';
                noteCircle.dataset.note=i;
                noteCircle.dataset.octave=octave;
                noteCircle.style.left=`${x}px`;
                noteCircle.style.top=`${y}px`;
                noteCircle.style.width='20px';
                noteCircle.style.height='20px';

                // events
                noteCircle.addEventListener('mouseenter', ()=>showFrequency(x,y,getFrequency(i,octave).toFixed(1)));
                noteCircle.addEventListener('mouseleave', hideFrequency);
                noteCircle.addEventListener('click', ()=>{
                    playNote(i,octave);
                    activateNote(noteCircle);
                });

                document.querySelector('.container').appendChild(noteCircle);
            }

            function createCircularLayout() {
                // radii for octaves 3,4,5
                const radii = {3:150,4:220,5:290};
                for (let octave=3;octave<=5;octave++) {
                    const radiusBase = radii[octave];
                    for (let i=0;i<12;i++) {
                        const angle = i*30 * Math.PI/180;
                        const x = 300 + radiusBase * Math.sin(angle);
                        const y = 300 - radiusBase * Math.cos(angle);
                        createNoteCircle(i,octave,x,y);
                        if (octave===5) {
                            const labelRadius = radiusBase+25;
                            const lx = 300 + labelRadius*Math.sin(angle);
                            const ly = 300 - labelRadius*Math.cos(angle);
                            const noteLabel=document.createElement('div');
                            noteLabel.className='note-label';
                            noteLabel.textContent=notes[i];
                            noteLabel.style.left=`${lx}px`;
                            noteLabel.style.top=`${ly}px`;
                            document.querySelector('.container').appendChild(noteLabel);
                        }
                    }
                }
            }

            function createSpiralLayout() {
                let idx=0; // 0..35
                for (let octave=3;octave<=5;octave++) {
                    for (let i=0;i<12;i++) {
                        const globalIdx = idx; // semitone count from C3
                        const angle = globalIdx * Math.PI/6; // 30° per semitone
                        const r = R0 * Math.pow(2, globalIdx/12);
                        const x = 300 + r*Math.sin(angle);
                        const y = 300 - r*Math.cos(angle);
                        createNoteCircle(i,octave,x,y);
                        idx++;
                    }
                }
            }

            function renderNotes() {
                clearNotes();
                if (spiralMode) {
                    createSpiralLayout();
                } else {
                    createCircularLayout();
                }
                // highlight default octave
                document.querySelectorAll(`.note-circle[data-octave="${defaultOctave}"]`).forEach(el=>el.classList.add('active-octave'));
                updateScaleNotes();
                addKeyLabels();
            }

            function showFrequency(x, y, freq){
              let freqEl = document.querySelector('.frequency');
              if (!freqEl){
                freqEl = document.createElement('div');
                freqEl.className = 'frequency';
                document.querySelector('.container').appendChild(freqEl);
              }
              freqEl.textContent = `${freq} Hz`;
              freqEl.style.left = `${x}px`;   // centre of the circle
              freqEl.style.top  = `${y}px`;   // no manual -20 px tweak needed
              freqEl.style.opacity = '1';
            }
            function hideFrequency(){const f=document.querySelector('.frequency');if(f)f.style.opacity='0';}
            function activateNote(el){el.classList.add('active');setTimeout(()=>el.classList.remove('active'),300);}

            // ------- Key Labels after mapping -------
            function addKeyLabels() {
                document.querySelectorAll('.note-circle').forEach(noteCircle=>{
                    const i = +noteCircle.dataset.note;
                    const octave = +noteCircle.dataset.octave;
                    const key = `${i}-${octave}`;
                    if (noteKeyMappings[key]) {
                        const lbl=document.createElement('div');
                        lbl.className='key-label';
                        lbl.textContent=noteKeyMappings[key].toUpperCase();
                        noteCircle.appendChild(lbl);
                    }
                });
            }

            // ------- DOM Ready -------
            document.addEventListener('DOMContentLoaded',()=>{
                initAudio();
                setupKeyboardMapping();
                renderNotes();

                // global keyboard listener
                document.addEventListener('keydown',e=>{
                    const k=e.key.toLowerCase();
                    if (keyToNoteMapping[k]) {
                        const {noteIndex, octave} = keyToNoteMapping[k];
                        playNote(noteIndex,octave);
                        const noteEl = document.querySelector(`.note-circle[data-note="${noteIndex}"][data-octave="${octave}"]`);
                        if (noteEl) activateNote(noteEl);
                    }
                });

                // scale dropdown listeners
                ['root-note','scale-pattern','mode'].forEach(id=>{
                    document.getElementById(id).addEventListener('change',updateScaleNotes);
                });

                // Spiral toggle
                document.getElementById('spiral-toggle').addEventListener('change',e=>{
                    spiralMode = e.target.checked;
                    renderNotes();
                });
            });
        </script>
    </body>
    </html>
    '''

    return render_template_string(html_template)


if __name__ == '__main__':
    app.run(debug=True)
