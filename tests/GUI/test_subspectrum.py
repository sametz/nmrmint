from nmrmint.GUI.history import Subspectrum


def test_subspectrum_instantiated_inactive():
    ss = Subspectrum()
    assert not ss.active


def test_subspectrum_toggle_true():
    ss = Subspectrum()
    ss.toggle_active()
    assert ss.active

    
def test_subspectrum_toggle_false():
    ss = Subspectrum(activity=True)
    assert ss.active
    ss.toggle_active()
    assert not ss.active
