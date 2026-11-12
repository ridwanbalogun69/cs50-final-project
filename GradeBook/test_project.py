import pytest

import project
from project import (
    ask_score,
    calculate_cgpa,
    calculate_gpa,
    describe_gpa,
    get_grade,
    get_totals,
    load_history,
    load_results,
    review_and_save,
    round_gpa,
    save_history,
    save_results,
    show_summary,
)


@pytest.mark.parametrize(
    "score, expected",
    [
        (100, ("A", 5)), (70, ("A", 5)),
        (69, ("B", 4)), (60, ("B", 4)),
        (59, ("C", 3)), (50, ("C", 3)),
        (49, ("D", 2)), (45, ("D", 2)),
        (44, ("E", 1)), (40, ("E", 1)),
        (39, ("F", 0)), (0, ("F", 0)),
    ],
)
def test_get_grade(score, expected):
    assert get_grade(score) == expected


@pytest.mark.parametrize("score", [-1, 101, 75.5, "70", True])
def test_get_grade_rejects_bad_scores(score):
    with pytest.raises(ValueError):
        get_grade(score)


def test_calculate_gpa():
    # CVE 301 (3 units, A=5) and IPE 305 (3 units, B=4): (15 + 12) / 6 = 4.5
    assert calculate_gpa({"CVE 301": 82, "IPE 305": 65}) == 4.5


def test_calculate_gpa_rounds_half_up():
    # 33 points / 8 units = 4.125, which should round UP to 4.13
    assert calculate_gpa({"CVE 301": 80, "IPE 305": 65, "ECE 331": 55}) == 4.13


def test_calculate_gpa_rejects_empty():
    with pytest.raises(ValueError):
        calculate_gpa({})


@pytest.mark.parametrize(
    "gpa, word",
    [(5.0, "First Class"), (4.5, "First Class"), (4.0, "Upper"),
     (3.0, "Lower"), (2.0, "Third"), (1.2, "Pass"), (0.5, "Below pass")],
)
def test_describe_gpa(gpa, word):
    assert word in describe_gpa(gpa)


def test_save_results(tmp_path):
    scores = {"CVE 301": 82, "ECE 355": 41}
    path = tmp_path / "results.csv"
    save_results(scores, path)
    assert load_results(path) == scores


def test_load_results(tmp_path):
    assert load_results(tmp_path / "missing.csv") == {}


@pytest.mark.parametrize(
    "contents, message",
    [
        ("course,score\nNOPE 101,70\n", "Unknown course"),
        ("course,score\nCVE 301,abc\n", "Invalid score"),
        ("course,score\nCVE 301,101\n", "Invalid score"),
        ("course,score\nCVE 301,70\nCVE 301,80\n", "Duplicate course"),
        ("name,mark\nCVE 301,70\n", "columns"),
        ("", "columns"),
    ],
)
def test_load_results_rejects_bad_files(tmp_path, contents, message):
    path = tmp_path / "results.csv"
    path.write_text(contents, encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        load_results(path)


def test_ask_score(monkeypatch):
    answers = iter(["abc", "101", "+70", "1_0", "7.5", "", "68"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    assert ask_score("CVE 301") == 68


def test_ask_score_returns_none_when_cancelled(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "Q")
    assert ask_score("CVE 301") is None


def test_show_summary(capsys):
    show_summary({"CVE 301": 80, "ECE 355": 55})
    output = capsys.readouterr().out
    assert "Total credit units: 4" in output
    assert "Semester GPA: 4.50 / 5.00" in output


def test_review_and_save(tmp_path, monkeypatch):
    path = tmp_path / "results.csv"
    monkeypatch.setattr(project, "RESULTS_FILE", path)
    answers = iter(["nonsense", "1", "90", ""])  # bad input, fix row 1, then save
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    review_and_save({"CVE 301": 50, "IPE 305": 60})
    assert load_results(path) == {"CVE 301": 90, "IPE 305": 60}


def test_get_totals():
    # CVE 301 (3 units, A=5) and IPE 305 (3 units, B=4): 15 + 12 = 27 points over 6 units
    assert get_totals({"CVE 301": 82, "IPE 305": 65}) == (27, 6)


def test_round_gpa():
    assert round_gpa(27, 6) == 4.5
    assert round_gpa(33, 8) == 4.13  # 4.125 rounds up
    assert round_gpa(0, 5) == 0.0


def test_calculate_cgpa():
    # Semester 1: 125 points over 25 units. Semester 2: 100 points over 25 units.
    history = [("First", 25, 125), ("Second", 25, 100)]
    assert calculate_cgpa(history) == 4.5


def test_calculate_cgpa_rejects_empty():
    with pytest.raises(ValueError):
        calculate_cgpa([])


def test_save_history(tmp_path):
    history = [("200L, First Semester", 25, 110), ("200L Second", 22, 90)]
    path = tmp_path / "history.csv"
    save_history(history, path)
    assert load_history(path) == history


def test_load_history(tmp_path):
    assert load_history(tmp_path / "missing.csv") == []


@pytest.mark.parametrize(
    "contents, message",
    [
        ("name,units\nA,25\n", "columns"),
        ("semester,units,points\nA,abc,10\n", "Invalid numbers"),
        ("semester,units,points\nA,0,0\n", "Invalid numbers"),
        ("semester,units,points\nA,10,60\n", "Invalid numbers"),
        ("semester,units,points\n,10,20\n", "Invalid numbers"),
    ],
)
def test_load_history_rejects_bad_files(tmp_path, contents, message):
    path = tmp_path / "history.csv"
    path.write_text(contents, encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        load_history(path)