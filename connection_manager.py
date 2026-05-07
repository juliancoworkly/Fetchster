"""
Connection Management for Large Search Operations
Prevents timeouts and handles connection issues gracefully
"""

import time
import requests
from typing import Callable, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ConnectionManager:
    """Manages connections and prevents timeouts during large operations"""
    
    def __init__(self):
        self.session = self._create_robust_session()
    
    def _create_robust_session(self):
        """Create a session with robust retry and timeout settings"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"]
        )
        
        # Mount adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set reasonable timeouts
        session.timeout = (5, 10)  # (connect, read)
        
        return session
    
    def execute_with_retry(self, func: Callable, *args, max_retries: int = 2, **kwargs) -> Any:
        """Execute a function with retry logic"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 0.5 * (attempt + 1)
                    time.sleep(wait_time)
                    print(f"Retry attempt {attempt + 1} after error: {str(e)}")
        
        # If all retries failed, raise the last error
        raise last_error
    
    def batch_process(self, items: list, process_func: Callable, batch_size: int = 5, delay: float = 0.1):
        """Process items in batches to prevent connection overload"""
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            for item in batch:
                try:
                    result = self.execute_with_retry(process_func, item)
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"Failed to process item after retries: {str(e)}")
                    continue
            
            # Small delay between batches
            if i + batch_size < len(items):
                time.sleep(delay)
        
        return results


# Global connection manager instance
connection_manager = ConnectionManager()