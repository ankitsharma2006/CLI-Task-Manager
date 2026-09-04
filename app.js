const KEY = "task_manager_cli_state";

let tasks = {};
let history = {};
let available_ids = [];
let last_id = 0;

/* null = waiting for a command
   object = waiting for one of the Python-style input() answers */
let cliState = null;

const output = document.getElementById("output");
const screen = document.getElementById("screen");
const cmd = document.getElementById("cmd");

function esc(value) {
  return String(value).replace(/[&<>"']/g, function (c) {
    const chars = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;"
    };
    return chars[c];
  });
}

function print(text = "", cls = "") {
  const div = document.createElement("div");
  div.className = "line " + cls;
  div.innerHTML = text;
  output.appendChild(div);
  screen.scrollTop = screen.scrollHeight;
}

function printPlain(text = "", cls = "") {
  print(esc(text), cls);
}

function saveData() {
  try {
    localStorage.setItem(KEY, JSON.stringify({
      last_id: last_id,
      history: history,
      available_ids: available_ids,
      tasks: tasks
    }));
  } catch (error) {
    printPlain("Unable to save task data.", "error");
  }
}

function loadData() {
  try {
    const raw = localStorage.getItem(KEY);

    if (raw === null) {
      last_id = 0;
      tasks = {};
      history = {};
      available_ids = [];
      return;
    }

    const data = JSON.parse(raw);

    last_id = data.last_id;
    available_ids = data.available_ids || [];

    Object.keys(data.history || {}).forEach(function (key) {
      const task = from_dict(data.history[key]);
      history[task.id] = task;
    });

    Object.keys(data.tasks || {}).forEach(function (key) {
      const task = from_dict(data.tasks[key]);
      tasks[task.id] = task;
    });
  } catch (error) {
    last_id = 0;
    tasks = {};
    history = {};
    available_ids = [];

    printPlain(
      "Data file is missing, empty, or corrupted. Starting with empty task data.",
      "error"
    );
  }
}

function from_dict(data) {
  return {
    id: data.id,
    name: data.name,
    priority: data.priority,
    completed: data.completed,
    date_created: data.date_created,
    deadline: data.deadline
  };
}

function generate_id() {
  last_id += 1;
  return last_id;
}

function parseDeadline(value) {
  if (!/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(value)) {
    throw new Error("Invalid deadline format");
  }

  const parts = value.split(" ");
  const dateParts = parts[0].split("-").map(Number);
  const timeParts = parts[1].split(":").map(Number);

  const year = dateParts[0];
  const month = dateParts[1];
  const day = dateParts[2];
  const hour = timeParts[0];
  const minute = timeParts[1];

  const date = new Date(year, month - 1, day, hour, minute);

  if (
    date.getFullYear() !== year ||
    date.getMonth() !== month - 1 ||
    date.getDate() !== day ||
    date.getHours() !== hour ||
    date.getMinutes() !== minute
  ) {
    throw new Error("Invalid deadline");
  }

  return date;
}

function validDeadline(value) {
  try {
    const date = parseDeadline(value);
    return date >= new Date();
  } catch (error) {
    return false;
  }
}

function taskTable(collection) {
  const values = Object.values(collection);

  if (values.length === 0) {
    return "";
  }

  let html =
    '<div class="table"><table>' +
    "<tr><th>ID</th><th>NAME</th><th>PRIORITY</th><th>COMPLETED</th><th>DATE CREATED</th><th>DEADLINE</th></tr>";

  values.forEach(function (task) {
    html +=
      "<tr><td>" + task.id + "</td>" +
      "<td>" + esc(task.name) + "</td>" +
      '<td class="' + task.priority + '">' + task.priority + "</td>" +
      "<td>" + task.completed + "</td>" +
      "<td>" + esc(task.date_created) + "</td>" +
      "<td>" + esc(task.deadline) + "</td></tr>";
  });

  html += "</table></div>";
  return html;
}

