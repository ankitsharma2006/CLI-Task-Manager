# Task Manager CLI

A command-line task manager built in Python as a practical project for learning and applying core programming concepts without relying on a framework.

The project focuses on working with classes, dictionaries, functions, input validation, file I/O, JSON persistence, state management, and defensive error handling.

## Features

- Create, update, delete, and complete tasks
- Set `LOW`, `MEDIUM`, or `HIGH` priority
- Set and validate deadlines in `YYYY-MM-DD HH:MM` format
- Search tasks by partial, case-insensitive name
- Keep completed tasks in a separate history
- Reuse IDs released by deleted tasks
- Persist the application state in `task.json`
- Restore tasks and history when the program starts
- Handle invalid input, missing files, and corrupted JSON
- Provide a simple interactive command-line interface

## Project Structure and Ownership

The main program is:

```text
app.py
task.json
```

`app.py` contains the actual Task Manager implementation and was fully coded and built by me. It contains the task model, command handling, CRUD operations, validation, ID generation and recycling, history management, and JSON persistence.

`task.json` stores the application's saved state between runs.

The remaining files:

```text
index.html
style.css
app.js
```

are a **vibe-coded presentation layer**. They were added to provide a browser-based version of the same CLI experience and make the project easier to run and observe through Vercel.

The core project is the Python implementation in `app.py` together with its persisted data in `task.json`.

## Architecture

```text
                         +----------------------+
                         |       User / CLI      |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |   Command Loop       |
                         | CREATE / LIST        |
                         | UPDATE / DELETE      |
                         | DONE / SEARCH        |
                         | HISTORY / HELP / EXIT|
                         +----------+-----------+
                                    |
                    +---------------+---------------+
                    |               |               |
                    v               v               v
              +-----------+   +-----------+   +-------------+
              |   tasks   |   |  history  |   | available_ids|
              |  active   |   | completed |   | deleted IDs |
              +-----------+   +-----------+   +-------------+
                    |               |               |
                    +---------------+---------------+
                                    |
                                    v
                         +----------------------+
                         |   JSON Persistence   |
                         |      task.json       |
                         +----------+-----------+
                                    |
                    +---------------+---------------+
                    |                               |
                    v                               v
              Program Start                    Program Exit
                    |                               |
                    v                               v
                 READ JSON                      WRITE JSON
```

### Application flow

```text
Program starts
      |
      v
Read task.json
      |
      v
Reconstruct tasks and history
      |
      v
Run command loop
      |
      +---- CREATE
      +---- LIST
      +---- UPDATE
      +---- DELETE
      +---- DONE
      +---- SEARCH
      +---- HISTORY
      +---- HELP
      |
      v
EXIT
      |
      v
Convert task objects to dictionaries
      |
      v
Write task.json
```

## Task Model

Each task contains:

```text
id
name
priority
completed
date_created
deadline
```

The program also maintains:

```text
last_id
tasks
history
available_ids
```

`last_id` keeps track of the highest newly generated ID. When a task is deleted, its ID is placed in `available_ids` and can be reused by a later `CREATE`.

When a task is completed, it is removed from `tasks` and moved to `history`. Completed IDs are therefore not recycled.

## Persistence

The program reads the saved state when it starts.

```text
task.json
   |
   +--> last_id
   +--> available_ids
   +--> tasks
   +--> history
```

When reading, the stored dictionaries are converted back into task objects using `Task.from_dict()`.

When the program exits, the task objects are converted into dictionaries using `to_dict()` and written back to `task.json` with JSON.

The web version uses `localStorage` instead of the local Python file because a static browser application cannot directly access the Python program's local `task.json`.

## Validation and Error Handling

Input is checked before operations are performed.

Examples include:

- Empty task names are rejected.
- Priority must be `LOW`, `MEDIUM`, or `HIGH`.
- Deadlines must follow `YYYY-MM-DD HH:MM`.
- Deadlines cannot be in the past.
- Task IDs must be valid integers.
- UPDATE options must be valid.
- Unknown commands do not terminate the program.
- Missing or corrupted JSON data is handled without crashing.

For `UPDATE ALL`, the new name, priority, and deadline are first validated using temporary values. The task is only changed after all three values are valid.

## Commands

| Command | Purpose |
|---|---|
| `CREATE` | Create a new task |
| `LIST` | Show active tasks |
| `UPDATE` | Update an existing task |
| `DELETE` | Delete a task and release its ID |
| `DONE` | Mark a task as completed and move it to history |
| `SEARCH` | Search active tasks by name |
| `HISTORY` | Show completed tasks |
| `HELP` | Show available commands |
| `EXIT` | Save the current state and exit |

## Testing

The main functionality was tested manually through the CLI with both valid and invalid inputs.

