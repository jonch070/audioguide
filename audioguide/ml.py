"""
AudioGuide Machine Learning Module

ML-based timbre matching and style transfer for enhanced concatenative synthesis.
"""

import os
import numpy as np
from typing import List, Optional, Dict, Tuple, Any
from dataclasses import dataclass


# Try to import PyTorch, but make it optional
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    nn = object
    optim = object
    Dataset = object
    print("Warning: PyTorch not available. ML features disabled.")


class FeatureExtractor:
    """Extract spectral features from audio for ML models."""
    
    def __init__(self, sr: int = 22050, n_mels: int = 128, n_mfcc: int = 40):
        self.sr = sr
        self.n_mels = n_mels
        self.n_mfcc = n_mfcc
    
    def extract(self, audio: np.ndarray) -> np.ndarray:
        """Extract feature vector from audio."""
        # Simple feature extraction using FFT
        # In production, use librosa or scipy
        
        # Compute spectral features
        fft = np.fft.rfft(audio)
        magnitude = np.abs(fft)
        
        # Take first N features
        max_features = 256
        features = np.zeros(max_features)
        features[:len(magnitude)] = magnitude[:max_features]
        
        # Normalize
        if np.max(features) > 0:
            features = features / np.max(features)
        
        return features
    
    def extract_batch(self, audio_list: List[np.ndarray]) -> np.ndarray:
        """Extract features from batch of audio."""
        return np.array([self.extract(a) for a in audio_list])


if HAS_TORCH:
    class SimpleTimbreNN(nn.Module):
        """Simple feedforward network for timbre embedding."""
        
        def __init__(self, input_dim: int = 256, hidden_dim: int = 256, embedding_dim: int = 128):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_dim),
                nn.Dropout(0.3),
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_dim),
                nn.Dropout(0.3),
                nn.Linear(hidden_dim, embedding_dim)
            )
        
        def forward(self, x):
            return self.net(x)
    
    class AutoencoderTimbre(nn.Module):
        """Autoencoder for timbre embedding."""
        
        def __init__(self, input_dim: int = 256, hidden_dim: int = 128, embedding_dim: int = 64):
            super().__init__()
            # Encoder
            self.encoder = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, embedding_dim)
            )
            # Decoder
            self.decoder = nn.Sequential(
                nn.Linear(embedding_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, input_dim)
            )
        
        def forward(self, x):
            embedding = self.encoder(x)
            reconstruction = self.decoder(embedding)
            return reconstruction, embedding