function getTaskJson() {
  return JSON.stringify({
    last_id: last_id,
    history: history,
    available_ids: available_ids,
    tasks: tasks
  }, null, 4);
}

function showTaskJsonOption() {
  const json = getTaskJson();
  const encoded = encodeURIComponent(json);

  print(
    '<span class="info">task.json saved successfully.</span> ' +
    '<a class="file-link" href="data:application/json;charset=utf-8,' +
    encoded +
    '" download="task.json">[ View / Download task.json ]</a>'
  );
}

function showTaskJson() {
  printPlain("----- task.json -----");
  print('<pre class="json-file">' + esc(getTaskJson()) + '</pre>');
  printPlain("---------------------");
}

function reexecuteProgram() {
  /*
   * This simulates starting the Python program again:
   * clear in-memory structures -> read persisted data -> continue.
   */
  printPlain("");
  printPlain("Re-executing task manager...");
  printPlain("");

  tasks = {};
  history = {};
  available_ids = [];
  last_id = 0;

  loadData();

  printPlain("Welcome to the Task Manager!");
  printPlain("help - Show available commands");
  printPlain("Data read from task.json successfully.", "info");
}

/* This is the browser equivalent of Python input(prompt).
   The prompt is printed first, then the next submitted line becomes its answer. */
function input(promptText, callback) {
  printPlain(promptText);
  cliState = { callback: callback };
  cmd.placeholder = "";
  cmd.focus();
}

function submitInput(answer) {
  if (cliState === null) {
    return false;
  }

  const callback = cliState.callback;
  cliState = null;
  callback(answer);
  return true;
}

function createCLI() {
  input("Enter task name: ", function (name) {
    name = name.trim();

    if (name === "") {
      printPlain(
        "Task name cannot be empty. Please enter a valid name.",
        "error"
      );
      return;
    }

    input("Enter task priority (LOW, MEDIUM, HIGH): ", function (priority) {
      priority = priority.trim().toUpperCase();

      if (!["LOW", "MEDIUM", "HIGH"].includes(priority)) {
        printPlain(
          "Invalid priority. Please enter LOW, MEDIUM, or HIGH.",
          "error"
        );
        return;
      }

      input("Enter task deadline (YYYY-MM-DD HH:MM): ", function (deadline) {
        deadline = deadline.trim();

        try {
          parseDeadline(deadline);

          if (deadline < new Date().toISOString().slice(0, 16).replace("T", " ")) {
            printPlain(
              "Deadline cannot be in the past. Please enter a future date and time.",
              "error"
            );
            return;
          }
        } catch (error) {
          printPlain(
            "Invalid deadline format. Please use YYYY-MM-DD HH:MM.",
            "error"
          );
          return;
        }

        let newId;

        if (available_ids.length > 0) {
          newId = available_ids.shift();
        } else {
          newId = generate_id();
        }

        const task = {
          id: newId,
          name: name,
          priority: priority,
          completed: false,
          date_created: new Date().toISOString().replace("T", " ").slice(0, 19),
          deadline: deadline
        };

        tasks[task.id] = task;
        saveData();

        printPlain(
          "Task '" + task.name + "' added with ID " + task.id + ".",
          "success"
        );
      });
    });
  });
}

