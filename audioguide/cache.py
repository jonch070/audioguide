"""
AudioGuide Descriptor Caching Module

Provides caching for descriptor analysis results to avoid redundant computation.
"""

import os
import json
import hashlib
import time
import threading
from pathlib import Path
from typing import Any, Optional, Dict
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class CacheEntry:
    """Represents a cached descriptor entry."""
    key: str
    file_path: str
    analysis_params: str  # JSON of params
    result_data: str  # JSON of results
    created_at: float
    expires_at: float
    size_bytes: int


class DescriptorCache:
    """
    Thread-safe descriptor cache with TTL and size limits.
    """
    
    def __init__(self, cache_dir: str = '.audioguide_cache', 
                 max_size_gb: float = 10.0, 
                 ttl_days: int = 30):
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = int(max_size_gb * 1024 * 1024 * 1024)
        self.ttl_seconds = ttl_days * 24 * 60 * 60
        self._lock = threading.RLock()
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Index file
        self.index_file = self.cache_dir / 'index.json'
        self._index: Dict[str, CacheEntry] = {}
        self._load_index()
    
    def _load_index(self):
        """Load cache index from disk."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                    for key, entry in data.items():
                        self._index[key] = CacheEntry(**entry)
            except Exception:
                pass  # Start fresh if index corrupted
    
    def _save_index(self):
        """Save cache index to disk."""
        with self._lock:
            data = {k: asdict(v) for k, v in self._index.items()}
            with open(self.index_file, 'w') as f:
                json.dump(data, f)
    
    def compute_key(self, file_path: str, analysis_params: Dict) -> str:
        """Compute cache key from file path and parameters."""
        # Include file modification time for invalidation
        mtime = os.path.getmtime(file_path) if os.path.exists(file_path) else 0
        
        key_data = f"{file_path}:{mtime}:{json.dumps(analysis_params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve cached value."""
        with self._lock:
            if key not in self._index:
                return None
            
            entry = self._index[key]
            
            # Check expiration
            if time.time() > entry.expires_at:
                del self._index[key]
                self._save_index()
                return None
            
            # Load result data
            result_file = self.cache_dir / f"{key}.json"
            if not result_file.exists():
                del self._index[key]
                return None
            
            try:
                with open(result_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return None
    
    def set(self, key: str, value: Any, file_path: str = '', analysis_params: Dict = None):
        """Store value in cache."""
        with self._lock:
            # Serialize value
            value_json = json.dumps(value, default=str)
            value_bytes = value_json.encode()
            
            # Check size limit
            total_size = sum(
                os.path.getsize(self.cache_dir / f"{k}.json") 
                for k in self._index 
                if (self.cache_dir / f"{k}.json").exists()
            )
            
            if total_size + len(value_bytes) > self.max_size_bytes:
                self._evict_oldest()
            
            # Write result file
            result_file = self.cache_dir / f"{key}.json"
            with open(result_file, 'w') as f:
                f.write(value_json)
            
            # Update index
            now = time.time()
            entry = CacheEntry(
                key=key,
                file_path=file_path,
                analysis_params=json.dumps(analysis_params, sort_keys=True) if analysis_params else '',
                result_data='',
                created_at=now,
                expires_at=now + self.ttl_seconds,
                size_bytes=len(value_bytes)
            )
            self._index[key] = entry
            self._save_index()
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is valid."""
        return self.get(key) is not None
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            for key in list(self._index.keys()):
                result_file = self.cache_dir / f"{key}.json"
                if result_file.exists():
                    result_file.unlink()
            self._index.clear()
            self._save_index()
    
    def clear_expired(self):
        """Remove expired entries."""
        with self._lock:
            now = time.time()
            expired = [k for k, v in self._index.items() if now > v.expires_at]
            
            for key in expired:
                result_file = self.cache_dir / f"{key}.json"
                if result_file.exists():
                    result_file.unlink()
                del self._index[key]
            
            if expired:
                self._save_index()
    
    def _evict_oldest(self):
        """Evict oldest entries to make space."""
        if not self._index:
            return
        
        # Sort by creation time
        sorted_keys = sorted(self._index.keys(), key=lambda k: self._index[k].created_at)
        
        # Remove oldest until under limit
        target_size = self.max_size_bytes * 0.8  # Target 80% of max
        current_size = sum(
            os.path.getsize(self.cache_dir / f"{k}.json")
            for k in sorted_keys
            if (self.cache_dir / f"{k}.json").exists()
        )
        
        for key in sorted_keys:
            if current_size <= target_size:
                break
            
            result_file = self.cache_dir / f"{key}.json"
            if result_file.exists():
                current_size -= result_file.stat().st_size
                result_file.unlink()
            del self._index[key]
        
        self._save_index()
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        with self._lock:
            total_size = sum(
                os.path.getsize(self.cache_dir / f"{k}.json")
                for k in self._index
                if (self.cache_dir / f"{k}.json").exists()
            )
            
            expired = sum(1 for v in self._index.values() if time.time() > v.expires_at)
            
            return {
                'entries': len(self._index),
                'total_size_mb': total_size / (1024 * 1024),
                'max_size_gb': self.max_size_bytes / (1024**3),
                'expired': expired,
                'cache_dir': str(self.cache_dir)
            }


# Global cache instance
_global_cache: Optional[DescriptorCache] = None


def get_cache() -> DescriptorCache:
    """Get global cache instance."""
    global _global_cache
    if _global_cache is None:
        from audioguide import defaults
        _global_cache = DescriptorCache(
            cache_dir=defaults.CACHE_DIR,
            max_size_gb=defaults.CACHE_MAX_SIZE_GB,
            ttl_days=defaults.CACHE_TTL_DAYS
        )
    return _global_cache


def clear_cache():
    """Clear the global cache."""
    get_cache().clear()


def cache_stats() -> Dict:
    """Get cache statistics."""
    return get_cache().get_stats()