### Functional tests

| Area | Test | Expected result |
|---|---|---|
| CREATE | Valid task | Task is created with a generated ID |
| CREATE | Empty name | Input is rejected |
| CREATE | Invalid priority | Input is rejected |
| CREATE | Invalid date | Input is rejected |
| CREATE | Past deadline | Input is rejected |
| LIST | Active tasks exist | Tasks are displayed |
| UPDATE | Valid name/priority/deadline | Task is updated |
| UPDATE | Invalid ID | Input is rejected |
| UPDATE | Invalid option | Input is rejected |
| UPDATE ALL | Invalid later field | Existing task is not partially changed |
| DELETE | Existing task | Task is removed and ID becomes available |
| DELETE | Unknown ID | Input is rejected |
| DONE | Existing task | Task moves to history |
| SEARCH | Partial name | Matching tasks are returned |
| SEARCH | No match | Empty-result message is shown |
| HISTORY | Completed tasks exist | Completed tasks are displayed |
| Persistence | Restart after saving | Previous state is restored |
| Persistence | Missing JSON | Program starts without crashing |
| Persistence | Corrupted JSON | Program starts without crashing |
| CLI | Unknown command | Error message is shown and loop continues |

### ID recycling test

A representative test flow is:

```text
CREATE -> ID 1
CREATE -> ID 2
DELETE -> ID 1 released
CREATE -> ID 1 reused
DONE -> ID 1 moved to HISTORY
CREATE -> next new ID continues from last_id
```

This verifies that deleted IDs can be reused without incorrectly lowering `last_id`.

## What Broke and What I Learned

Building the project from scratch exposed several problems that were not obvious at the beginning. Fixing them helped me understand how the different parts of the application actually work together.

- **JSON cannot store Python objects directly.** Tasks were Python class objects, but JSON only supports basic data types. I learned to convert task objects into dictionaries using `to_dict()` before saving, and reconstruct them using `from_dict()` when loading.

- **Loading data is different from creating new tasks.** When reading `task.json`, creating a `Task` normally would generate a new ID and date. I had to modify the design so that saved IDs and creation dates could be restored instead of regenerated.

- **I initially had redundant object assignment in `from_dict()`.** The ID was already being passed to `__init__()`, so assigning `task.id` again afterward was unnecessary. This helped me understand exactly when and where object attributes are initialized.

- **ID generation and ID recycling caused logical issues.** A deleted task's ID can be reused, but deleting a task must not reduce `last_id`. I separated `last_id` from `available_ids` so newly generated IDs continue correctly while deleted IDs can be reused.

- **Validation should happen before changing the task.** This became especially important with `UPDATE ALL`. If one of the later inputs was invalid, directly modifying the task could leave it partially updated. I learned to validate the new values first and only assign them after all inputs are valid.

- **Input errors should not terminate the application.** Invalid task IDs, priorities, dates, update options, and commands needed to be handled without crashing the command loop. This made me use `try/except` and explicit validation more carefully.

- **Date validation required more than checking the format.** A deadline could have the correct-looking format but still be invalid or already in the past. I learned to parse the date and compare it against the current time rather than treating it as plain text.

- **Missing and corrupted files are different failure cases.** The program needed to start normally when `task.json` did not exist and also handle invalid JSON instead of crashing during startup.

- **The browser version initially did not match the actual CLI design.** The first interface used dashboard-style elements and popup forms, which did not represent how the Python program actually worked. I changed the interaction to follow the same sequential `input()` style as the CLI.

- **The web implementation exposed a JavaScript syntax error.** One incorrect character in the JavaScript caused the entire browser program to fail. Checking the JavaScript syntax before packaging helped identify the problem.

- **A browser cannot directly use the Python program's local `task.json`.** The Python application reads and writes the local file, while a static browser application runs separately. This made me understand the difference between the actual Python application and a browser-based presentation of it.

- **Persistence has to be tested across program runs.** It was not enough to verify that tasks existed in memory. Restarting the program and checking that tasks, history, IDs, and deleted-ID information were restored helped verify that the JSON persistence was actually working.

The main lesson from the project was that even a relatively small CLI application requires careful handling of **state, data conversion, validation, object construction, file persistence, and edge cases**. Building these parts manually made the underlying Python concepts much clearer than using a framework to handle them automatically.

## Running the Program

```bash
python app.py
```

The program reads and writes `task.json` in the project directory.

## Project Structure

```text
task-manager/
├── app.py          # Main Python program and logic
├── task.json       # Saved application state
├── index.html      # Vibe-coded web presentation
├── style.css       # Vibe-coded web styling
├── app.js          # Vibe-coded browser presentation logic
└── README.md
```

`app.py` and `task.json` are the core project files. The other files are used for the browser-based presentation.
