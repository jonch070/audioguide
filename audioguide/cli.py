#!/usr/bin/env python3
"""
AudioGuide Command-Line Interface

Headless CLI for running AudioGuide without the web GUI.
"""

import argparse
import sys
import os

# Ensure audioguide is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def parse_args(args=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog='audioguide',
        description='AudioGuide concatenative synthesis - command-line interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --template single_note --target input.wav --corpus corpus/
  %(prog)s --config config.json
  %(prog)s --validate-only --config config.json
  %(prog)s --template melody -v --target input.wav --corpus corpus/ --output output.rpp

Templates:
  single_note  Sustained notes with spectral reconstruction (whole-file)
  melody       Monophonic melodic material (segmented)
  chord        Polyphonic/chordal material with multiple partials
        """
    )
    
    parser.add_argument(
        '-c', '--config',
        help='JSON configuration file path'
    )
    
    parser.add_argument(
        '-t', '--template',
        choices=['single_note', 'melody', 'chord'],
        help='Use a template configuration (single_note, melody, chord)'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Run validation only, do not execute synthesis'
    )
    
    parser.add_argument(
        '-i', '--target',
        help='Target audio file path'
    )
    
    parser.add_argument(
        '-j', '--corpus',
        help='Corpus directory path'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information'
    )
    
    if args is None:
        return parser.parse_args()
    else:
        return parser.parse_args(args)


def main(args=None):
    """Main CLI entry point."""
    opts = parse_args(args)
    
    # Handle version flag
    if opts.version:
        from audioguide import __version__
        print(f"AudioGuide version {__version__}")
        return 0
    
    if opts.verbose:
        print("AudioGuide CLI - Starting...")
    
    # Step 1: Load template if specified
    config = {}
    if opts.template:
        if opts.verbose:
            print(f"Loading template: {opts.template}")
        from audioguide.templates import get_template
        config = get_template(opts.template)
    
    # Step 2: Load config file if specified
    if opts.config:
        if opts.verbose:
            print(f"Loading config: {opts.config}")
        from audioguide.config_io import load_config_from_json
        from audioguide.validator import validate_config_file
        
        # Validate first
        validation_error = validate_config_file(opts.config)
        if validation_error:
            print(validation_error)
            return 1
        
        file_config = load_config_from_json(opts.config)
        config.update(file_config)
    
    # Step 3: Apply command-line overrides
    # Set headless-friendly verbosity if not explicitly configured
    if 'VERBOSITY' not in config:
        # Check if we're running non-interactively
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            config['VERBOSITY'] = 0  # Headless mode - no progress bars
        # Otherwise use default (from defaults.py)
    
    if opts.target:
        if opts.verbose:
            print(f"Setting target: {opts.target}")
        from audioguide.userclasses import TargetOptionsEntry as tsf
        config['TARGET'] = tsf(opts.target)
    
    if opts.corpus:
        if opts.verbose:
            print(f"Setting corpus: {opts.corpus}")
        from audioguide.userclasses import CorpusOptionsEntry as csf
        if 'CORPUS' not in config:
            config['CORPUS'] = []
        config['CORPUS'].append(csf(opts.corpus))
    
    if opts.output:
        if opts.verbose:
            print(f"Setting output: {opts.output}")
        # Set appropriate output file based on extension
        if opts.output.endswith('.rpp'):
            config['RPP_FILEPATH'] = opts.output
        elif opts.output.endswith('.csd'):
            config['CSOUND_CSD_FILEPATH'] = opts.output
        elif opts.output.endswith('.json'):
            config['DICT_OUTPUT_FILEPATH'] = opts.output
    
    # Step 4: Validate configuration
    if opts.verbose:
        print("Validating configuration...")
    
    from audioguide.validator import validate_config, ConfigValidationError
    validation_error = validate_config(config)
    
    if validation_error:
        print(validation_error)
        return 1
    
    if opts.validate_only:
        print("Configuration validation passed!")
        if config:
            print("\nValidated configuration:")
            for key in sorted(config.keys())[:10]:
                print(f"  {key}: {type(config[key]).__name__}")
            if len(config) > 10:
                print(f"  ... and {len(config) - 10} more")
        return 0
    
    # Step 5: Run synthesis
    if opts.verbose:
        print("Running synthesis...")
    
    try:
        from audioguide import concatenate
        concatenate(config)
        print("Synthesis complete!")
        return 0
    except Exception as e:
        from audioguide.util import error
        error("SYNTHESIS", str(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
