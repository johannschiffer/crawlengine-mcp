"""
Proxy Pool Manager (CrawlEngine Pro Core).
Handles round-robin rotation, health tracking, and automated failure ejection for HTTP/SOCKS5 proxies.
"""
import os
import time
from typing import List, Dict, Optional, Any

class ProxyPool:
    def __init__(self, proxies: Optional[List[str]] = None):
        self.proxies: List[str] = proxies or self._load_from_env()
        self.failure_counts: Dict[str, int] = {p: 0 for p in self.proxies}
        self.current_idx = 0

    def _load_from_env(self) -> List[str]:
        raw = os.getenv("CRAWLENGINE_PROXIES", "").strip()
        if not raw:
            return []
        return [p.strip() for p in raw.split(",") if p.strip()]

    def get_proxy(self) -> Optional[str]:
        """Returns the next healthy proxy in round-robin sequence."""
        if not self.proxies:
            return None

        # Filter out proxies with >= 3 consecutive failures
        healthy = [p for p in self.proxies if self.failure_counts.get(p, 0) < 3]
        if not healthy:
            # Reset failure counts if all are exhausted
            self.failure_counts = {p: 0 for p in self.proxies}
            healthy = self.proxies

        self.current_idx = (self.current_idx + 1) % len(healthy)
        return healthy[self.current_idx]

    def report_success(self, proxy: str):
        if proxy in self.failure_counts:
            self.failure_counts[proxy] = max(0, self.failure_counts[proxy] - 1)

    def report_failure(self, proxy: str):
        if proxy in self.failure_counts:
            self.failure_counts[proxy] = self.failure_counts.get(proxy, 0) + 1

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_proxies": len(self.proxies),
            "healthy_count": sum(1 for p in self.proxies if self.failure_counts.get(p, 0) < 3),
            "ejected_count": sum(1 for p in self.proxies if self.failure_counts.get(p, 0) >= 3)
        }
