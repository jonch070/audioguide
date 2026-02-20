"""
AudioGuide Real-time Processing Module

Live audio input processing and real-time concatenative synthesis.
"""

import os
import threading
import time
import numpy as np
from typing import List, Optional, Callable, Dict, Any
from dataclasses import dataclass
from queue import Queue


@dataclass
class RealtimeConfig:
    """Configuration for real-time processing."""
    buffer_size: int = 512
    hop_size: int = 256
    sample_rate: int = 44100
    latency_target_ms: int = 20
    input_device: Optional[int] = None
    output_device: Optional[int] = None


class LatencyTracker:
    """Monitor and track processing latency."""
    
    def __init__(self):
        self.latencies = []
        self.max_latencies = 1000
    
    def add_latency(self, latency_ms: float):
        self.latencies.append(latency_ms)
        if len(self.latencies) > self.max_latencies:
            self.latencies.pop(0)
    
    @property
    def average_latency(self) -> float:
        return np.mean(self.latencies) if self.latencies else 0
    
    @property
    def max_latency(self) -> float:
        return np.max(self.latencies) if self.latencies else 0
    
    @property
    def min_latency(self) -> float:
        return np.min(self.latencies) if self.latencies else 0


class AudioStreamHandler:
    """
    Handle audio input/output streams.
    
    Supports multiple backends: sounddevice, JACK (via jackd).
    """
    
    def __init__(self, config: RealtimeConfig):
        self.config = config
        self.running = False
        self.input_buffer = Queue()
        self.output_buffer = Queue()
        self.latency_tracker = LatencyTracker()
        
        # Try to import sounddevice
        try:
            import sounddevice as sd
            self.sd = sd
            self.backend = 'sounddevice'
        except ImportError:
            self.backend = None
            print("Warning: sounddevice not available. Real-time disabled.")
    
    def list_devices(self) -> List[Dict]:
        """List available audio devices."""
        if self.backend == 'sounddevice':
            return self.sd.query_devices()
        return []
    
    def start_input(self, callback: Callable[[np.ndarray], None]):
        """Start audio input stream."""
        if self.backend != 'sounddevice':
            print("Error: sounddevice not available")
            return
        
        self.running = True
        self.input_stream = self.sd.InputStream(
            device=self.config.input_device,
            channels=1,
            samplerate=self.config.sample_rate,
            blocksize=self.config.buffer_size,
            callback=callback
        )
        self.input_stream.start()
    
    def start_output(self):
        """Start audio output stream."""
        if self.backend != 'sounddevice':
            return
        
        self.output_stream = self.sd.OutputStream(
            device=self.config.output_device,
            channels=1,
            samplerate=self.config.sample_rate,
            blocksize=self.config.buffer_size
        )
        self.output_stream.start()
    
    def stop(self):
        """Stop all streams."""
        self.running = False
        if hasattr(self, 'input_stream'):
            self.input_stream.stop()
            self.input_stream.close()
        if hasattr(self, 'output_stream'):
            self.output_stream.stop()
            self.output_stream.close()


class MIDIInputHandler:
    """
    Handle MIDI controller input for real-time parameter control.
    """
    
    def __init__(self):
        self.running = False
        self.midi_values = {}  # CC -> value
        self.parameter_mapping = {
            1: ('OUTPUT_GAIN_DB', 0, 12),   # Mod Wheel -> Gain
            7: ('OUTPUT_GAIN_DB', 0, 12),   # Volume -> Gain
            11: ('SPECTRAL_MAX_PARTIALS', 2, 32),  # Expression -> Partials
        }
        self.callbacks = []
        
        # Try to import mido
        try:
            import mido
            self.mido = mido
            self.backend = 'mido'
        except ImportError:
            self.backend = None
    
    def start(self, port_name: Optional[str] = None):
        """Start MIDI input."""
        if self.backend != 'mido':
            print("Warning: mido not available. MIDI control disabled.")
            return
        
        self.running = True
        
        # Open MIDI port
        if port_name is None:
            # Get first available input
            port_name = self.mido.get_input_names()[0] if self.mido.get_input_names() else None
        
        if port_name:
            self.port = self.mido.open_input(port_name)
            self._thread = threading.Thread(target=self._read_loop)
            self._thread.daemon = True
            self._thread.start()
    
    def _read_loop(self):
        """Read MIDI messages in loop."""
        while self.running:
            for msg in self.port:
                if msg.type == 'control_change':
                    cc = msg.control
                    value = msg.value / 127.0  # Normalize to 0-1
                    self.midi_values[cc] = value
                    
                    # Map to parameter
                    if cc in self.parameter_mapping:
                        param, min_val, max_val = self.parameter_mapping[cc]
                        actual_value = min_val + value * (max_val - min_val)
                        
                        # Notify callbacks
                        for callback in self.callbacks:
                            callback(param, actual_value)
    
    def stop(self):
        """Stop MIDI input."""
        self.running = False
        if hasattr(self, 'port'):
            self.port.close()
    
    def register_callback(self, callback: Callable[[str, float], None]):
        """Register parameter change callback."""
        self.callbacks.append(callback)
    
    def set_mapping(self, cc: int, param_name: str, min_val: float, max_val: float):
        """Set MIDI CC to parameter mapping."""
        self.parameter_mapping[cc] = (param_name, min_val, max_val)


