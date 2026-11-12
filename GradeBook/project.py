"""GradeBook - a friendly semester GPA calculator."""

import csv
from pathlib import Path

# Every course and how many credit units it carries
COURSES = {
    "CVE 301": 3,
    "IPE 305": 3,
    "ECE 327": 3,
    "ECE 331": 2,
    "ECE 323": 3,
    "ECE 325": 2,
    "ECE 337": 2,
    "ECE 329": 2,
    "ECE 333": 2,
    "ECE 355": 1,
    "ECE 321": 2,
}

# results.csv lives in the same folder as this file
RESULTS_FILE = Path(__file__).with_name("results.csv")

# history.csv keeps one line per finished semester, so we can work out a CGPA
HISTORY_FILE = Path(__file__).with_name("history.csv")

# A little reaction after each score
REACTIONS = {
    "A": "Great work!",
    "B": "Solid.",
    "C": "Not bad.",
    "D": "Keep pushing.",
    "E": "Tough one.",
    "F": "Ouch. Worth double-checking that score?",
}


def main():
    print("Welcome to GradeBook!")
    name = input("What's your name? ").strip()
    if name == "":
        name = "there"
    print(f"Hi {name}, let's look at your semester.")

    try:
        while True:
            print("\n==============================")
            print("  GRADEBOOK")
            print("  Your semester, in numbers")
            print("==============================")
            print("  1. See my courses")
            print("  2. Enter my scores")
            print("  3. Fix a saved score")
            print("  4. See my results and GPA")
            print("  5. Save this semester to my history")
            print("  6. See my CGPA (all semesters)")
            print("  7. Exit")
            print("------------------------------")
            choice = input("What would you like to do? (1-7): ").strip()

            if choice == "7":
                break
            elif choice == "1":
                show_courses()
            elif choice == "2":
                enter_scores()
            elif choice == "3":
                edit_scores()
            elif choice == "4":
                view_results()
            elif choice == "5":
                archive_semester()
            elif choice == "6":
                view_cgpa()
            else:
                print(f"\nHmm, '{choice[:20]}' isn't one of the options. Please type a number from 1 to 7.")

            input("\nPress ENTER to go back to the menu...")
    except (KeyboardInterrupt, EOFError):
        print()

    print(f"See you next time, {name}!")


def get_grade(score):
    """Turn a score from 0 to 100 into a letter and a grade point."""
    if type(score) is not int:
        raise ValueError("Score must be a whole number.")
    if score < 0 or score > 100:
        raise ValueError("Score must be between 0 and 100.")

    if score >= 70:
        return "A", 5
    elif score >= 60:
        return "B", 4
    elif score >= 50:
        return "C", 3
    elif score >= 45:
        return "D", 2
    elif score >= 40:
        return "E", 1
    else:
        return "F", 0


def get_totals(scores):
    """Return (total quality points, total units) for a {course: score} dictionary."""
    total_points = 0
    total_units = 0
    for course, score in scores.items():
        letter, point = get_grade(score)
        units = COURSES[course]
        total_points += point * units
        total_units += units
    return total_points, total_units


def round_gpa(points, units):
    """Divide points by units and round to 2 decimals, rounding .5 up."""
    # Whole-number maths so that 4.125 rounds up to 4.13, like most universities do
    hundredths = (points * 200 + units) // (2 * units)
    return hundredths / 100


def calculate_gpa(scores):
    """Work out the semester GPA from a {course: score} dictionary."""
    if len(scores) == 0:
        raise ValueError("There are no scores to work with.")

    points, units = get_totals(scores)
    return round_gpa(points, units)


def calculate_cgpa(history):
    """Work out the cumulative GPA from a list of (semester, units, points)."""
    if len(history) == 0:
        raise ValueError("There are no past semesters yet.")

    total_points = 0
    total_units = 0
    for semester, units, points in history:
        total_points += points
        total_units += units
    return round_gpa(total_points, total_units)


