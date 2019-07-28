from code import g
from code.data import load_techs
from code.dirs import create_directories


def setup_module():
    create_directories(True)


def test_reseachable():
    load_techs()
    techs = g.techs
    for tech in techs.values():
        conjunction = tech.type.prerequisites_in_cnf_format()
        if conjunction is None:
            # deliberately marked impossible
            continue
        for disjunction in conjunction:
            for tech_dep_id in disjunction:
                assert '|' not in tech_dep_id, 'Tech "%s" references unknown dependency tech "%s" (' \
                                               'did you use pre instead of pre_list?)' % (tech.id, tech_dep_id)
                assert tech_dep_id in techs, 'Tech "%s" references unknown dependency tech "%s"' % (
                    tech.id, tech_dep_id)
            for keyword in ('impossible', 'OR'):
                assert keyword not in disjunction, 'The keyword "%s" must be the first in a pre_list (Tech: "%s")' % (
                    keyword, tech.id
                )
