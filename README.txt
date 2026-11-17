# Strict counterpoint engine (Salzer & Schachter)

An algorithmic symbolic music processing tool written in Python that evaluates strict cantus firmus exercises based on the principles outlined in Felix Salzer and Carl Schachter's "Counterpoint in Composition".

I built this command-line interface engine to combine traditional music theory and software engineering. It parses MIDI files in this version 1.0 so it translates raw pitch data into traditional solfège. I runs a comprehensive sequence harmonic and melodic rules. It's essentially a pedagogical backend designed to provide immediate and contextual feedback for me for my music students's homework done in MuseScore. Planning to complete it with the other counterpoint species and minor modes, and a UI.

# Features

- **MIDI Parsing:** Extracts note events and rhythmic durations using the `mido` library.
- **Solfège translation:** Automatically converts MIDI note numbers (e.g., 60) into standard musical nomenclature (e.g., do4) for user-friendly console feedback.
- **Structural validation:** Evaluates vocal range, ambitus, correct rhythmic figures (whole notes mandatory) and human tonal boundaries.
- **Melodic contour analysis:** Evaluates undulating curves, ando single climax points. Also prevents futile oscillations or mechanical sequences.
- **Advanced interval logic:** 
  - Validates all leaps strictly against Salzer and Schachter's voice-leading rules.
  - **Look-ahead compensation:** Ensures large leaps (4ths, 5ths, minor 6ths, octaves) are properly prepared and immediately compensated by stepwise motion in the opposite direction.
  - Prevents consecutive unidirectional leaps and outlined tritone profiles.
- **Severity scaling:** Differentiates between strict contrapuntal errors (which halt execution) and pedagogical stylistic warnings (which suggest better vocal flow).

# Installation

1. Clone this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

# Usage

Place your cantus firmus MIDI file (e.g., cantus_test.mid) in the root directory alongside the script and run the engine:

bash
python counterpoint_engine.py

The orchestrator will evaluate the melody sequentially and print a detailed diagnostic report to the console.

# Roadmap & future work

V 1.0 (Current): Full support for strict Major mode Cantus Firmus.

V 2.0 (Planned): Implementation of minor mode strict rules.

V 3.0 (Planned): First species (note-against-note)