class RealtimeProcessor:
    """
    Real-time concatenative synthesis processor.
    """
    
    def __init__(self, config: RealtimeConfig, corpus_data: Any = None):
        self.config = config
        self.corpus_data = corpus_data
        self.stream_handler = AudioStreamHandler(config)
        self.latency_tracker = LatencyTracker()
        self.midi_handler = MIDIInputHandler()
        
        # Processing state
        self.running = False
        self.output_buffer = np.array([])
        
        # Current parameter values (can be controlled via MIDI)
        self.parameters = {
            'OUTPUT_GAIN_DB': 0.0,
            'SPECTRAL_MAX_PARTIALS': 8,
            'SPECTRAL_TOLERANCE_CENTS': 50,
        }
    
    def process_buffer(self, audio: np.ndarray) -> np.ndarray:
        """
        Process an audio buffer through the spectral matching pipeline.
        
        In a full implementation, this would:
        1. Extract spectral features
        2. Match to corpus
        3. Synthesize output
        """
        # For now, pass through with gain
        gain = 10 ** (self.parameters['OUTPUT_GAIN_DB'] / 20)
        output = audio * gain
        
        # Mix with any buffered output
        if len(self.output_buffer) > 0:
            output = output + self.output_buffer[:len(output)]
        
        return output
    
    def start(self, input_callback: Optional[Callable] = None):
        """Start real-time processing."""
        self.running = True
        
        # Start MIDI
        self.midi_handler.start()
        self.midi_handler.register_callback(self._on_midi_change)
        
        # Start audio
        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"Audio callback status: {status}")
            
            # Get input audio
            audio = indata[:, 0]
            
            # Process
            start_time = time.time()
            output = self.process_buffer(audio)
            latency = (time.time() - start_time) * 1000
            self.latency_tracker.add_latency(latency)
            
            # Output (in real implementation, would write to output stream)
            if input_callback:
                input_callback(output)
        
        self.stream_handler.start_input(audio_callback)
        self.stream_handler.start_output()
        
        print(f"Real-time processing started. Target latency: {self.config.latency_target_ms}ms")
    
    def stop(self):
        """Stop real-time processing."""
        self.running = False
        self.stream_handler.stop()
        self.midi_handler.stop()
        print("Real-time processing stopped.")
    
    def _on_midi_change(self, param: str, value: float):
        """Handle MIDI parameter change."""
        self.parameters[param] = value


def process_live(corpus_path: str, 
                buffer_size: int = 512,
                latency_target_ms: int = 20,
                use_midi: bool = True):
    """
    Main entry point for live processing.
    
    Args:
        corpus_path: Path to corpus directory
        buffer_size: Audio buffer size
        latency_target_ms: Target latency
        use_midi: Enable MIDI control
    """
    config = RealtimeConfig(
        buffer_size=buffer_size,
        hop_size=buffer_size // 2,
        latency_target_ms=latency_target_ms
    )
    
    # In full implementation, load corpus here
    corpus_data = None
    
    processor = RealtimeProcessor(config, corpus_data)
    
    try:
        processor.start()
        
        # Keep running
        while processor.running:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        processor.stop()
