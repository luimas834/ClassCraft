"""Tests for the independent validator of the hard rules H1 to H9."""

from dataclasses import replace
from pathlib import Path

from solver import validator
from solver.loader_json import load_problem
from solver.problem import Audience, Division, Group, Placement, Problem
from solver.validator import validate

FIXTURES = Path(__file__).parent.parent / "fixtures"
IUT_DATA = Path(__file__).parents[2] / "app" / "seed_data" / "iut_cse.json"


def _tiny() -> tuple[Problem, list[Placement]]:
    """The tiny instance together with the hand-checked answer it carries."""
    return load_problem(FIXTURES / "tiny.json")


def _with_card(problem: Problem, card_id: str, **changes: object) -> Problem:
    """A copy of the problem in which one card is replaced."""
    cards = tuple(
        replace(card, **changes) if card.id == card_id else card for card in problem.cards
    )
    return replace(problem, cards=cards)


def _with_second_division(problem: Problem) -> Problem:
    """Class X gains a second division, so a clash across divisions is possible."""
    student_class = problem.classes[0]
    divisions = (
        student_class.divisions[0],
        Division(id="X-D2", groups=(Group(id="Arabic", name="Arabic"),)),
    )
    return replace(problem, classes=(replace(student_class, divisions=divisions),))


def _moved(placements: list[Placement], card_id: str, **changes: object) -> list[Placement]:
    """A copy of the placements in which one card has moved."""
    return [replace(item, **changes) if item.card_id == card_id else item for item in placements]


def _rules(found: list[validator.Violation]) -> list[str]:
    """The rule codes of the violations, so a test can name the one it expects."""
    return sorted(item.rule for item in found)


def test_the_current_iut_routine_has_no_violations():
    problem, placements = load_problem(IUT_DATA)

    assert validate(problem, placements, problem.settings) == []


def test_the_medium_instance_has_no_violations():
    problem, placements = load_problem(FIXTURES / "medium.json")

    assert validate(problem, placements, problem.settings) == []


def test_the_tiny_expected_answer_has_no_violations():
    problem, placements = _tiny()

    assert validate(problem, placements, problem.settings) == []


def test_h1_reports_a_card_that_is_not_placed():
    problem, placements = _tiny()
    without_c5 = [item for item in placements if item.card_id != "C5"]

    found = validate(problem, without_c5, problem.settings)

    assert _rules(found) == ["H1"]
    assert found[0].card_ids == ("C5",)
    assert found[0].text == "Course 5 for Class X A is not placed."


def test_h1_reports_a_card_that_is_placed_twice():
    problem, placements = _tiny()
    doubled = placements + [item for item in placements if item.card_id == "C5"]

    found = validate(problem, doubled, problem.settings)

    assert _rules(found) == ["H1"]
    assert found[0].text == "Course 5 for Class X A is placed more than once."


def test_h2_refuses_a_two_period_lesson_that_runs_past_the_day():
    problem, placements = _tiny()
    moved = _moved(placements, "C2", start_period=4)

    found = validate(problem, moved, problem.settings)

    assert _rules(found) == ["H2"]
    assert found[0].text == "Course 2 for Class X B cannot start at period 4."


def test_h3_reports_a_teacher_who_is_in_two_places():
    problem, placements = _tiny()
    moved = _moved(placements, "C4", start_period=1)

    found = validate(problem, moved, problem.settings)

    assert _rules(found) == ["H3"]
    assert found[0].card_ids == ("C3", "C4")
    assert found[0].text == "T2 teaches Course 3 and Course 4 at the same time (Tue, period 1)."


def test_h4_reports_a_room_that_holds_two_lessons():
    problem, placements = _tiny()
    # C4 loses its teacher and takes the classroom pool, so only the room can break.
    problem = _with_card(problem, "C4", teachers=(), room_group="CLASSROOM")
    moved = _moved(placements, "C4", start_period=1, room="R1")

    found = validate(problem, moved, problem.settings)

    assert _rules(found) == ["H4"]
    assert found[0].text == "R1 holds Course 3 and Course 4 at the same time (Tue, period 1)."


def test_h5_reports_one_group_with_two_lessons_at_once():
    problem, placements = _tiny()
    # C4 joins group A and loses its teacher, so only the group rule can break.
    problem = _with_card(problem, "C4", teachers=(), audiences=(Audience("X", "A"),))
    moved = _moved(placements, "C4", start_period=3)

    found = validate(problem, moved, problem.settings)

    assert _rules(found) == ["H5"]
    assert found[0].text == "Class X has Course 4 and Course 5 at the same time (Tue, period 3)."


