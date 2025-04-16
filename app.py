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
        <title>Musical Octaves</title>
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
            .note-circle[data-octave="3"] {
                border: 1px solid transparent;
            }
            .note-circle[data-octave="4"] {
                border: 1px solid transparent;
            }
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
                color: #000000; /* Changed to black */
                font-size: 10px;
                font-weight: bold;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                pointer-events: none;
                z-index: 10;
            }
            .subtitle {
                position: absolute;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 16px;
                color: #aaa;
                text-align: center;
                width: 100%;
            }
            .instructions {
                position: absolute;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 14px;
                color: #888;
                text-align: center;
                width: 80%;
            }
            .frequency {
                position: absolute;
                color: #aaa;
                font-size: 12px;
                opacity: 0;
                transition: opacity 0.3s ease;
                transform: translate(-50%, -50%);
                pointer-events: none;
            }
            .octave-label {
                position: absolute;
                left: 50%;
                transform: translateX(-50%);
                color: #aaa;
                font-size: 12px;
            }
            .status {
                position: absolute;
                top: 50px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 14px;
                color: #64ffda;
                text-align: center;
            }
            .key-instructions {
                position: absolute;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 14px;
                color: #64ffda;
                text-align: center;
                width: 80%;
            }
            /* New side panel styles */
            .control-panel {
                position: fixed;
                right: 0;
                top: 0;
                width: 250px;
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
            .control-group select {
                width: 100%;
                padding: 8px;
                background-color: #2a2a2a;
                border: 1px solid #444;
                color: #eee;
                border-radius: 4px;
            }
            .control-group select:focus {
                outline: none;
                border-color: #64ffda;
            }
            /* Style for scale notes list */
            .scale-notes {
                display: none; /* Hide the scale notes */
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="status" id="status"></div>
        </div>

            <!-- Side control panel without scale notes display -->
            <div class="control-panel">
                <h3>Scale Controls</h3>

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
                        <option value="blues">Blues Scale [3,2,1,1,3,2]</option>
                        <option value="chromatic">Chromatic [1,1,1,1,1,1,1,1,1,1,1,1]</option>
                        <option value="wholeTone">Whole Tone [2,2,2,2,2,2]</option>
                        <option value="diminished">Diminished [2,1,2,1,2,1,2,1]</option>
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
            </div>

        <script>
            // Create pre-computed audio files for all notes
            const notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];

            // Define keyboard layout - starting with numbers 1-0, then letters
            const keyboardLayout = [
                '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p',
                'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',
                'z', 'x', 'c', 'v', 'b', 'n', 'm'
            ];

            // Note to key mappings for all octaves
            const noteKeyMappings = {};

            // Reverse mapping: key to note and octave
            const keyToNoteMapping = {};

            // Debug function to test keyboard functionality
            function testKeyboardMapping() {
                console.log("Testing keyboard mapping...");

                // Simulate key presses for the first few notes
                for (let i = 0; i < 5; i++) {
                    if (i < keyboardLayout.length) {
                        const key = keyboardLayout[i];
                        console.log(`Simulating key press: ${key}`);

                        if (keyToNoteMapping[key]) {
                            const { noteIndex, octave } = keyToNoteMapping[key];
                            console.log(`Would play: ${notes[noteIndex]} (octave ${octave})`);
                        } else {
                            console.log(`No mapping found for key: ${key}`);
                        }
                    }
                }
            }

            let audioContext = null;
            let audioEnabled = false;
            const audioBuffers = {};
            const defaultOctave = 4; // Middle octave

            const scalePatterns = {
                major: [0, 2, 4, 5, 7, 9, 11], // Whole, Whole, Half, Whole, Whole, Whole, Half
                minor: [0, 2, 3, 5, 7, 8, 10], // Whole, Half, Whole, Whole, Half, Whole, Whole
                harmonicMinor: [0, 2, 3, 5, 7, 8, 11], // Natural minor with raised 7th
                melodicMinor: [0, 2, 3, 5, 7, 9, 11], // Ascending melodic minor
                pentatonicMajor: [0, 2, 4, 7, 9], // Major without 4th and 7th
                pentatonicMinor: [0, 3, 5, 7, 10], // Minor without 2nd and 6th
                blues: [0, 3, 5, 6, 7, 10], // Minor pentatonic with added diminished 5th
                chromatic: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], // All notes
                wholeTone: [0, 2, 4, 6, 8, 10], // Whole tone scale
                diminished: [0, 2, 3, 5, 6, 8, 9, 11] // Diminished scale (half-whole)
            };

            // Create stepwise interval sequences for each scale
            const scaleIntervals = {
                major: [2, 2, 1, 2, 2, 2, 1], // Intervals between consecutive notes: Whole, Whole, Half, Whole, Whole, Whole, Half
                minor: [2, 1, 2, 2, 1, 2, 2], // Whole, Half, Whole, Whole, Half, Whole, Whole
                harmonicMinor: [2, 1, 2, 2, 1, 3, 1], // Whole, Half, Whole, Whole, Half, Minor Third, Half
                melodicMinor: [2, 1, 2, 2, 2, 2, 1], // Whole, Half, Whole, Whole, Whole, Whole, Half
                pentatonicMajor: [2, 2, 3, 2, 3], // Whole, Whole, Minor Third, Whole, Minor Third
                pentatonicMinor: [3, 2, 2, 3, 2], // Minor Third, Whole, Whole, Minor Third, Whole
                blues: [3, 2, 1, 1, 3, 2], // Minor Third, Whole, Half, Half, Minor Third, Whole
                chromatic: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], // All Half steps
                wholeTone: [2, 2, 2, 2, 2, 2], // All Whole steps
                diminished: [2, 1, 2, 1, 2, 1, 2, 1] // Alternating Whole-Half steps
            };

            // Track the current scale's notes
            let currentScaleNotes = [];

            // Calculate and update which notes are in the current scale
            function updateScaleNotes() {
                // Get selected values
                const rootNote = parseInt(document.getElementById('root-note').value);
                const scaleType = document.getElementById('scale-pattern').value;
                const modeIndex = parseInt(document.getElementById('mode').value);

                // Clear previous scale highlighting
                document.querySelectorAll('.note-circle.in-scale').forEach(el => {
                    el.classList.remove('in-scale');
                });

                // Get scale pattern
                const basePattern = scalePatterns[scaleType];

                // Adjust for mode (rotate the pattern)
                let pattern = [];
                if (modeIndex > 0 && basePattern.length > modeIndex) {
                    // For modes, we rotate the pattern
                    pattern = [
                        ...basePattern.slice(modeIndex),
                        ...basePattern.slice(0, modeIndex).map(n => n + 12)
                    ];

                    // Normalize pattern to start from 0 (adjust all values down by pattern[0])
                    const firstValue = pattern[0];
                    pattern = pattern.map(n => (n - firstValue) % 12);
                } else {
                    pattern = [...basePattern];
                }

                // Calculate actual notes in the scale
                currentScaleNotes = pattern.map(interval => (rootNote + interval) % 12);

                // Update UI to show which notes are in the scale
                document.querySelectorAll('.note-circle').forEach(noteCircle => {
                    const noteIndex = parseInt(noteCircle.dataset.note);
                    if (currentScaleNotes.includes(noteIndex)) {
                        noteCircle.classList.add('in-scale');
                    }
                });

                // Update scale notes display in control panel
                const scaleNotesDisplay = document.getElementById('scale-notes');
                const rootNoteName = notes[rootNote];
                const scaleTypeFormatted = scaleType.replace(/([A-Z])/g, ' $1').toLowerCase();
                const scaleTypeCapitalized = scaleTypeFormatted.charAt(0).toUpperCase() + scaleTypeFormatted.slice(1);

                // Get mode name
                const modeNames = ["Ionian", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Locrian"];
                const modeName = modeNames[modeIndex] || "";

                // We don't need to display scale notes in the panel as requested
                // But we still calculate them for debugging
                const scaleNoteNames = currentScaleNotes.map(noteIdx => notes[noteIdx]).join(', ');

                console.log(`Updated scale: ${rootNoteName} ${scaleType} ${modeName} - Notes: ${scaleNoteNames}`);
            }

            // Create audio buffer for a given frequency
            function createAudioBuffer(frequency, duration = .5) {
                if (!audioContext) return null;

                const sampleRate = audioContext.sampleRate;
                const bufferSize = duration * sampleRate;
                const buffer = audioContext.createBuffer(1, bufferSize, sampleRate);
                const data = buffer.getChannelData(0);

                for (let i = 0; i < bufferSize; i++) {
                    // Sine wave with amplitude envelope
                    const t = i / sampleRate;
                    const envelope = Math.min(1, 10 * t) * Math.max(0, 1 - 3 * (t - duration + 0.3));
                    data[i] = envelope * Math.sin(2 * Math.PI * frequency * t);
                }

                return buffer;
            }

            // Calculate frequency for a note
            function getFrequency(noteIndex, octave) {
                // A4 = 440Hz (note index 9, octave 4)
                const a4Index = 9 + (4 * 12);
                const noteIndex12 = noteIndex + (octave * 12);
                return 440 * Math.pow(2, (noteIndex12 - a4Index) / 12);
            }

            // Initialize audio system
            function initAudio() {
                try {
                    window.AudioContext = window.AudioContext || window.webkitAudioContext;
                    audioContext = new AudioContext();

                    // Auto-resume AudioContext if it's in suspended state
                    if (audioContext.state === 'suspended') {
                        audioContext.resume();
                    }

                    // Pre-generate all note buffers
                    const octaves = [3, 4, 5]; // Lower, middle, higher

                    for (let octave of octaves) {
                        for (let i = 0; i < 12; i++) {
                            const frequency = getFrequency(i, octave);
                            const key = `${i}-${octave}`;
                            audioBuffers[key] = createAudioBuffer(frequency);
                        }
                    }

                    audioEnabled = true;
                    console.log("Audio initialized successfully");
                    return true;
                } catch (e) {
                    console.error("Audio initialization failed:", e);
                    document.getElementById('status').textContent = 'Audio failed to initialize: ' + e.message;
                    return false;
                }
            }

            // Play a note
            function playNote(noteIndex, octave) {
                if (!audioEnabled || !audioContext) return;

                try {
                    // Check if context is suspended (browser policy) and resume it
                    if (audioContext.state === 'suspended') {
                        audioContext.resume();
                    }

                    const key = `${noteIndex}-${octave}`;
                    const buffer = audioBuffers[key];

                    if (!buffer) {
                        console.warn(`No buffer for note ${notes[noteIndex]} at octave ${octave}`);
                        return;
                    }

                    const source = audioContext.createBufferSource();
                    const gainNode = audioContext.createGain();

                    source.buffer = buffer;
                    gainNode.gain.value = 0.3;

                    source.connect(gainNode);
                    gainNode.connect(audioContext.destination);

                    source.start();
                    console.log(`Playing ${notes[noteIndex]} (octave ${octave}) - ${getFrequency(noteIndex, octave).toFixed(2)} Hz`);
                } catch (e) {
                    console.error("Error playing note:", e);
                }
            }

            // Ensure keyboard events work globally
            const keyDownHandler = (event) => {
                const key = event.key.toLowerCase();
                console.log(`Global key handler: ${key}`);

                // Check if the pressed key is in our mapping
                if (keyToNoteMapping[key]) {
                    const { noteIndex, octave } = keyToNoteMapping[key];
                    console.log(`Playing note: ${notes[noteIndex]} (octave ${octave})`);

                    // Play the note
                    playNote(noteIndex, octave);

                    // Activate the corresponding note circle
                    const noteElement = document.querySelector(
                        `.note-circle[data-note="${noteIndex}"][data-octave="${octave}"]`
                    );

                    if (noteElement) {
                        // Visual feedback
                        noteElement.classList.add('active');
                        setTimeout(() => {
                            noteElement.classList.remove('active');
                        }, 300);
                    }
                }
            };

            // Add global event listener
            document.addEventListener('keydown', keyDownHandler);

            document.addEventListener('DOMContentLoaded', () => {
                const container = document.querySelector('.container');

                // Initialize audio when page loads
                initAudio();
                setupVisualElements();

                // Set up keyboard mappings first, then add listeners
                setupKeyboardMapping();

                // Small delay to ensure DOM is ready and mappings are set
                setTimeout(() => {
                    // Add key labels after mappings are set up
                    if (window.addKeyLabels) {
                        window.addKeyLabels();
                    }

                    setupKeyboardListeners();
                    console.log("Keyboard listeners set up");

                    // Initialize the scale notes
                    updateScaleNotes();

                    // Setup scale control listeners
                    document.getElementById('root-note').addEventListener('change', updateScaleNotes);
                    document.getElementById('scale-pattern').addEventListener('change', updateScaleNotes);
                    document.getElementById('mode').addEventListener('change', updateScaleNotes);

                    // Add message to console to test keyboard
                    console.log("Try pressing keys Q-P, A-L, Z-M to play notes");
                }, 200);

                // Handle user interaction to unlock audio on browsers that require it
                function unlockAudio() {
                    if (audioContext && audioContext.state === 'suspended') {
                        audioContext.resume().then(() => {
                            console.log('AudioContext resumed successfully');
                        });
                    }
                    document.removeEventListener('click', unlockAudio);
                    document.removeEventListener('touchstart', unlockAudio);
                }

                // Add event listeners for user interaction to unlock audio
                document.addEventListener('click', unlockAudio);
                document.addEventListener('touchstart', unlockAudio);

                function setupVisualElements() {
                    // Create notes for each octave
                    createOctave(3, 150); // Lower octave (3)
                    createOctave(4, 220); // Middle octave (4)
                    createOctave(5, 290); // Higher octave (5)

                    // Highlight the default octave
                    document.querySelectorAll(`.note-circle[data-octave="${defaultOctave}"]`).forEach(circle => {
                        circle.classList.add('active-octave');
                    });

                    // Add a function to add key labels after mapping is complete
                    window.addKeyLabels = function() {
                        console.log("Adding key labels to notes");
                        document.querySelectorAll('.note-circle').forEach(noteCircle => {
                            const i = parseInt(noteCircle.dataset.note);
                            const octave = parseInt(noteCircle.dataset.octave);
                            const noteKey = `${i}-${octave}`;

                            if (noteKeyMappings[noteKey]) {
                                const keyLabel = document.createElement('div');
                                keyLabel.className = 'key-label';
                                keyLabel.textContent = noteKeyMappings[noteKey].toUpperCase();
                                noteCircle.appendChild(keyLabel);

                                console.log(`Added key label ${noteKeyMappings[noteKey].toUpperCase()} for note ${notes[i]} (octave ${octave})`);
                            }
                        });
                    };
                }

                // Setup keyboard to note mappings
                function setupKeyboardMapping() {
                    // Clear any existing mappings
                    Object.keys(noteKeyMappings).forEach(key => delete noteKeyMappings[key]);
                    Object.keys(keyToNoteMapping).forEach(key => delete keyToNoteMapping[key]);

                    console.log("Setting up keyboard mappings...");

                    // We have 36 notes total (12 notes x 3 octaves)
                    // Assign keys from highest to lowest pitch (as per requirement)

                    // We'll go from highest octave (5) to lowest (3)
                    // And for each octave, from highest note (B) to lowest (C)
                    const allNotes = [];

                    // Add notes from highest to lowest pitch
                    for (let octave = 5; octave >= 3; octave--) {
                        for (let i = 11; i >= 0; i--) {
                            allNotes.push({ noteIndex: i, octave });
                        }
                    }

                    console.log(`Total notes to map: ${allNotes.length}`);
                    console.log(`Available keys: ${keyboardLayout.length}`);

                    // Assign keyboard keys to notes, starting with 'q' for the highest pitch
                    for (let i = 0; i < Math.min(allNotes.length, keyboardLayout.length); i++) {
                        const { noteIndex, octave } = allNotes[i];
                        const noteKey = `${noteIndex}-${octave}`;
                        const keyChar = keyboardLayout[i];

                        // Store mapping
                        noteKeyMappings[noteKey] = keyChar;
                        keyToNoteMapping[keyChar] = { noteIndex, octave };

                        console.log(`Assigned key '${keyChar}' to note ${notes[noteIndex]} (octave ${octave})`);
                    }

                    // Debug - print first few mappings
                    console.log("First 5 key mappings:");
                    Object.entries(keyToNoteMapping).slice(0, 5).forEach(([key, value]) => {
                        console.log(`Key ${key} -> Note ${notes[value.noteIndex]} (octave ${value.octave})`);
                    });
                }

                // Setup keyboard event listeners
                function setupKeyboardListeners() {
                    document.addEventListener('keydown', (event) => {
                        const key = event.key.toLowerCase();
                        console.log(`Key pressed: ${key}`);

                        // Check if the pressed key is in our mapping
                        if (keyToNoteMapping[key]) {
                            const { noteIndex, octave } = keyToNoteMapping[key];
                            console.log(`Playing note: ${notes[noteIndex]} (octave ${octave})`);

                            // Play the note
                            playNote(noteIndex, octave);

                            // Activate the corresponding note circle
                            const noteElement = document.querySelector(
                                `.note-circle[data-note="${noteIndex}"][data-octave="${octave}"]`
                            );

                            if (noteElement) {
                                activateNote(noteElement);
                            } else {
                                console.warn(`Could not find note element for ${notes[noteIndex]} (octave ${octave})`);
                            }
                        }
                    });

                    // Log the complete keyboard mapping for debugging
                    console.log("Keyboard mappings:", keyToNoteMapping);
                }

                // Create octave visualization
                function createOctave(octave, radiusBase) {
                    for (let i = 0; i < 12; i++) {
                        // Calculate position on circle
                        const angle = (i * 30) * (Math.PI / 180);
                        const x = 300 + radiusBase * Math.sin(angle);
                        const y = 300 - radiusBase * Math.cos(angle);

                        // Create note circle with slightly larger size to accommodate key label
                        const noteCircle = document.createElement('div');
                        noteCircle.className = 'note-circle';
                        noteCircle.dataset.note = i;
                        noteCircle.dataset.octave = octave;
                        noteCircle.style.left = `${x}px`;
                        noteCircle.style.top = `${y}px`;
                        noteCircle.style.width = '20px';  // Slightly larger to fit key labels
                        noteCircle.style.height = '20px';
                        container.appendChild(noteCircle);

                        // Add event listeners
                        noteCircle.addEventListener('mouseenter', () => {
                            const freq = getFrequency(i, octave);
                            showFrequency(x, y, freq.toFixed(1));
                        });

                        noteCircle.addEventListener('mouseleave', () => {
                            hideFrequencies();
                        });

                        noteCircle.addEventListener('click', () => {
                            if (audioContext && audioContext.state === 'suspended') {
                                audioContext.resume().then(() => {
                                    playNote(i, octave);
                                    activateNote(noteCircle);
                                });
                            } else {
                                playNote(i, octave);
                                activateNote(noteCircle);
                            }
                        });

                        // Add note labels only to the outermost circle
                        if (octave === 5) {
                            const labelRadius = radiusBase + 25;
                            const labelX = 300 + labelRadius * Math.sin(angle);
                            const labelY = 300 - labelRadius * Math.cos(angle);

                            const noteLabel = document.createElement('div');
                            noteLabel.className = 'note-label';
                            noteLabel.textContent = notes[i];
                            noteLabel.style.left = `${labelX}px`;
                            noteLabel.style.top = `${labelY}px`;
                            container.appendChild(noteLabel);
                        }

                        // We'll add key labels later after the mapping is complete
                        // Store the info needed to create the label
                        noteCircle.dataset.angle = angle;
                        noteCircle.dataset.radiusBase = radiusBase;
                    }
                }

                // Show frequency display
                function showFrequency(x, y, freq) {
                    let freqDisplay = document.querySelector('.frequency');
                    if (!freqDisplay) {
                        freqDisplay = document.createElement('div');
                        freqDisplay.className = 'frequency';
                        container.appendChild(freqDisplay);
                    }

                    freqDisplay.textContent = `${freq} Hz`;
                    freqDisplay.style.left = `${x}px`;
                    freqDisplay.style.top = `${y - 20}px`;
                    freqDisplay.style.opacity = '1';
                }

                // Hide frequency display
                function hideFrequencies() {
                    const freqDisplay = document.querySelector('.frequency');
                    if (freqDisplay) freqDisplay.style.opacity = '0';
                }

                // Visual feedback for active notes
                function activateNote(noteElement) {
                    noteElement.classList.add('active');
                    setTimeout(() => {
                        noteElement.classList.remove('active');
                    }, 300);
                }
            });
        </script>
    </body>
    </html>
    '''

    return render_template_string(html_template)


if __name__ == '__main__':
    app.run(debug=True)