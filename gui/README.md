# AudioGuide GUI

A modern web-based interface for AudioGuide spectral reconstruction synthesis.

## Quick Start

1. **Install dependencies:**
```bash
pip install flask werkzeug
```

2. **Run the GUI server:**
```bash
cd gui
python app.py
```

3. **Open your browser:**
Navigate to http://localhost:5000

## Features

### 🎛️ Intuitive Interface
- **Parameter Configuration**: Easy-to-use sliders and toggles for all AudioGuide settings
- **File Management**: Drag-and-drop target audio and corpus directories
- **Project Templates**: Pre-configured settings for common use cases
- **Real-time Validation**: Instant feedback on configuration errors

### 🎵 Audio Processing
- **Spectral Reconstruction**: Complete control over additive synthesis parameters
- **Whole-File Analysis**: Perfect for sustained notes and chords
- **Volume Automation**: Track-level VOLENV generation
- **Multiple Output Formats**: RPP, AAF, Csound, JSON

### 📊 Visualization & Feedback
- **Progress Tracking**: Real-time processing status
- **Results Summary**: Detailed statistics about your reconstruction
- **File Downloads**: Easy access to generated projects and audio
- **Log Output**: Detailed processing information

## Project Templates

### Single Note 🎼
- **Use Case**: Isolated sustained notes or single tones
- **Settings**: Whole-file analysis, 8 partials, 100 cent tolerance
- **Perfect for**: Instrument sampling, harmonic analysis

### Monophonic Melody 🎵
- **Use Case**: Single-line melodies and phrases
- **Settings**: Segmented analysis, 4 partials, volume automation enabled
- **Perfect for**: Melodic reconstruction, clear fundamental preservation

### Chord/Polyphonic 🎹
- **Use Case**: Multiple simultaneous notes, harmony
- **Settings**: 24 partials, higher amplitude threshold
- **Perfect for**: Chord reconstruction, harmonic textures

### Custom ⚙️
- **Use Case**: Complete control over all parameters
- **Settings**: Default starting point for experimentation
- **Perfect for**: Advanced users and research

## Parameter Guide

### Core Settings

- **Max Partials**: Number of spectral peaks to reconstruct (1-32)
  - Single notes: 4-8
  - Melodies: 4-8 (fundamental + harmonics)
  - Chords: 16-32 (multiple fundamentals)

- **Frequency Tolerance**: Matching tolerance in cents (10-200)
  - 100 cents = 1 semitone
  - Lower values = more precise matching
  - Higher values = more corpus matches

- **Min Amplitude Ratio**: Filter weak spectral peaks (0.001-0.1)
  - 0.01 = 1% of strongest peak
  - Higher values reduce noise, may miss quiet partials

### Advanced Options

- **Whole-File Analysis**: Analyze entire target as one spectral snapshot
  - ✅ Use for: Sustained notes, drones, chords
  - ❌ Avoid for: Melodies with note changes

- **Volume Automation**: Time-varying amplitude for each partial
  - Creates VOLENV automation in Reaper projects
  - More realistic amplitude evolution

## Workflow

### Basic Workflow
1. **Create Project**: Give your project a meaningful name
2. **Upload Target**: Select the audio you want to reconstruct
3. **Select Corpus**: Choose directory with source sounds
4. **Configure Settings**: Use templates or custom parameters
5. **Validate**: Check configuration for errors
6. **Process**: Run AudioGuide and monitor progress
7. **Download**: Access generated project files

### Pro Tips

#### Corpus Selection
- **Pure Sine Waves**: Best for clean additive synthesis
- **Chromatic Coverage**: Ensure frequency range matches target
- **Quality Matters**: Pure harmonics reduce spectral pollution

#### Parameter Optimization
- **Start Simple**: Begin with 4 partials, increase if needed
- **Listen First**: Audio quality matters more than numbers
- **Iterate**: Adjust based on results, not just theory

#### File Management
- **Organize**: Keep projects in separate folders
- **Backup**: Save project configurations for later
- **Clean Up**: Remove temporary files after processing

## Technical Details

### Supported Formats
- **Target Audio**: WAV, AIFF, MP3, FLAC, OGG, M4A
- **Corpus Files**: Same as target formats
- **Output**: RPP (Reaper), AAF (Logic/Pro Tools), Csound (.csd), JSON

### Performance
- **File Size Limit**: 500MB per upload
- **Processing Timeout**: 5 minutes
- **Memory Usage**: Depends on corpus size and analysis settings

### Browser Compatibility
- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+

## Troubleshooting

### Common Issues

**"Validation Failed"**
- Check that all required fields are filled
- Ensure target audio and corpus files are selected
- Verify spectral settings are in valid ranges

**"Processing Timeout"**
- Reduce corpus size or number of partials
- Try simpler settings first
- Check target file length

**"Poor Audio Quality"**
- Increase frequency tolerance
- Adjust amplitude threshold
- Try different corpus material
- Reduce number of partials for melodic content

**"File Not Found" Errors**
- Ensure uploads completed successfully
- Check file formats are supported
- Verify file permissions

### Getting Help

1. **Check Logs**: Review processing output for clues
2. **Validate Settings**: Use the validation button before processing
3. **Start Simple**: Begin with templates and basic settings
4. **Consult Documentation**: See main AudioGuide docs for detailed parameters

## Development

### Project Structure
```
gui/
├── app.py                 # Flask backend server
├── static/
│   ├── css/
│   │   └── style.css      # Responsive CSS styles
│   ├── js/
│   │   └── main.js        # Frontend JavaScript
│   └── index.html         # Main GUI (moved to templates/)
├── templates/
│   └── index.html         # Flask template
└── README.md              # This file
```

### Customization

The GUI is designed to be easily customizable:

- **CSS Variables**: Modify colors and spacing in `style.css`
- **Templates**: Add new project templates in `main.js`
- **Parameters**: Extend form fields for new AudioGuide features
- **Output Formats**: Add support for additional export formats

### Contributing

We welcome contributions! Areas needing help:

- **UI/UX**: Design improvements and user experience
- **Features**: New AudioGuide parameter integration
- **Testing**: Cross-browser compatibility testing
- **Documentation**: Guides and tutorials

## License

This GUI is part of the AudioGuide project. See the main AudioGuide license for details.