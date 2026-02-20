"""
AudioGuide Configuration I/O

Save and load configuration to/from JSON files.
"""

import json
import os
from typing import Dict, Any, Optional


def save_config_to_json(filepath: str, config: Optional[Dict[str, Any]] = None) -> None:
    """
    Save current configuration to JSON file.
    
    Args:
        filepath: Output path for JSON file
        config: Configuration dict to save. If None, saves current defaults.
    """
    import audioguide.defaults as defaults
    
    if config is None:
        config = _collect_defaults()
    
    # Serialize to JSON-compatible format
    serialized = _serialize_config(config)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(serialized, f, indent=2)


def load_config_from_json(filepath: str, apply_to_defaults: bool = True) -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        filepath: Path to JSON config file
        apply_to_defaults: If True, apply loaded config to defaults module
        
    Returns:
        Loaded configuration dictionary
    """
    import audioguide.defaults as defaults
    
    with open(filepath, 'r') as f:
        serialized = json.load(f)
    
    # Deserialize special types
    config = _deserialize_config(serialized)
    
    if apply_to_defaults:
        _apply_to_defaults(config)
    
    return config


def _collect_defaults() -> Dict[str, Any]:
    """Collect all uppercase variables from defaults module."""
    import audioguide.defaults as defaults
    
    config = {}
    for name in dir(defaults):
        if name.isupper() and not name.startswith('_'):
            value = getattr(defaults, name)
            # Skip modules, classes, functions
            if not callable(value) and not hasattr(value, '__module__'):
                config[name] = value
    
    return config


def _serialize_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize config to JSON-compatible format."""
    from audioguide.userclasses import (
        TargetOptionsEntry as tsf,
        CorpusOptionsEntry as csf,
        SuperimpositionOptionsEntry as si,
        SearchPassOptionsEntry as spass,
        Instrument as instr,
        Score as score
    )
    
    serialized = {}
    for key, value in config.items():
        serialized[key] = _serialize_value(value)
    
    return serialized


def _serialize_value(value: Any) -> Any:
    """Serialize a single value to JSON-compatible format."""
    from audioguide.userclasses import (
        TargetOptionsEntry as tsf,
        CorpusOptionsEntry as csf,
        SuperimpositionOptionsEntry as si,
        SearchPassOptionsEntry as spass,
        Instrument as instr,
        Score as score
    )
    
    # Handle special types by converting to dict representation
    value_type = type(value).__name__
    
    if value_type == 'TargetOptionsEntry':
        return {
            '__type__': 'tsf',
            'filename': value.filename,
            'start': value.start,
            'end': value.end,
            'thresh': value.thresh,
            'offsetRise': value.offsetRise,
            'offsetThreshAdd': value.offsetThreshAdd,
            'offsetThreshAbs': value.offsetThreshAbs,
            'scaleDb': value.scaleDb,
            'minSegLen': value.minSegLen,
            'maxSegLen': value.maxSegLen,
        }
    
    elif value_type == 'CorpusOptionsEntry':
        return {
            '__type__': 'csf',
            'corpusname': value.corpusname,
            'wholeFile': getattr(value, 'wholeFile', False),
            'instrTag': getattr(value, 'instrTag', None),
        }
    
    elif value_type == 'SuperimpositionOptionsEntry':
        return {
            '__type__': 'si',
            'superimpositionNumber': value.superimpositionNumber,
            'superimpositionMode': value.superimpositionMode,
        }
    
    elif isinstance(value, (list, tuple)):
        return [_serialize_value(item) for item in value]
    
    elif isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    
    else:
        return value


def _deserialize_config(serialized: Dict[str, Any]) -> Dict[str, Any]:
    """Deserialize config from JSON format."""
    from audioguide.userclasses import (
        TargetOptionsEntry as tsf,
        CorpusOptionsEntry as csf,
    )
    
    config = {}
    for key, value in serialized.items():
        config[key] = _deserialize_value(value)
    
    return config


def _deserialize_value(value: Any) -> Any:
    """Deserialize a single value from JSON format."""
    from audioguide.userclasses import (
        TargetOptionsEntry as tsf,
        CorpusOptionsEntry as csf,
    )
    
    if isinstance(value, dict):
        if '__type__' not in value:
            # Regular dict, deserialize contents
            return {k: _deserialize_value(v) for k, v in value.items()}
        
        # Special type
        type_ = value['__type__']
        
        if type_ == 'tsf':
            return tsf(
                value.get('filename'),
                start=value.get('start'),
                end=value.get('end'),
                thresh=value.get('thresh', -40),
                offsetRise=value.get('offsetRise', 1.5),
                offsetThreshAdd=value.get('offsetThreshAdd', 12),
                offsetThreshAbs=value.get('offsetThreshAbs', -80),
                scaleDb=value.get('scaleDb', 0),
                minSegLen=value.get('minSegLen', 0.1),
                maxSegLen=value.get('maxSegLen', 1000),
            )
        
        elif type_ == 'csf':
            return csf(
                value.get('corpusname'),
                wholeFile=value.get('wholeFile', False),
                instrTag=value.get('instrTag'),
            )
    
    elif isinstance(value, list):
        return [_deserialize_value(item) for item in value]
    
    return value


def _apply_to_defaults(config: Dict[str, Any]) -> None:
    """Apply configuration to defaults module."""
    import audioguide.defaults as defaults
    
    for key, value in config.items():
        if hasattr(defaults, key):
            setattr(defaults, key, value)


def export_current_config(filepath: str) -> None:
    """
    Export current defaults to a JSON file.
    
    This is a convenience alias for save_config_to_json().
    
    Args:
        filepath: Output path for JSON file
    """
    save_config_to_json(filepath)


def import_config(filepath: str) -> Dict[str, Any]:
    """
    Import configuration from a JSON file.
    
    This is a convenience alias for load_config_from_json().
    
    Args:
        filepath: Path to JSON config file
        
    Returns:
        Loaded configuration dictionary
    """
    return load_config_from_json(filepath)
