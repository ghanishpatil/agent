"""Challenge-specific solver modules"""

import logging
from typing import Dict, Optional, TYPE_CHECKING

# Lazy imports to avoid circular dependency
if TYPE_CHECKING:
    from .base import BaseModule


class ModuleRegistry:
    """Registry for challenge solver modules"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('md-exploit-engine.modules')
        self._modules: Dict[str, 'BaseModule'] = {}
        self._flag_handler = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy initialization of modules"""
        if self._initialized:
            return
        
        # Import modules here to avoid circular imports
        from .base import BaseModule
        from .web import WebModule
        from .crypto import CryptoModule
        from .pwn import PwnModule
        from .reversing import ReversingModule
        from .forensics import ForensicsModule
        from .osint import OSINTModule
        from .flag_handler import FlagHandler
        
        self._flag_handler = FlagHandler(self.config)
        
        module_classes = {
            'web': WebModule,
            'crypto': CryptoModule,
            'pwn': PwnModule,
            'reversing': ReversingModule,
            'forensics': ForensicsModule,
            'osint': OSINTModule,
            'misc': CryptoModule,
        }
        
        for category, module_class in module_classes.items():
            if self.config.get(f'modules.{category}.enabled', True):
                try:
                    self._modules[category] = module_class(self.config)
                    self.logger.info(f"Loaded module: {category}")
                except Exception as e:
                    self.logger.error(f"Failed to load module {category}: {e}")
        
        self._initialized = True
    
    @property
    def flag_handler(self):
        self._ensure_initialized()
        return self._flag_handler
    
    def get_module(self, category: str) -> Optional['BaseModule']:
        """Get module for category"""
        self._ensure_initialized()
        aliases = {
            'rev': 'reversing',
            'reverse': 'reversing',
            'binary': 'pwn',
            'exploitation': 'pwn',
            'stego': 'forensics',
            'steganography': 'forensics',
            'network': 'forensics',
            'recon': 'osint',
        }
        category = aliases.get(category.lower(), category.lower())
        return self._modules.get(category)
    
    def list_modules(self) -> list:
        """List all loaded modules"""
        self._ensure_initialized()
        return list(self._modules.keys())
    
    def get_all_modules(self) -> Dict[str, 'BaseModule']:
        """Get all loaded modules"""
        self._ensure_initialized()
        return self._modules.copy()


__all__ = ['ModuleRegistry']