def test_h6_refuses_a_lab_lesson_in_a_classroom():
    problem, placements = _tiny()
    moved = _moved(placements, "C4", room="R1")

    found = validate(problem, moved, problem.settings)

    assert _rules(found) == ["H6"]
    assert found[0].text == "Course 4 for Class X B is in R1, which is not allowed for it."


def test_h7_reports_a_fixed_card_that_sits_elsewhere():
    problem, placements = _tiny()
    problem = _with_card(problem, "C1", fixed_period=3)

    found = validate(problem, placements, problem.settings)

    assert _rules(found) == ["H7"]
    assert found[0].text == (
        "Course 1 for Class X A is fixed on Mon, period 3, but is placed elsewhere."
    )


def test_h8_refuses_a_teacher_on_a_day_off():
    problem, placements = _tiny()
    moved = _moved(placements, "C4", day="Mon", start_period=1)

    found = validate(problem, moved, problem.settings)

    assert _rules(found) == ["H8"]
    assert found[0].text == "T2 is not available on Mon, period 1, but teaches Course 4."


def test_h8_is_not_checked_when_the_switch_is_off():
    problem, placements = _tiny()
    moved = _moved(placements, "C4", day="Mon", start_period=1)

    assert validate(problem, moved, replace(problem.settings, h8=False)) == []


def test_h9_refuses_the_same_course_twice_on_one_day():
    problem, placements = _tiny()
    problem = _with_card(problem, "C4", course="Course 3", audiences=(Audience("X", "A"),))

    found = validate(problem, placements, problem.settings)

    assert _rules(found) == ["H9"]
    assert found[0].card_ids == ("C3", "C4")
    assert found[0].text == "Course 3 for Class X A is held twice on Tue."


def test_h9_is_not_checked_when_the_switch_is_off():
    problem, placements = _tiny()
    problem = _with_card(problem, "C4", course="Course 3", audiences=(Audience("X", "A"),))

    assert validate(problem, placements, replace(problem.settings, h9=False)) == []


def test_two_groups_of_one_division_may_share_a_slot():
    problem, placements = _tiny()
    problem = _with_card(problem, "C2", teachers=())
    moved = _moved(placements, "C2", start_period=1)

    assert validate(problem, moved, problem.settings) == []


def test_groups_of_different_divisions_may_not_share_a_slot():
    problem, placements = _tiny()
    problem = _with_second_division(problem)
    problem = _with_card(problem, "C2", teachers=(), audiences=(Audience("X", "Arabic"),))
    moved = _moved(placements, "C2", start_period=1)

    found = validate(problem, moved, problem.settings)

    assert _rules(found) == ["H5"]
    assert found[0].card_ids == ("C1", "C2")


def test_a_group_and_the_whole_class_may_not_share_a_slot():
    problem, placements = _tiny()
    problem = _with_card(problem, "C2", teachers=(), audiences=(Audience("X", None),))
    moved = _moved(placements, "C2", start_period=1)

    found = validate(problem, moved, problem.settings)

    assert _rules(found) == ["H5"]
    assert found[0].text == "Class X has Course 1 and Course 2 at the same time (Mon, period 1)."


def test_alternate_week_lessons_may_share_a_teacher_a_room_and_a_slot():
    problem, placements = _tiny()
    problem = _with_card(problem, "C3", weeks=("A",))
    problem = _with_card(problem, "C4", weeks=("B",), room_group="CLASSROOM")
    moved = _moved(placements, "C4", start_period=1, room="R1")

    assert validate(problem, moved, problem.settings) == []


def test_lessons_of_the_same_week_may_not_share_a_teacher_and_a_room():
    problem, placements = _tiny()
    problem = _with_card(problem, "C3", weeks=("A",))
    problem = _with_card(problem, "C4", weeks=("A",), room_group="CLASSROOM")
    moved = _moved(placements, "C4", start_period=1, room="R1")

    found = validate(problem, moved, problem.settings)

    assert _rules(found) == ["H3", "H4"]


def test_moving_one_card_of_a_teacher_onto_another_names_both_courses():
    problem, placements = load_problem(IUT_DATA)
    # L003 and L186 are both taught by KH, on Monday period 3 and Friday period 3.
    moved = _moved(placements, "L186", day="Mon", start_period=3)

    found = [item for item in validate(problem, moved, problem.settings) if item.rule == "H3"]

    assert found[0].card_ids == ("L003", "L186")
    assert found[0].text == "KH teaches CSE 4105 and SWE 4502 at the same time (Mon, period 3)."


def test_the_validator_does_not_use_or_tools():
    source = Path(validator.__file__).read_text(encoding="utf-8")

    assert "ortools" not in source
