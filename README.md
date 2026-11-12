# GradeBook

#### Video Demo:https://youtu.be/XdihMjRc9LY?si=81usbrYMcQrtyHkE
#### Description:

GradeBook is a command-line program written in Python that works out my GPA. I type in my score for each course in a semester, and it shows my letter grades, my total credit units and my semester GPA out of 5.00. It saves my scores in a file, so I can come back later, look at them again, or fix one score without typing everything again. When a semester is finished, I can save it to a history file, and the program then works out my CGPA (cumulative GPA) across all my semesters.

I made it because I used to work out my GPA by hand every semester, and with so many courses and different credit units it was easy to make mistakes. The courses in the program are my own semester courses, and the grading scale is the one my university uses: 70 and above is an A (5 points), 60 to 69 is a B (4), 50 to 59 is a C (3), 45 to 49 is a D (2), 40 to 44 is an E (1), and below 40 is an F (0).

## How to use it

Run python project.py. The program asks for my name and then shows a menu:

1. See my courses
2. Enter my scores
3. Fix a saved score
4. See my results and GPA
5. Save this semester to my history
6. See my CGPA (all semesters)
7. Exit

To run the tests, install pytest (pip install pytest) and run pytest.

## Files

- project.py is the whole program. main shows the menu, and the other functions do the work.
- test_project.py has the pytest tests for the functions in project.py.
- requirements.txt lists pytest, which is the only thing needed to run the tests.
- results.csv is made automatically when I save my scores for the current semester.
- history.csv is made automatically when I save a finished semester. It has one line per semester.

## What the main functions do

- get_grade turns a score from 0 to 100 into a letter and a grade point. It raises an error if the score is not a whole number from 0 to 100.
- get_totals goes through all the courses and adds up the quality points (grade point times units) and the units.
- round_gpa divides points by units and rounds to two decimal places.
- calculate_gpa works out one semester's GPA, and calculate_cgpa works out the GPA over all the saved semesters.
- describe_gpa says something encouraging about a GPA, like "First Class range".
- save_results and load_results write and read the scores file. save_history and load_history do the same for the history file. The loading functions check the file carefully and give a clear error message if something is wrong.
- ask_score keeps asking until I type a valid score, and typing Q cancels.
- show_summary prints the numbered results table, and review_and_save is the screen where I can fix a row before saving.

## Design choices

I only save the course and the score. My first version also saved the units, the letter grade and the grade point. Then I had to check that all five columns agreed with each other, which meant a lot of extra code. Those three things can always be worked out again, so now I only save two columns. There is only one place where a mistake can hide.

The history file saves units and points, not GPAs. To work out a CGPA, I cannot just average the semester GPAs, because a semester with more units should count for more. So for each semester I save the total units and the total quality points. The CGPA is then all the points divided by all the units. I also check when loading that the points can never be more than 5 times the units.

GPA rounding uses whole-number maths. Python's round() turns 4.125 into 4.12, but most universities round up to 4.13. So round_gpa works in hundredths using integer division. I wrote a test for exactly this case.

A review screen before saving. Typing eleven scores in a row makes typos likely. Instead of asking "are you sure?" after every course, the program lets me type everything and then shows the whole table, where I can fix any row. I reuse the same screen for "Fix a saved score", which kept the code shorter.
Careful input checking. ask_score only accepts plain digits, so inputs like +70 or 7.5 are rejected. Typing Q cancels, so I never get stuck in the middle. Option 2 also asks before it replaces saved scores, and a broken CSV file shows a friendly message instead of crashing.

## Testing

I used pytest. The tests check every grade boundary (69 is a B and 70 is an A), the GPA and CGPA maths including the rounding case, saving and loading through a temporary folder, and bad CSV files. For the functions that use input() and print(), I used monkeypatch to fake the keyboard and capsys to read what was printed.

## What I would add next

The courses are written inside project.py, so I have to edit them each semester. Later I could read them from a file instead.