function updateCLI() {
  input("Enter task ID to update: ", function (rawId) {
    let taskId;

    try {
      taskId = Number(rawId);

      if (!Number.isInteger(taskId)) {
        throw new Error("ValueError");
      }
    } catch (error) {
      printPlain(
        "Invalid task ID. Please enter a valid integer.",
        "error"
      );
      return;
    }

    if (!(taskId in tasks)) {
      printPlain("Task ID not found.", "error");
      return;
    }

    input(
      "Enter 1 to update name, 2 to update priority, 3 to update deadline, 4 to update all: ",
      function (rawUpdate) {
        let update;

        try {
          update = Number(rawUpdate);

          if (!Number.isInteger(update)) {
            throw new Error("ValueError");
          }
        } catch (error) {
          printPlain(
            "Invalid input. Please enter a valid integer.",
            "error"
          );
          return;
        }

        if (![1, 2, 3, 4].includes(update)) {
          printPlain(
            "Invalid option. Please enter 1, 2, 3, or 4.",
            "error"
          );
          return;
        }
      

        const task = tasks[taskId];

        if (update === 1) {
          input(
            "Enter new name (current: " + task.name + "): ",
            function (newName) {
              task.name = newName || task.name;

              if (task.name.trim() === "") {
                printPlain(
                  "Task name cannot be empty. Please enter a valid name.",
                  "error"
                );
                return;
              }

              saveData();
              printPlain("Task ID " + task.id + " updated.", "success");
            }
          );
        }

        else if (update === 2) {
          input(
            "Enter new priority (current: " + task.priority + "): ",
            function (newPriority) {
              newPriority =
                newPriority.toUpperCase() || task.priority;

              if (!["LOW", "MEDIUM", "HIGH"].includes(newPriority)) {
                printPlain(
                  "Invalid priority. Please enter LOW, MEDIUM, or HIGH.",
                  "error"
                );
                return;
              }

              task.priority = newPriority;
              saveData();
              printPlain("Task ID " + task.id + " updated.", "success");
            }
          );
        }

        else if (update === 3) {
          input(
            "Enter new deadline (current: " + task.deadline + "): ",
            function (newDeadline) {
              newDeadline = newDeadline || task.deadline;

              try {
                parseDeadline(newDeadline);

                if (
                  newDeadline <
                  new Date().toISOString().slice(0, 16).replace("T", " ")
                ) {
                  printPlain(
                    "Deadline cannot be in the past. Please enter a future date and time.",
                    "error"
                  );
                  return;
                }

                task.deadline = newDeadline;
                saveData();
                printPlain("Task ID " + task.id + " updated.", "success");
              } catch (error) {
                printPlain(
                  "Invalid deadline format. Please use YYYY-MM-DD HH:MM.",
                  "error"
                );
              }
            }
          );
        }

        else if (update === 4) {
          input(
            "Enter new name (current: " + task.name + "): ",
            function (newName) {
              const tempName = newName || task.name;

              if (tempName.trim() === "") {
                printPlain(
                  "Task name cannot be empty. Please enter a valid name.",
                  "error"
                );
                return;
              }

              input(
                "Enter new priority (current: " + task.priority + "): ",
                function (newPriority) {
                  const tempPriority =
                    newPriority.toUpperCase() || task.priority;

                  if (!["LOW", "MEDIUM", "HIGH"].includes(tempPriority)) {
                    printPlain(
                      "Invalid priority. Please enter LOW, MEDIUM, or HIGH.",
                      "error"
                    );
                    return;
                  }

                  input(
                    "Enter new deadline (current: " + task.deadline + "): ",
                    function (newDeadline) {
                      const tempDeadline =
                        newDeadline || task.deadline;

                      try {
                        parseDeadline(tempDeadline);

                        if (
                          tempDeadline <
                          new Date().toISOString().slice(0, 16).replace("T", " ")
                        ) {
                          printPlain(
                            "Deadline cannot be in the past. Please enter a future date and time.",
                            "error"
                          );
                          return;
                        }
                      } catch (error) {
                        printPlain(
                          "Invalid deadline format. Please use YYYY-MM-DD HH:MM.",
                          "error"
                        );
                        return;
                      }

                      task.name = tempName;
                      task.priority = tempPriority;
                      task.deadline = tempDeadline;

                      saveData();
                      printPlain("Task ID " + task.id + " updated.", "success");
                    }
                  );
                }
              );
            }
          );
        }
      }
    );
  });
}

