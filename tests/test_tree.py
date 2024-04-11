from jmullan.tree import tree


def test_valid_name():
    assert not tree.valid_name(None)
    assert not tree.valid_name("__foo__")
    assert not tree.valid_name("__foo__.py")
    assert not tree.valid_name(".foo")
    assert tree.valid_name("__foo")
    assert tree.valid_name("foo__")
    assert tree.valid_name("foo")
