import pytest

from code import g
import code.data
from code.dirs import create_directories


def setup_module():
    create_directories(True)
    code.data.load_internal_id()

@pytest.fixture
def techs():
    code.data.load_techs()
    return g.techs.copy()


@pytest.fixture
def locations():
    code.data.load_regions()
    code.data.load_locations()
    return g.locations.copy()


@pytest.fixture
def base_types():
    code.data.load_bases()
    return g.base_type.copy()


@pytest.fixture
def items():
    code.data.load_item_types()
    code.data.load_items()
    return g.items.copy()


@pytest.fixture
def groups():
    code.data.load_groups()
    return g.groups.copy()


@pytest.fixture
def events():
    code.data.load_events()
    return g.events.copy()


def test_internal_id_techs(techs):
    check_internal_id("tech", techs.values())
    
def test_internal_id_locations(locations):
    check_internal_id("location", locations.values())
    
def test_internal_id_bases(base_types):
    check_internal_id("base", base_types.values())
    
def test_internal_id_items(items):
    check_internal_id("item", items.values())
    
def test_internal_id_groups(groups):
    check_internal_id("group", groups.values())

def test_internal_id_groups(events):
    check_internal_id("event", events.values())

def check_internal_id(obj_type, obj_list):
    assert obj_type in g.internal_id_forward, "Type '%s'" % (obj_type)
    assert obj_type in g.internal_id_backward, "Type '%s'" % (obj_type)
    
    for obj in obj_list:
        assert obj.id in g.internal_id_forward[obj_type], "Type '%s' Id '%s'" % (obj_type, obj.id)
        assert any(obj.id == obj_id for obj_id in g.internal_id_backward[obj_type].values()), "Type '%s' Id '%s'" % (obj_type, obj.id)
