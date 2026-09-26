"""Challenge representation and result handling"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime


@dataclass
class Challenge:
    """Represents a CTF challenge"""
    
    name: str
    category: Optional[str] = None
    description: str = ""
    points: int = 0
    files: List[Path] = field(default_factory=list)
    url: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    hints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize challenge data"""
        if self.category:
            self.category = self.category.lower()
    
    @property
    def has_files(self) -> bool:
        return len(self.files) > 0
    
    @property
    def has_connection(self) -> bool:
        return self.host is not None and self.port is not None
    
    @property
    def has_url(self) -> bool:
        return self.url is not None


@dataclass
class ChallengeResult:
    """Result of challenge solving attempt"""
    
    challenge: Challenge
    success: bool
    flag: Optional[str] = None
    error: Optional[str] = None
    method: Optional[str] = None
    duration: float = 0.0
    attempts: int = 0
    logs: List[str] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def add_log(self, message: str):
        """Add log message"""
        self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'challenge_name': self.challenge.name,
            'category': self.challenge.category,
            'success': self.success,
            'flag': self.flag,
            'error': self.error,
            'method': self.method,
            'duration': self.duration,
            'attempts': self.attempts,
            'timestamp': self.timestamp.isoformat(),
            'logs': self.logs
        }
