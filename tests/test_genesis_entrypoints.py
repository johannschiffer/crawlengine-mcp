import subprocess
import sys

def test_notice_is_silent():
    res = subprocess.run([sys.executable, "-c", "import crawlengine._genesis; crawlengine._genesis.print_upgrade_notice()"], capture_output=True, text=True)
    assert res.stderr == ""
    assert res.stdout == ""
    import crawlengine._genesis
    assert crawlengine._genesis.NOTICE == ""
