"""
AudioGuide Configuration Validator

Validates configuration options and provides detailed error messages
with suggestions for fixing issues.
"""

import os
import json
from typing import Dict, List, Any, Optional


class ConfigValidationError(Exception):
    """Exception raised when configuration validation fails."""
    
    def __init__(self, errors: List[Dict[str, str]]):
        self.errors = errors
        super().__init__(self._format_errors())
    
    def _format_errors(self):
        """Format all errors into a readable message."""
        if not self.errors:
            return "Configuration validation failed."
        
        lines = ["Configuration validation failed with the following issues:"]
        for i, err in enumerate(self.errors, 1):
            lines.append(f"  {i}. {err['field']}: {err['message']}")
            if 'suggestion' in err:
                lines.append(f"     → {err['suggestion']}")
        
        return "\n".join(lines)
    
    def to_dict(self):
        """Return errors as a list of dicts."""
        return self.errors


def validate_config(config_dict: Dict[str, Any]) -> ConfigValidationError:
    """
    Validate configuration dictionary.
    
    Args:
        config_dict: Configuration to validate
        
    Returns:
        ConfigValidationError with all issues found (not just first)
    """
    from audioguide import tests
    from audioguide.tests import UserVar_types
    
    errors = []
    
    # Get all uppercase config options from defaults
    import audioguide.defaults as defaults
    all_vars = {name: getattr(defaults, name) for name in dir(defaults) 
                if name.isupper() and not name.startswith('_')}
    
    for field, value in config_dict.items():
        # Skip special types that have their own validation
        if field in ('TARGET', 'CORPUS', 'SUPERIMPOSE', 'SEARCH', 'INSTRUMENTS'):
            continue
        
        # Get expected types for this field
        expected_types = UserVar_types.get(field, ['a string'])
        
        # Try each expected type
        valid = False
        for vtype in expected_types:
            if tests.testVariable(vtype, value):
                valid = True
                break
        
        if not valid:
            # Find a good suggestion
            suggestion = _get_suggestion(field, value, expected_types)
            errors.append({
                'field': field,
                'message': f"Must be {expected_types[0]} (got {type(value).__name__}: {value})",
                'suggestion': suggestion
            })
    
    # Special validation for TARGET and CORPUS
    if 'TARGET' in config_dict:
        target = config_dict['TARGET']
        if target is not None:
            from audioguide.userclasses import TargetOptionsEntry as tsf
            if not _is_instance(target, tsf):
                errors.append({
                    'field': 'TARGET',
                    'message': f"Must be a tsf() object (got {type(target).__name__})",
                    'suggestion': "Create with: TARGET = tsf('path/to/audio.wav', thresh=-40)"
                })
            else:
                # Check file exists
                if hasattr(target, 'filename') and target.filename:
                    if not os.path.exists(target.filename):
                        errors.append({
                            'field': 'TARGET',
                            'message': f"File not found: {target.filename}",
                            'suggestion': "Check the file path is correct and the file exists"
                        })
    
    if 'CORPUS' in config_dict:
        corpus = config_dict['CORPUS']
        if corpus is not None:
            from audioguide.userclasses import CorpusOptionsEntry as csf
            if not isinstance(corpus, list):
                errors.append({
                    'field': 'CORPUS',
                    'message': f"Must be a list of csf() objects (got {type(corpus).__name__})",
                    'suggestion': "Create with: CORPUS = [csf('path/to/corpus/dir')]"
                })
            else:
                for i, c in enumerate(corpus):
                    if not _is_instance(c, csf):
                        errors.append({
                            'field': f'CORPUS[{i}]',
                            'message': f"Must be a csf() object (got {type(c).__name__})",
                            'suggestion': "Each corpus entry should be: csf('path/to/dir')"
                        })
                    elif hasattr(c, 'corpusname') and c.corpusname:
                        # Check directory exists
                        if not os.path.exists(c.corpusname):
                            errors.append({
                                'field': f'CORPUS[{i}]',
                                'message': f"Corpus directory not found: {c.corpusname}",
                                'suggestion': "Check the corpus directory path is correct"
                            })
    
    # Validate numeric ranges
    if 'SPECTRAL_MAX_PARTIALS' in config_dict:
        val = config_dict['SPECTRAL_MAX_PARTIALS']
        if not isinstance(val, int) or val <= 0:
            errors.append({
                'field': 'SPECTRAL_MAX_PARTIALS',
                'message': f"Must be a positive integer (got {val})",
                'suggestion': "Set to a positive integer like 8 or 16"
            })
    
    if 'SPECTRAL_TOLERANCE_CENTS' in config_dict:
        val = config_dict['SPECTRAL_TOLERANCE_CENTS']
        if not isinstance(val, (int, float)) or val <= 0:
            errors.append({
                'field': 'SPECTRAL_TOLERANCE_CENTS',
                'message': f"Must be a positive number (got {val})",
                'suggestion': "Set to a positive number like 50 or 100"
            })
    
    if errors:
        return ConfigValidationError(errors)
    
    return None


def _is_instance(obj, cls):
    """Check if obj is instance of cls by comparing class names."""
    obj_name = type(obj).__name__
    cls_name = cls.__name__
    return obj_name == cls_name


def _get_suggestion(field: str, value: Any, expected_types: List[str]) -> str:
    """Get a helpful suggestion based on the field and value."""
    
    # Field-specific suggestions
    suggestions = {
        'USE_SPECTRAL_RECONSTRUCTION': "Set to True or False (not quoted)",
        'SPECTRAL_WHOLE_FILE': "Set to True or False (not quoted)",
        'SPECTRAL_MAX_PARTIALS': "Set to a positive integer like 4, 8, or 16",
        'SPECTRAL_TOLERANCE_CENTS': "Set to a positive number like 50 or 100",
        'SPECTRAL_MIN_AMPLITUDE_RATIO': "Set to a small decimal like 0.01 or 0.02",
        'ENABLE_TAKEENV': "Set to True or False (not quoted)",
        'FLUCOMA_ENABLE': "Set to True or False (not quoted)",
        'RANDOM_SEED': "Set to an integer or None",
        'OUTPUT_GAIN_DB': "Set to a number like 0.0 or -6.0",
    }
    
    if field in suggestions:
        return suggestions[field]
    
    # Type-based suggestions
    if isinstance(value, str):
        return "Remove quotes around the value if it's a boolean or number"
    
    return f"Expected: {expected_types[0]}"


def validate_config_file(filepath: str) -> Optional[ConfigValidationError]:
    """
    Validate a JSON configuration file.
    
    Args:
        filepath: Path to JSON config file
        
    Returns:
        ConfigValidationError if issues found, None if valid
    """
    if not os.path.exists(filepath):
        return ConfigValidationError([{
            'field': 'config_file',
            'message': f"File not found: {filepath}",
            'suggestion': "Check the file path is correct"
        }])
    
    try:
        with open(filepath, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        return ConfigValidationError([{
            'field': 'config_file',
            'message': f"Invalid JSON: {e}",
            'suggestion': "Fix JSON syntax errors (missing quotes, commas, brackets)"
        }])
    
    return validate_config(config)


def load_and_validate(filepath: str) -> Dict[str, Any]:
    """
    Load and validate a JSON configuration file.
    
    Args:
        filepath: Path to JSON config file
        
    Returns:
        Validated configuration dictionary
        
    Raises:
        ConfigValidationError: If validation fails
    """
    error = validate_config_file(filepath)
    if error:
        raise error
    
    with open(filepath, 'r') as f:
        return json.load(f)