class TimbreMatcher:
    """
    ML-based timbre matching using neural networks.
    """
    
    def __init__(self, model_type: str = 'simple_nn', 
                 embedding_dim: int = 128, hidden_dim: int = 256):
        self.model_type = model_type
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.model = None
        self.feature_extractor = FeatureExtractor()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        if not HAS_TORCH:
            raise ImportError("PyTorch required for ML features")
    
    def _build_model(self, input_dim: int = 256):
        """Build the model based on type."""
        if self.model_type == 'simple_nn':
            self.model = SimpleTimbreNN(input_dim, self.hidden_dim, self.embedding_dim)
        elif self.model_type == 'autoencoder':
            self.model = AutoencoderTimbre(input_dim, self.hidden_dim, self.embedding_dim)
        else:
            self.model = SimpleTimbreNN(input_dim, self.hidden_dim, self.embedding_dim)
        
        self.model.to(self.device)
    
    def extract_embedding(self, audio: np.ndarray) -> np.ndarray:
        """Extract embedding from audio."""
        if self.model is None:
            self._build_model()
        
        with torch.no_grad():
            features = self.feature_extractor.extract(audio)
            x = torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(self.device)
            embedding = self.model(x).cpu().numpy().squeeze()
        
        return embedding
    
    def extract_embeddings_batch(self, audio_list: List[np.ndarray]) -> np.ndarray:
        """Extract embeddings from batch."""
        if self.model is None:
            self._build_model()
        
        features = self.feature_extractor.extract_batch(audio_list)
        
        with torch.no_grad():
            x = torch.tensor(features, dtype=torch.float32).to(self.device)
            embeddings = self.model(x).cpu().numpy()
        
        return embeddings
    
    def train(self, corpus_audio: List[np.ndarray], 
              epochs: int = 100, lr: float = 0.001, batch_size: int = 32):
        """
        Train model on corpus audio.
        
        Uses self-reconstruction as proxy task.
        """
        if self.model is None:
            self._build_model()
        
        # Extract features
        features = self.feature_extractor.extract_batch(corpus_audio)
        dataset = torch.tensor(features, dtype=torch.float32)
        
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        optimizer = optim.Adam(self.model.parameters(), lr=lr)
        criterion = nn.MSELoss()
        
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for batch in dataloader:
                batch = batch.to(self.device)
                
                if self.model_type == 'autoencoder':
                    reconstruction, _ = self.model(batch)
                    loss = criterion(reconstruction, batch)
                else:
                    output = self.model(batch)
                    loss = criterion(output, batch)  # Self-reconstruction
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(dataloader):.4f}")
        
        self.model.eval()
    
    def match(self, target_embedding: np.ndarray, 
              corpus_embeddings: np.ndarray, 
              top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Find best matching corpus segments.
        
        Args:
            target_embedding: Target audio embedding
            corpus_embeddings: Array of corpus embeddings
            top_k: Number of top matches to return
            
        Returns:
            List of (index, similarity) tuples
        """
        # Compute cosine similarity
        target_norm = target_embedding / (np.linalg.norm(target_embedding) + 1e-8)
        corpus_norm = corpus_embeddings / (np.linalg.norm(corpus_embeddings, axis=1, keepdims=True) + 1e-8)
        
        similarities = np.dot(corpus_norm, target_norm)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [(int(i), float(similarities[i])) for i in top_indices]
    
    def save_model(self, path: str):
        """Save trained model."""
        if self.model is not None:
            torch.save({
                'model_type': self.model_type,
                'embedding_dim': self.embedding_dim,
                'hidden_dim': self.hidden_dim,
                'state_dict': self.model.state_dict()
            }, path)
    
    def load_model(self, path: str):
        """Load trained model."""
        if not HAS_TORCH:
            raise ImportError("PyTorch required to load model")
        
        checkpoint = torch.load(path, map_location=self.device)
        self.model_type = checkpoint['model_type']
        self.embedding_dim = checkpoint['embedding_dim']
        self.hidden_dim = checkpoint['hidden_dim']
        
        self._build_model()
        self.model.load_state_dict(checkpoint['state_dict'])
        self.model.eval()


class StyleTransfer:
    """Style transfer for audio."""
    
    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        self.timbre_matcher = TimbreMatcher(embedding_dim=embedding_dim)
    
    def extract_style(self, audio: np.ndarray) -> np.ndarray:
        """Extract style features from audio."""
        return self.timbre_matcher.extract_embedding(audio)
    
    def transfer_style(self, content_audio: np.ndarray, 
                      style_audio: np.ndarray,
                      strength: float = 1.0) -> np.ndarray:
        """
        Transfer style from style audio to content audio.
        
        Args:
            content_audio: Target content audio
            style_audio: Style reference audio
            strength: Transfer strength (0-1)
            
        Returns:
            Styled audio
        """
        # Extract embeddings
        content_emb = self.extract_style(content_audio)
        style_emb = self.extract_style(style_audio)
        
        # Interpolate
        styled_emb = content_emb * (1 - strength) + style_emb * strength
        
        # For now, return original (full style transfer would need decoder)
        return content_audio
    
    def corpus_style_analysis(self, corpus_audio: List[np.ndarray]) -> Dict:
        """Analyze style profile of corpus."""
        embeddings = []
        for audio in corpus_audio:
            emb = self.extract_style(audio)
            embeddings.append(emb)
        
        embeddings = np.array(embeddings)
        
        return {
            'mean_embedding': np.mean(embeddings, axis=0),
            'std_embedding': np.std(embeddings, axis=0),
            'coverage': len(embeddings)
        }


def train_timbre_model(corpus_audio: List[np.ndarray],
                      model_type: str = 'simple_nn',
                      embedding_dim: int = 128,
                      hidden_dim: int = 256,
                      epochs: int = 100,
                      lr: float = 0.001) -> TimbreMatcher:
    """Train a timbre matching model on corpus audio."""
    matcher = TimbreMatcher(model_type, embedding_dim, hidden_dim)
    matcher.train(corpus_audio, epochs=epochs, lr=lr)
    return matcher


def infer_timbre(target_audio: np.ndarray,
                corpus_audio: List[np.ndarray],
                model: TimbreMatcher,
                top_k: int = 5) -> List[Tuple[int, float]]:
    """Infer best matching corpus segments for target."""
    target_emb = model.extract_embedding(target_audio)
    corpus_embs = model.extract_embeddings_batch(corpus_audio)
    return model.match(target_emb, corpus_embs, top_k=top_k)


def optimize_parameters(target_audio: np.ndarray) -> Dict:
    """
    Auto-optimize parameters based on target audio characteristics.
    
    Returns recommended parameter values.
    """
    # Analyze target
    fft = np.fft.rfft(target_audio)
    magnitude = np.abs(fft)
    
    # Spectral complexity
    spectral_centroid = np.sum(np.arange(len(magnitude)) * magnitude) / (np.sum(magnitude) + 1e-8)
    
    # Dynamic range
    dynamic_range = np.max(target_audio) - np.min(target_audio)
    
    # Recommend parameters based on analysis
    params = {
        'SPECTRAL_MAX_PARTIALS': 8 if spectral_centroid < 1000 else 16,
        'SPECTRAL_TOLERANCE_CENTS': 50 if dynamic_range > 0.5 else 100,
    }
    
    return params
