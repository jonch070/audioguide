AudioGuide is a program for concatenative synthesis developed by Ben Hackbarth, Norbert Schnell, Philippe Esling, and Diemo Schwarz. It is written in python, however, one does not need to code in python to use AudioGuide - the user supplies simple options files that are written in python's syntax to interact with the program.

## 🆕 Web GUI (Beta)

A modern web-based interface is now available! No Python coding required.

**Quick Start:**
```bash
cd gui
pip install flask werkzeug
python app.py
# Open http://localhost:5000
```

**Features:**
- 🎛️ Intuitive parameter controls
- 📁 Drag-and-drop file management  
- 🎼 Pre-configured templates (single note, melody, chord)
- 📊 Real-time processing feedback
- 💾 Project save/load functionality

See `gui/README.md` for detailed documentation.

* AudioGuide can create a variety of different output file formats:
   * a csound score (which is rendered by default at the end of the concatenative process)
   * an .aaf file you can import into Logic/Pro Tools
   * a .rpp file you can open in Reaper
   * a file you can load into bach.roll in Max/MSP
   * a json file you can use in Max/MSP (or somewhere else)

AudioGuide differs from other programs for concatenative synthesis in several notable ways:

* AudioGuide is not realtime and therefore sounds can be layered much more densely compared to realtime concatenation.  Non-realtime analysis also permits more flexible and creative mapping between target and corpus descriptors as well as algorithmic accounting for overlapping corpus sounds in descriptor calculations.  More info about how to control the superimposition of sounds is [here](https://www.youtube.com/watch?v=V3MgfbaDi9I&t=288s).

* AudioGuide gives a large number of controls for fine tuning what sounds are included in the corpus, permitting the user to include and exclude segments according to descriptor values, filenames, restricting segment repetition, scaling amplitude, etc.  See all of the options [here](http://www.benhackbarth.com/audioGuide/docs_v1.35.html#TheCORPUSVariable).

* AudioGuide aims to give maximum creative control over how the sounds of the corpus are mapped onto the target.  Many different configurations for [normalizing corpus and target data](https://www.youtube.com/watch?v=UYElwMFF6Ug&t=17m46s) give the user a higher degree of control over the results and permit creative flexibility in defining similarity.

* Similarity between target and corpus sounds can be evaluated using time-varying descriptors, thus giving a better sense of the temporal morphology of sounds.  Watch [this](https://www.youtube.com/watch?v=UYElwMFF6Ug&t=217s).

* AudioGuide has a robust and flexible system for defining how corpus samples are matched to target segments. One may find the best match according to list of descriptors, but one may also define multiple search "passes", effectively creating a hierarchical search routine. One may also create boolean tests within the search function to further nuance the search process. See [here](https://www.youtube.com/watch?v=UYElwMFF6Ug&t=1535s).

## 🚀 Spectral Reconstruction

AudioGuide now supports **spectral reconstruction synthesis** - a mode where target sounds are analyzed for their spectral content and reconstructed by layering corpus sounds matched to individual spectral peaks.

**Key Features:**
- Direct FFT peak detection (no pitch estimation required)
- Whole-file analysis for sustained notes and chords
- Track-level volume automation (VOLENV)
- Polyphonic chord reconstruction support

**Documentation:**
- `CONTEXT.md` - Complete spectral reconstruction guide
- `ROADMAP.md` - Development roadmap and future plans
- `CHORD_RECONSTRUCTION_NOTES.md` - Polyphonic synthesis details

## 📋 Development Roadmap

See `ROADMAP.md` for the complete development plan including:

**Phase 1** (Next 2-4 weeks):
- ✅ HTML GUI implementation
- Project templates and workflows
- User documentation

**Phase 2** (4-8 weeks):
- FluCoMa integration for advanced analysis
- Enhanced segmentation algorithms
- Improved timbre matching

**Phase 3-5**: Performance optimizations, real-time capabilities, machine learning integration