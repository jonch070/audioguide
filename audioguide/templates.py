"""
AudioGuide Template System

Provides pre-configured templates for common use cases:
- single_note: Sustained single notes with spectral reconstruction
- melody: Monophonic melodic material with segmentation
- chord: Polyphonic/chord material with multiple partials
"""

# Note: defaults is imported lazily in functions that need it
# to avoid circular import issues

# Template definitions
TEMPLATES = {
    'single_note': {
        # Whole-file spectral reconstruction for sustained notes
        'USE_SPECTRAL_RECONSTRUCTION': True,
        'SPECTRAL_WHOLE_FILE': True,
        'SPECTRAL_MAX_PARTIALS': 8,
        'SPECTRAL_TOLERANCE_CENTS': 100,
        'SPECTRAL_MIN_AMPLITUDE_RATIO': 0.01,
        'ENABLE_SPECTRAL_VOLUMEENV': True,
    },
    'melody': {
        # Segmented spectral reconstruction for monophonic melodies
        'USE_SPECTRAL_RECONSTRUCTION': True,
        'SPECTRAL_WHOLE_FILE': False,
        'SPECTRAL_MAX_PARTIALS': 4,  # Fundamental + 3 harmonics for clarity
        'SPECTRAL_TOLERANCE_CENTS': 100,
        'SPECTRAL_MIN_AMPLITUDE_RATIO': 0.01,
        'ENABLE_SPECTRAL_VOLUMEENV': True,
        'SPECTRAL_ADAPTIVE_PARTIALS': True,  # Auto-detect complexity
    },
    'chord': {
        # Segmented for polyphonic/chordal material with more partials
        'USE_SPECTRAL_RECONSTRUCTION': True,
        'SPECTRAL_WHOLE_FILE': False,
        'SPECTRAL_MAX_PARTIALS': 24,  # Capture multiple fundamentals
        'SPECTRAL_TOLERANCE_CENTS': 50,
        'SPECTRAL_MIN_AMPLITUDE_RATIO': 0.02,  # Higher threshold for dense textures
        'ENABLE_SPECTRAL_VOLUMEENV': True,
        'SPECTRAL_POLYPHONIC': True,
        'SPECTRAL_POLYPHONIC_MAX_VOICES': 4,
    },
}


def list_templates():
    """Return list of available template names."""
    return list(TEMPLATES.keys())


def get_template(name):
    """
    Get template configuration by name.
    
    Args:
        name: Template name ('single_note', 'melody', 'chord')
        
    Returns:
        dict: Template configuration
        
    Raises:
        ValueError: If template name not found
    """
    if name not in TEMPLATES:
        available = ', '.join(TEMPLATES.keys())
        raise ValueError(f"Unknown template: '{name}'. Available: {available}")
    return TEMPLATES[name].copy()


def apply_template(template_name):
    """
    Apply template settings to the defaults module.
    
    Args:
        template_name: Name of template to apply
        
    Raises:
        ValueError: If template name not found
    """
    import audioguide.defaults as defaults
    
    template = get_template(template_name)
    
    for key, value in template.items():
        if hasattr(defaults, key):
            setattr(defaults, key, value)
        else:
            raise ValueError(f"Template references unknown config option: {key}")
    
    return template


def create_config_from_template(template_name, target_path=None, corpus_path=None):
    """
    Create a complete config dict from a template.
    
    Args:
        template_name: Name of template to use
        target_path: Optional path to target audio file
        corpus_path: Optional path to corpus directory
        
    Returns:
        dict: Complete configuration with template applied
    """
    from audioguide.userclasses import TargetOptionsEntry as tsf
    from audioguide.userclasses import CorpusOptionsEntry as csf
    
    config = get_template(template_name)
    
    # Add required fields if paths provided
    if target_path:
        config['TARGET'] = tsf(target_path)
    if corpus_path:
        config['CORPUS'] = [csf(corpus_path)]
    
    return config
