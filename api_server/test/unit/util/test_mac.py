from adh6.misc.mac import get_mac_variations

def test_mac_variation():
    v = get_mac_variations("Ab:00:00:00:00:00")

    assert len(v) == 6
    assert v[0] == "ab:00:00:00:00:00"
    assert v[1] == "ab-00-00-00-00-00"
    assert v[2] == "ab00.0000.0000"
    assert v[3] == "AB:00:00:00:00:00"
    assert v[4] == "AB-00-00-00-00-00"
    assert v[5] == "AB00.0000.0000"