function deleteCLI() {
  input("Enter task ID to delete: ", function (rawId) {
    let taskId;

    try {
      taskId = Number(rawId);

      if (!Number.isInteger(taskId)) {
        throw new Error("ValueError");
      }
    } catch (error) {
      printPlain(
        "Invalid task ID. Please enter a valid integer.",
        "error"
      );
      return;
    }

    if (taskId in tasks) {
      available_ids.push(taskId);
      delete tasks[taskId];

      printPlain("Task ID " + taskId + " deleted.", "success");
    } else {
      printPlain("Task ID not found.", "error");
    }

    saveData();
  });
}

function doneCLI() {
  input("Enter task ID to mark as done: ", function (rawId) {
    let taskId;

    try {
      taskId = Number(rawId);

      if (!Number.isInteger(taskId)) {
        throw new Error("ValueError");
      }
    } catch (error) {
      printPlain(
        "Invalid task ID. Please enter a valid integer.",
        "error"
      );
      return;
    }

    if (taskId in tasks) {
      tasks[taskId].completed = true;
      history[taskId] = tasks[taskId];
      delete tasks[taskId];

      printPlain(
        "Task ID " + taskId + " marked as done.",
        "success"
      );
      saveData();
    } else {
      printPlain("Task ID not found.", "error");
    }
  });
}

function searchCLI() {
  input("Enter task name to search: ", function (searchName) {
    const found = Object.values(tasks).filter(function (task) {
      return task.name.toLowerCase().includes(searchName.toLowerCase());
    });

    if (found.length > 0) {
      const result = {};

      found.forEach(function (task) {
        result[task.id] = task;
      });

      print(taskTable(result));
    } else {
      printPlain("No tasks found with that name.", "warn");
    }
  });
}

function helpCLI() {
  print(
    '<div class="help">' +
      "<b>CREATE</b><span>Create a new task</span>" +
      "<b>LIST</b><span>List all tasks</span>" +
      "<b>UPDATE</b><span>Update an existing task</span>" +
      "<b>DELETE</b><span>Delete a task</span>" +
      "<b>DONE</b><span>Mark a task as completed</span>" +
      "<b>SEARCH</b><span>Search for tasks by name</span>" +
      "<b>HISTORY</b><span>Show completed tasks</span><b>TASK.JSON</b><span>Show the saved JSON file</span><b>REEXEC</b><span>Re-execute and read saved data</span>" +
      "<b>EXIT</b><span>Exit the task manager</span>" +
    "</div>"
  );
}

function executeCommand(raw) {
  const choice = raw.trim().toUpperCase();

  if (choice === "") {
    return;
  }

  print('<span class="echo">&gt; ' + esc(choice) + "</span>");

  if (choice === "CREATE") {
    createCLI();
  }
  else if (choice === "LIST") {
    if (Object.keys(tasks).length > 0) {
      print(taskTable(tasks));
    } else {
      printPlain("No tasks found.");
    }
  }
  else if (choice === "UPDATE") {
    updateCLI();
  }
  else if (choice === "DELETE") {
    deleteCLI();
  }
  else if (choice === "DONE") {
    doneCLI();
  }
  else if (choice === "SEARCH") {
    searchCLI();
  }
  else if (choice === "HISTORY") {
    if (Object.keys(history).length > 0) {
      print(taskTable(history));
    } else {
      printPlain("No completed tasks.");
    }
  }
  else if (choice === "HELP") {
    helpCLI();
  }
  else if (choice === "EXIT") {
    saveData();
    printPlain("Exiting task manager...");
    showTaskJsonOption();
    printPlain("Program stopped.");
    printPlain("Type 'REEXEC' to run the program again and read task.json.");
  }
  else if (choice === "REEXEC") {
    reexecuteProgram();
  }
  else if (choice === "TASK.JSON") {
    showTaskJson();
  }
  else {
    printPlain("Invalid command. Please try again.");
    printPlain("Type 'help' to see the list of commands.");
  }
}

document.getElementById("form").addEventListener("submit", function (event) {
  event.preventDefault();

  const value = cmd.value;
  cmd.value = "";

  if (!submitInput(value)) {
    executeCommand(value);
  }
});

loadData();

printPlain("Welcome to the Task Manager!");
printPlain("help - Show available commands");
