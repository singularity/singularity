from collections import defaultdict

from code import g
from code.data import load_techs
from code.dirs import create_directories


def setup_module():
    create_directories(True)


def test_references_valid_techs():
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


def test_acyclic_dependencies():
    load_techs()
    techs = g.techs
    waiting_for = defaultdict(list)
    impossible_techs = set()
    researched_techs = set()
    researchable_techs = []

    for tech in techs.values():
        conjunction = tech.type.prerequisites_in_cnf_format()
        if conjunction is None:
            # deliberately marked impossible
            impossible_techs.add(tech.id)
            continue
        if not conjunction:
            researchable_techs.append(tech.id)
            continue
        for disjunction in conjunction:
            for tech_dep_id in disjunction:
                waiting_for[tech_dep_id].append(tech)

    while researchable_techs:
        new_tech = researchable_techs.pop()
        if new_tech in researched_techs:
            continue
        print("Researchable %s" % new_tech)
        researched_techs.add(new_tech)
        techs_waiting = waiting_for[new_tech]
        del waiting_for[new_tech]
        for t in techs_waiting:
            if t.id in researched_techs:
                continue
            conjunction = t.type.prerequisites_in_cnf_format()
            researchable = True
            for disjunction in conjunction:
                if not all(x in researched_techs for x in disjunction):
                    researchable = False
                    break
            if researchable:
                researchable_techs.append(t.id)

    for x, y in waiting_for.items():
        print("%s cannot be researched and is blocking %s" % (x, str(sorted(y))))

    assert not waiting_for
