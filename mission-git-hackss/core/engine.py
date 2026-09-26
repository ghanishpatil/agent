"""Main exploit engine orchestrator with advanced capabilities"""

import logging
import time
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, TimeoutError, as_completed
from dataclasses import dataclass
import threading

from .config import Config
from .challenge import Challenge, ChallengeResult
from .classifier import ChallengeClassifier
from modules import ModuleRegistry


@dataclass
class SolveAttempt:
    """Track a solve attempt"""
    module_name: str
    start_time: float
    end_time: Optional[float] = None
    success: bool = False
    flag: Optional[str] = None
    error: Optional[str] = None


class ExploitEngine:
    """Advanced engine for automated CTF challenge solving with parallel execution"""
    
    def __init__(self, config: Config, threads: int = 4, timeout: int = 300):
        self.config = config
        self.threads = threads
        self.timeout = timeout
        self.logger = logging.getLogger('md-exploit-engine.engine')
        
        # Initialize components
        self.classifier = ChallengeClassifier(config)
        self.module_registry = ModuleRegistry(config)
        
        # Statistics tracking
        self.stats = {
            'total_attempts': 0,
            'successful_solves': 0,
            'failed_solves': 0,
            'timeouts': 0,
            'total_time': 0.0,
            'flags_found': [],
            'methods_used': {},
        }
        
        # Callbacks
        self._on_flag_found: List[Callable] = []
        self._on_progress: List[Callable] = []
        
        self.logger.info(f"Engine initialized with {threads} threads, {timeout}s timeout")
    
    def solve_challenge(self, challenge_path: str, category: Optional[str] = None,
                       parallel: bool = False) -> ChallengeResult:
        """
        Solve a CTF challenge with optional parallel module execution
        
        Args:
            challenge_path: Path to challenge file or directory
            category: Optional category override
            parallel: Try multiple modules in parallel
        
        Returns:
            ChallengeResult with solving outcome
        """
        start_time = time.time()
        self.stats['total_attempts'] += 1
        
        try:
            # Parse challenge
            challenge = self._parse_challenge(challenge_path)
            self.logger.info(f"Solving challenge: {challenge.name}")
            
            # Classify if category not provided
            if category:
                challenge.category = category
            elif not challenge.category:
                challenge.category = self.classifier.classify(challenge)
            
            self.logger.info(f"Challenge category: {challenge.category}")
            
            if parallel:
                result = self._solve_parallel(challenge)
            else:
                result = self._solve_sequential(challenge)
            
            result.duration = time.time() - start_time
            self._update_stats(result)
            
            return result
        
        except Exception as e:
            self.logger.exception(f"Error solving challenge: {e}")
            self.stats['failed_solves'] += 1
            return ChallengeResult(
                challenge=Challenge(name=str(challenge_path)),
                success=False,
                error=str(e),
                duration=time.time() - start_time
            )
    
    def _solve_sequential(self, challenge: Challenge) -> ChallengeResult:
        """Solve using single module sequentially"""
        module = self.module_registry.get_module(challenge.category)
        if not module:
            return ChallengeResult(
                challenge=challenge,
                success=False,
                error=f"No module available for category: {challenge.category}"
            )
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(module.solve, challenge)
            try:
                result = future.result(timeout=self.timeout)
                return result
            except TimeoutError:
                self.stats['timeouts'] += 1
                return ChallengeResult(
                    challenge=challenge,
                    success=False,
                    error=f"Timeout after {self.timeout}s"
                )
    
    def _solve_parallel(self, challenge: Challenge) -> ChallengeResult:
        """Try multiple modules in parallel"""
        modules = self.module_registry.get_all_modules()
        
        # Prioritize the classified category
        priority_module = modules.get(challenge.category)
        other_modules = {k: v for k, v in modules.items() if k != challenge.category}
        
        results = []
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {}
            
            # Submit priority module first
            if priority_module:
                futures[executor.submit(priority_module.solve, challenge)] = challenge.category
            
            # Submit other modules
            for category, module in other_modules.items():
                futures[executor.submit(module.solve, challenge)] = category
            
            # Wait for first successful result or all to complete
            for future in as_completed(futures, timeout=self.timeout):
                category = futures[future]
                try:
                    result = future.result(timeout=5)
                    results.append((category, result))
                    
                    if result.success and result.flag:
                        self.logger.info(f"Flag found by {category} module")
                        # Cancel remaining futures
                        for f in futures:
                            f.cancel()
                        return result
                except TimeoutError:
                    self.logger.warning(f"Module {category} timed out")
                except Exception as e:
                    self.logger.warning(f"Module {category} failed: {e}")
        
        # Return best result (prioritize partial success)
        for category, result in results:
            if result.success:
                return result
        
        # Return first result with logs
        if results:
            return results[0][1]
        
        return ChallengeResult(
            challenge=challenge,
            success=False,
            error="All modules failed"
        )
    
    def solve_batch(self, challenge_paths: List[str], category: Optional[str] = None,
                   parallel: bool = True) -> List[ChallengeResult]:
        """Solve multiple challenges in batch"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {
                executor.submit(self.solve_challenge, path, category, False): path
                for path in challenge_paths
            }
            
            for future in as_completed(futures):
                path = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result.success:
                        self.logger.info(f"Solved: {path} -> {result.flag}")
                        self._notify_flag_found(result)
                except Exception as e:
                    self.logger.error(f"Failed: {path} -> {e}")
                    results.append(ChallengeResult(
                        challenge=Challenge(name=path),
                        success=False,
                        error=str(e)
                    ))
        
        return results
    
    def _parse_challenge(self, challenge_path: str) -> Challenge:
        """Parse challenge from path with enhanced detection"""
        path = Path(challenge_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Challenge not found: {challenge_path}")
        
        # Basic challenge parsing
        challenge = Challenge(
            name=path.stem,
            files=[path] if path.is_file() else list(path.glob('*'))
        )
        
        # Try to extract metadata from various sources
        if path.is_dir():
            # Check for description files
            desc_files = ['description.txt', 'README.md', 'readme.txt', 'challenge.txt', 'info.txt']
            for desc_file in desc_files:
                desc_path = path / desc_file
                if desc_path.exists():
                    challenge.description = desc_path.read_text(errors='ignore')
                    break
            
            # Check for connection info
            conn_files = ['connection.txt', 'nc.txt', 'server.txt']
            for conn_file in conn_files:
                conn_path = path / conn_file
                if conn_path.exists():
                    conn_info = conn_path.read_text(errors='ignore')
                    # Parse host:port
                    import re
                    match = re.search(r'(\S+)\s+(\d+)', conn_info)
                    if match:
                        challenge.host = match.group(1)
                        challenge.port = int(match.group(2))
                    break
            
            # Check for URL
            url_files = ['url.txt', 'website.txt', 'target.txt']
            for url_file in url_files:
                url_path = path / url_file
                if url_path.exists():
                    challenge.url = url_path.read_text(errors='ignore').strip()
                    break
        
        return challenge
    
    def _update_stats(self, result: ChallengeResult):
        """Update statistics after solve attempt"""
        self.stats['total_time'] += result.duration or 0
        
        if result.success:
            self.stats['successful_solves'] += 1
            if result.flag:
                self.stats['flags_found'].append(result.flag)
            if result.method:
                self.stats['methods_used'][result.method] = \
                    self.stats['methods_used'].get(result.method, 0) + 1
        else:
            self.stats['failed_solves'] += 1
    
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            **self.stats,
            'success_rate': (self.stats['successful_solves'] / max(1, self.stats['total_attempts'])) * 100,
            'avg_time': self.stats['total_time'] / max(1, self.stats['total_attempts']),
        }
    
    def on_flag_found(self, callback: Callable):
        """Register callback for when flag is found"""
        self._on_flag_found.append(callback)
    
    def on_progress(self, callback: Callable):
        """Register callback for progress updates"""
        self._on_progress.append(callback)
    
    def _notify_flag_found(self, result: ChallengeResult):
        """Notify callbacks when flag is found"""
        for callback in self._on_flag_found:
            try:
                callback(result)
            except Exception as e:
                self.logger.warning(f"Callback error: {e}")
    
    def _notify_progress(self, message: str, progress: float):
        """Notify callbacks of progress"""
        for callback in self._on_progress:
            try:
                callback(message, progress)
            except Exception as e:
                self.logger.warning(f"Callback error: {e}")
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'total_attempts': 0,
            'successful_solves': 0,
            'failed_solves': 0,
            'timeouts': 0,
            'total_time': 0.0,
            'flags_found': [],
            'methods_used': {},
        }
