"""
Unit tests for ProxyPool.
"""
from crawlengine.core.proxy_pool import ProxyPool

def test_proxy_pool_rotation_and_ejection():
    proxies = ["http://proxy1:8080", "http://proxy2:8080"]
    pool = ProxyPool(proxies)

    p1 = pool.get_proxy()
    p2 = pool.get_proxy()
    assert p1 != p2

    # Report failures on proxy1 to trigger ejection
    pool.report_failure(p1)
    pool.report_failure(p1)
    pool.report_failure(p1)

    stats = pool.get_stats()
    assert stats["ejected_count"] == 1
    assert stats["healthy_count"] == 1

    # Next proxy requested should be the remaining healthy proxy
    next_p = pool.get_proxy()
    assert next_p == p2