def describe_gpa(gpa):
    """Say something kind about a GPA."""
    if gpa >= 4.5:
        return "That's First Class range. Brilliant!"
    elif gpa >= 3.5:
        return "That's Second Class Upper range. Really good!"
    elif gpa >= 2.4:
        return "That's Second Class Lower range. Solid, with room to climb."
    elif gpa >= 1.5:
        return "That's Third Class range. You can bring it up, keep going."
    elif gpa >= 1.0:
        return "That's Pass range. Time to regroup. You've got this."
    else:
        return "Below pass level this semester. Talk to your course adviser and make a plan."


def save_results(scores, file_path=None):
    """Save {course: score} to a CSV file."""
    if file_path is None:
        file_path = RESULTS_FILE

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["course", "score"])
        for course, score in scores.items():
            writer.writerow([course, score])


def load_results(file_path=None):
    """Read {course: score} from a CSV file. No file just means no results yet."""
    if file_path is None:
        file_path = RESULTS_FILE
    if not Path(file_path).exists():
        return {}

    scores = {}
    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames or []
        if "course" not in columns or "score" not in columns:
            raise ValueError("The results file needs 'course' and 'score' columns.")

        for row in reader:
            course = (row["course"] or "").strip()
            if course not in COURSES:
                raise ValueError(f"Unknown course in results file: '{course}'.")
            if course in scores:
                raise ValueError(f"Duplicate course in results file: {course}.")
            try:
                score = int(row["score"])
                get_grade(score)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid score for {course} in results file.")
            scores[course] = score
    return scores


def save_history(history, file_path=None):
    """Save a list of (semester, units, points) to a CSV file."""
    if file_path is None:
        file_path = HISTORY_FILE

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["semester", "units", "points"])
        for semester, units, points in history:
            writer.writerow([semester, units, points])


def load_history(file_path=None):
    """Read the list of (semester, units, points). No file just means no history yet."""
    if file_path is None:
        file_path = HISTORY_FILE
    if not Path(file_path).exists():
        return []

    history = []
    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames or []
        if "semester" not in columns or "units" not in columns or "points" not in columns:
            raise ValueError("The history file needs 'semester', 'units' and 'points' columns.")

        for row in reader:
            semester = (row["semester"] or "").strip()
            try:
                units = int(row["units"])
                points = int(row["points"])
            except (ValueError, TypeError):
                raise ValueError(f"Invalid numbers for '{semester}' in the history file.")
            # The best possible grade point is 5, so points can never be more than 5 x units
            if semester == "" or units <= 0 or points < 0 or points > 5 * units:
                raise ValueError(f"Invalid numbers for '{semester}' in the history file.")
            history.append((semester, units, points))
    return history


def ask_score(course, label=""):
    """Ask for a score until it's valid. Returns None if the user types Q."""
    while True:
        units = COURSES[course]
        word = "unit" if units == 1 else "units"
        text = input(f"{label}{course} ({units} {word}) - your score: ").strip()
        if text.lower() == "q":
            return None

        # isdigit() rejects things like "+70", "7.5" and "-3"
        if text.isdigit():
            score = int(text)
            if score <= 100:
                letter, point = get_grade(score)
                print(f"   That's a {letter}. {REACTIONS[letter]}")
                return score
        print("   Please type a whole number from 0 to 100 (or Q to cancel).")


def show_summary(scores):
    """Print a numbered table of results, then the GPA."""
    print(f"\n{'#':>2}  {'Course':<8} {'Units':>5} {'Score':>6} {'Grade':>6}")
    print("-" * 32)
    total_units = 0
    number = 1
    for course, score in scores.items():
        letter, point = get_grade(score)
        print(f"{number:>2}  {course:<8} {COURSES[course]:>5} {score:>6} {letter:>6}")
        total_units += COURSES[course]
        number += 1
    print("-" * 32)

    gpa = calculate_gpa(scores)
    print(f"Total credit units: {total_units}")
    print(f"Semester GPA: {gpa:.2f} / 5.00")
    print(describe_gpa(gpa))
    print()


