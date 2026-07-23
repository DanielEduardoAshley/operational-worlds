from ow import Primitive, World

def test_add():
    w=World()
    w.add(Primitive(id="OW01",name="Establish",geometry="Circle"))
    assert len(w)==1
