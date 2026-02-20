// AudioGuide GUI JavaScript
class AudioGuideGUI {
    constructor() {
        this.projectData = {
            name: '',
            targetFile: null,
            corpusDir: null,
            settings: {
                useSpectral: false,
                wholeFile: false,
                volumeAutomation: false,
                maxPartials: 8,
                toleranceCents: 50,
                minAmplitude: 0.01
            },
            output: {
                format: 'rpp',
                name: 'spectral_output'
            }
        };
        
        this.initializeEventListeners();
        this.loadTemplates();
    }

    initializeEventListeners() {
        // File inputs
        document.getElementById('target-file').addEventListener('change', (e) => this.handleTargetFile(e));
        document.getElementById('corpus-dir').addEventListener('change', (e) => this.handleCorpusDir(e));
        
        // Project name
        document.getElementById('project-name').addEventListener('input', (e) => {
            this.projectData.name = e.target.value;
        });

        // Spectral settings
        document.getElementById('use-spectral').addEventListener('change', (e) => {
            this.projectData.settings.useSpectral = e.target.checked;
            this.toggleSpectralOptions(e.target.checked);
        });

        document.getElementById('whole-file').addEventListener('change', (e) => {
            this.projectData.settings.wholeFile = e.target.checked;
        });

        document.getElementById('volume-automation').addEventListener('change', (e) => {
            this.projectData.settings.volumeAutomation = e.target.checked;
        });

        // Sliders
        document.getElementById('max-partials').addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            document.getElementById('partials-value').textContent = value;
            this.projectData.settings.maxPartials = value;
        });

        document.getElementById('tolerance-cents').addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            document.getElementById('tolerance-value').textContent = value;
            this.projectData.settings.toleranceCents = value;
        });

        document.getElementById('min-amplitude').addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            document.getElementById('amplitude-value').textContent = value.toFixed(3);
            this.projectData.settings.minAmplitude = value;
        });

        // Output settings
        document.querySelectorAll('input[name="output"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.projectData.output.format = e.target.value;
            });
        });

        document.getElementById('output-name').addEventListener('input', (e) => {
            this.projectData.output.name = e.target.value;
        });

        // Template buttons
        document.querySelectorAll('.template-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.applyTemplate(e.target.dataset.template));
        });

        // Action buttons
        document.getElementById('validate-btn').addEventListener('click', () => this.validateSettings());
        document.getElementById('run-btn').addEventListener('click', () => this.runAudioGuide());
        document.getElementById('save-btn').addEventListener('click', () => this.saveProject());
        document.getElementById('load-btn').addEventListener('click', () => this.loadProject());
        document.getElementById('new-project-btn').addEventListener('click', () => this.newProject());
    }

    handleTargetFile(event) {
        const file = event.target.files[0];
        if (file) {
            this.projectData.targetFile = file;
            document.getElementById('target-info').textContent = `${file.name} (${this.formatFileSize(file.size)})`;
        }
    }

    handleCorpusDir(event) {
        const files = event.target.files;
        if (files.length > 0) {
            this.projectData.corpusDir = event.target.files;
            document.getElementById('corpus-info').textContent = `${files.length} files selected`;
        }
    }

    toggleSpectralOptions(enabled) {
        const spectralOptions = document.getElementById('spectral-section').querySelectorAll('.slider-group, .toggle-group');
        spectralOptions.forEach(option => {
            if (option.querySelector('#use-spectral') === null) {
                option.style.opacity = enabled ? '1' : '0.5';
                option.style.pointerEvents = enabled ? 'auto' : 'none';
            }
        });
    }

    loadTemplates() {
        this.templates = {
            'single-note': {
                name: 'Single Note',
                settings: {
                    useSpectral: true,
                    wholeFile: true,
                    volumeAutomation: false,
                    maxPartials: 8,
                    toleranceCents: 100,
                    minAmplitude: 0.01
                }
            },
            'melody': {
                name: 'Monophonic Melody',
                settings: {
                    useSpectral: true,
                    wholeFile: false,
                    volumeAutomation: true,
                    maxPartials: 4,
                    toleranceCents: 100,
                    minAmplitude: 0.01
                }
            },
            'chord': {
                name: 'Chord/Polyphonic',
                settings: {
                    useSpectral: true,
                    wholeFile: false,
                    volumeAutomation: true,
                    maxPartials: 24,
                    toleranceCents: 100,
                    minAmplitude: 0.02
                }
            },
            'custom': {
                name: 'Custom',
                settings: {
                    useSpectral: true,
                    wholeFile: false,
                    volumeAutomation: false,
                    maxPartials: 8,
                    toleranceCents: 50,
                    minAmplitude: 0.01
                }
            }
        };
    }

    applyTemplate(templateName) {
        const template = this.templates[templateName];
        if (!template) return;

        // Update button states
        document.querySelectorAll('.template-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-template="${templateName}"]`).classList.add('active');

        // Apply settings
        const settings = template.settings;
        
        document.getElementById('use-spectral').checked = settings.useSpectral;
        document.getElementById('whole-file').checked = settings.wholeFile;
        document.getElementById('volume-automation').checked = settings.volumeAutomation;
        
        document.getElementById('max-partials').value = settings.maxPartials;
        document.getElementById('partials-value').textContent = settings.maxPartials;
        
        document.getElementById('tolerance-cents').value = settings.toleranceCents;
        document.getElementById('tolerance-value').textContent = settings.toleranceCents;
        
        document.getElementById('min-amplitude').value = settings.minAmplitude;
        document.getElementById('amplitude-value').textContent = settings.minAmplitude.toFixed(3);

        // Update project data
        Object.assign(this.projectData.settings, settings);
        
        // Toggle spectral options
        this.toggleSpectralOptions(settings.useSpectral);

        // Show feedback
        this.showNotification(`Template "${template.name}" applied`, 'success');
    }

    validateSettings() {
        const errors = [];

        if (!this.projectData.name) {
            errors.push('Project name is required');
        }

        if (!this.projectData.targetFile) {
            errors.push('Target audio file is required');
        }

        if (!this.projectData.corpusDir || this.projectData.corpusDir.length === 0) {
            errors.push('Corpus directory is required');
        }

        if (this.projectData.settings.useSpectral) {
            if (this.projectData.settings.maxPartials < 1 || this.projectData.settings.maxPartials > 32) {
                errors.push('Max partials must be between 1 and 32');
            }

            if (this.projectData.settings.toleranceCents < 10 || this.projectData.settings.toleranceCents > 200) {
                errors.push('Frequency tolerance must be between 10 and 200 cents');
            }
        }

        if (errors.length > 0) {
            this.showNotification('Validation Errors:\n' + errors.join('\n'), 'error');
            return false;
        } else {
            this.showNotification('Settings validated successfully!', 'success');
            return true;
        }
    }

    async runAudioGuide() {
        if (!this.validateSettings()) {
            return;
        }

        // Show progress section
        document.getElementById('progress-section').classList.remove('hidden');
        document.getElementById('results-section').classList.add('hidden');

        // Prepare form data
        const formData = new FormData();
        formData.append('projectName', this.projectData.name);
        formData.append('targetFile', this.projectData.targetFile);
        
        // Add corpus files
        for (let i = 0; i < this.projectData.corpusDir.length; i++) {
            formData.append('corpusFiles', this.projectData.corpusDir[i]);
        }

        // Add settings
        formData.append('settings', JSON.stringify(this.projectData.settings));
        formData.append('output', JSON.stringify(this.projectData.output));

        try {
            this.updateProgress(0, 'Initializing AudioGuide...');

            const response = await fetch('/run-audioguide', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.updateProgress(100, 'Processing complete!');
                this.showResults(result);
            } else {
                throw new Error(result.error || 'Processing failed');
            }

        } catch (error) {
            this.showNotification(`Error: ${error.message}`, 'error');
            document.getElementById('progress-section').classList.add('hidden');
        }
    }

    updateProgress(percent, status) {
        document.getElementById('progress-fill').style.width = `${percent}%`;
        document.getElementById('status-text').textContent = status;
    }

    showResults(result) {
        const resultsSection = document.getElementById('results-section');
        const resultsInfo = document.getElementById('results-info');
        const downloadSection = document.getElementById('download-section');

        // Show results info
        resultsInfo.innerHTML = `
            <h3>✅ Processing Complete</h3>
            <p><strong>Project:</strong> ${this.projectData.name}</p>
            <p><strong>Duration:</strong> ${result.duration}s</p>
            <p><strong>Segments:</strong> ${result.segments}</p>
            <p><strong>Events:</strong> ${result.events}</p>
            <p><strong>Corpus files used:</strong> ${result.corpusFiles}</p>
        `;

        // Show download links
        downloadSection.innerHTML = '';
        result.files.forEach(file => {
            const link = document.createElement('a');
            link.href = `/download/${file.filename}`;
            link.className = 'download-btn';
            link.textContent = `Download ${file.displayName}`;
            link.download = file.filename;
            downloadSection.appendChild(link);
        });

        // Show results section
        resultsSection.classList.remove('hidden');
    }

    saveProject() {
        const projectData = {
            ...this.projectData,
            timestamp: new Date().toISOString()
        };

        const blob = new Blob([JSON.stringify(projectData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `${this.projectData.name || 'audioguide_project'}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
        this.showNotification('Project saved successfully!', 'success');
    }

    loadProject() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        const projectData = JSON.parse(e.target.result);
                        this.loadProjectData(projectData);
                        this.showNotification('Project loaded successfully!', 'success');
                    } catch (error) {
                        this.showNotification('Error loading project file', 'error');
                    }
                };
                reader.readAsText(file);
            }
        });
        
        input.click();
    }

    loadProjectData(projectData) {
        this.projectData = projectData;
        
        // Update UI
        document.getElementById('project-name').value = projectData.name || '';
        
        // Update settings
        const settings = projectData.settings;
        document.getElementById('use-spectral').checked = settings.useSpectral;
        document.getElementById('whole-file').checked = settings.wholeFile;
        document.getElementById('volume-automation').checked = settings.volumeAutomation;
        
        document.getElementById('max-partials').value = settings.maxPartials;
        document.getElementById('partials-value').textContent = settings.maxPartials;
        
        document.getElementById('tolerance-cents').value = settings.toleranceCents;
        document.getElementById('tolerance-value').textContent = settings.toleranceCents;
        
        document.getElementById('min-amplitude').value = settings.minAmplitude;
        document.getElementById('amplitude-value').textContent = settings.minAmplitude.toFixed(3);

        // Update output
        document.querySelector(`input[name="output"][value="${projectData.output.format}"]`).checked = true;
        document.getElementById('output-name').value = projectData.output.name;

        // Toggle spectral options
        this.toggleSpectralOptions(settings.useSpectral);
    }

    newProject() {
        if (confirm('Create a new project? Any unsaved changes will be lost.')) {
            location.reload();
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            max-width: 400px;
            background: ${type === 'success' ? 'var(--success-color)' : 
                         type === 'error' ? 'var(--error-color)' : 
                         'var(--primary-color)'};
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize GUI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.audioGuideGUI = new AudioGuideGUI();
});

// Handle file drops for better UX
document.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
});

document.addEventListener('drop', (e) => {
    e.preventDefault();
    // Handle file drops if needed
});