def review_and_save(scores):
    """Show the results, let the user fix a row, and save when they're happy."""
    courses = list(scores)
    while True:
        show_summary(scores)
        choice = input("Press ENTER to save, type a row number to change it, or Q to throw this away: ")
        choice = choice.strip().lower()

        if choice == "":
            save_results(scores)
            print("Saved! Your scores are safe in results.csv.")
            return
        elif choice == "q":
            print("No problem, nothing was saved.")
            return
        elif choice.isdigit() and 1 <= int(choice) <= len(courses):
            course = courses[int(choice) - 1]
            new_score = ask_score(course)
            if new_score is not None:
                scores[course] = new_score
        else:
            print("Sorry, I didn't get that. ENTER to save, a row number, or Q.")


def get_saved_scores():
    """Load saved scores, with a friendly message if there's nothing or something's wrong."""
    try:
        scores = load_results()
    except ValueError as error:
        print(f"\nOops, there's a problem with your results file: {error}")
        print("Pick option 2 to start fresh.")
        return {}

    if len(scores) == 0:
        print("\nYou haven't saved any scores yet. Pick option 2 to add them.")
    return scores


def show_courses():
    print(f"\n{'Course':<8} {'Units':>5}")
    print("-" * 14)
    for course, units in COURSES.items():
        print(f"{course:<8} {units:>5}")
    print("-" * 14)
    print(f"{'Total':<8} {sum(COURSES.values()):>5}")


def enter_scores():
    if RESULTS_FILE.exists():
        answer = input("You already have saved scores. Replace them? (y/N): ").strip().lower()
        if answer != "y":
            print("Okay, leaving them as they are. Use option 3 if you just want to fix one.")
            return

    print("\nLet's go through your courses one by one (scores are 0-100).")
    print("You can fix mistakes at the end, or type Q any time to cancel.\n")

    scores = {}
    number = 1
    for course in COURSES:
        score = ask_score(course, f"[{number}/{len(COURSES)}] ")
        if score is None:
            print("No problem, nothing was saved.")
            return
        scores[course] = score
        number += 1

    review_and_save(scores)


def edit_scores():
    scores = get_saved_scores()
    if len(scores) > 0:
        review_and_save(scores)


def view_results():
    scores = get_saved_scores()
    if len(scores) > 0:
        show_summary(scores)


def archive_semester():
    scores = get_saved_scores()
    if len(scores) == 0:
        return

    name = input("What should this semester be called? (for example: 200L First Semester): ").strip()
    if name == "":
        print("A semester needs a name, so nothing was saved.")
        return

    try:
        history = load_history()
    except ValueError as error:
        print(f"\nOops, there's a problem with your history file: {error}")
        return

    # If this name is already in the history, replace it instead of adding it twice
    new_history = []
    for semester, units, points in history:
        if semester != name:
            new_history.append((semester, units, points))
    points, units = get_totals(scores)
    new_history.append((name, units, points))

    save_history(new_history)
    print(f"Done! '{name}' is now in your history. Option 6 shows your CGPA.")


def view_cgpa():
    try:
        history = load_history()
    except ValueError as error:
        print(f"\nOops, there's a problem with your history file: {error}")
        return
    if len(history) == 0:
        print("\nYour history is empty. Finish a semester with option 5 first.")
        return

    print(f"\n{'Semester':<26} {'Units':>5} {'GPA':>6}")
    print("-" * 39)
    for semester, units, points in history:
        print(f"{semester:<26} {units:>5} {round_gpa(points, units):>6.2f}")
    print("-" * 39)

    cgpa = calculate_cgpa(history)
    print(f"Cumulative GPA (CGPA): {cgpa:.2f} / 5.00")
    print(describe_gpa(cgpa))


if __name__ == "__main__":
    main()