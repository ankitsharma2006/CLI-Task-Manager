import json
from datetime import datetime

class Task:
  def __init__(self,name: str, priority: int, deadline: str,id=None):
    if id is None:
       self.id = generate_id()
    else:
       self.id = id
      
    self.name = name
    self.priority = priority
    self.completed = False
    self.date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    self.deadline = deadline
  def to_dict(self):
      return {
        "id": self.id,
        "name": self.name,
        "priority": self.priority,
        "completed": self.completed,
        "date_created": self.date_created,
        "deadline": self.deadline
      }
  @classmethod
  def from_dict(cls, data):
      task = cls(data["name"], data["priority"], data["deadline"],data["id"])
      task.completed = data["completed"]
      task.date_created = data["date_created"]
      return task

tasks = {}
history = {}
available_ids = []
  
#read operation
try:
  with open("task.json", "r") as f:
    data=json.load(f)

  last_id = data["last_id"]

  for i in data["available_ids"]:
      available_ids.append(i)

  for i in data["history"]:
      task_data = data["history"][i]
      task = Task.from_dict(task_data)
      history[task.id] = task

  for i in data["tasks"]:
      task_data = data["tasks"][i]
      task = Task.from_dict(task_data)
      tasks[task.id] = task

except (FileNotFoundError, json.JSONDecodeError):
  last_id = 0
  tasks = {}
  history = {}
  available_ids = []

def generate_id():
    global last_id
    last_id += 1
    return last_id

x=True
print("Welcome to the Task Manager!")
print("help - Show available commands")
while x:
    choice = input("Enter command: ").strip().upper()
    
    if choice == "CREATE":
        name = input("Enter task name: ").strip()
        if name.strip() == "":
            print("Task name cannot be empty. Please enter a valid name.")
            continue
        priority = input("Enter task priority (LOW, MEDIUM, HIGH): ").strip().upper()
        if priority not in ["LOW", "MEDIUM", "HIGH"]:
            print("Invalid priority. Please enter LOW, MEDIUM, or HIGH.")
            continue
        deadline = input("Enter task deadline (YYYY-MM-DD HH:MM): ").strip()
        try:
            datetime.strptime(deadline, "%Y-%m-%d %H:%M")
            if deadline < datetime.now().strftime("%Y-%m-%d %H:%M"):
                print("Deadline cannot be in the past. Please enter a future date and time.")
                continue
        except ValueError:
            print("Invalid deadline format. Please use YYYY-MM-DD HH:MM.")
            continue
        if available_ids:
            new_id = available_ids.pop(0)
        else:
            new_id = generate_id()
        task = Task(name, priority, deadline, new_id)
        tasks[task.id] = task
        print(f"Task '{task.name}' added with ID {task.id}.")
    
    elif choice == "LIST":
        if tasks:
            print(f"ID  | NAME    | PRIORITY   | COMPLETED    | DEADLINE   ")
            for task in tasks.values():
              print(f"{task.id} | {task.name} | {task.priority} | {task.completed} | {task.deadline}")
        else:
            print("No tasks found.")
    
    elif choice == "UPDATE":
        try:
            task_id = int(input("Enter task ID to update: "))
        except ValueError:
            print("Invalid task ID. Please enter a valid integer.")
            continue
        if task_id not in tasks:
            print("Task ID not found.")
            continue
        try:
            update = int(input("Enter 1 to update name, 2 to update priority, 3 to update deadline, 4 to update all: "))
            if update not in [1, 2, 3, 4]:
                print("Invalid option. Please enter 1, 2, 3, or 4.")
                continue
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
            continue
        task = tasks[task_id]
        if update == 1:
            task.name = input(f"Enter new name (current: {task.name}): ") or task.name
            if task.name.strip() == "":
                print("Task name cannot be empty. Please enter a valid name.")
                continue
        elif update == 2:
            task_priority = input(f"Enter new priority (current: {task.priority}): ").upper() or task.priority
            if task_priority not in ["LOW", "MEDIUM", "HIGH"]:
                print("Invalid priority. Please enter LOW, MEDIUM, or HIGH.")
                continue
            task.priority = task_priority
        elif update == 3:
            task_deadline = input(f"Enter new deadline (current: {task.deadline}): ") or task.deadline
            if task_deadline:
                try:
                    datetime.strptime(task_deadline, "%Y-%m-%d %H:%M")
                    if task_deadline < datetime.now().strftime("%Y-%m-%d %H:%M"):
                        print("Deadline cannot be in the past. Please enter a future date and time.")
                        continue
                    task.deadline = task_deadline
                except ValueError:
                    print("Invalid deadline format. Please use YYYY-MM-DD HH:MM.")
                    continue
        elif update == 4:
            print("\nLeave a field blank to keep the current value.")
            task_name = input(f"Enter new name (current: {task.name}): ") or task.name
            task_priority = input(f"Enter new priority (current: {task.priority}): ").upper() or task.priority
            if task_priority not in ["LOW", "MEDIUM", "HIGH"]:
                print("Invalid priority. Please enter LOW, MEDIUM, or HIGH.")
                continue
            task_deadline = input(f"Enter new deadline (current: {task.deadline}): ") or task.deadline
            if task_deadline:
                try:
                    datetime.strptime(task_deadline, "%Y-%m-%d %H:%M")
                    if task_deadline < datetime.now().strftime("%Y-%m-%d %H:%M"):
                        print("Deadline cannot be in the past. Please enter a future date and time.")
                        continue
                except ValueError:
                    print("Invalid deadline format. Please use YYYY-MM-DD HH:MM.")
                    continue
            task.name = task_name
            task.priority = task_priority
            task.deadline = task_deadline
        print(f"Task ID {task.id} updated.")
    
    elif choice == "DELETE":
        try:
            task_id = int(input("Enter task ID to delete: "))
        except ValueError:
            print("Invalid task ID. Please enter a valid integer.")
            continue
        if task_id in tasks:
            available_ids.append(task_id)
            del tasks[task_id]
            print(f"Task ID {task_id} deleted.")
        else:
            print("Task ID not found.")
    
    elif choice == "DONE":
        try:
            task_id = int(input("Enter task ID to mark as done: "))
        except ValueError:
            print("Invalid task ID. Please enter a valid integer.")
            continue
        if task_id in tasks:
            tasks[task_id].completed = True
            history[task_id] = tasks[task_id]
            del tasks[task_id]
            print(f"Task ID {task_id} marked as done.")
        else:
            print("Task ID not found.")
    elif choice == "SEARCH":
        search_name = input("Enter task name to search: ")  
        found_tasks = [task for task in tasks.values() if search_name.lower() in task.name.lower()]
        if found_tasks:
            print(f"ID | NAME | PRIORITY | COMPLETED | DEADLINE")
            for task in found_tasks:
                print(f"{task.id} | {task.name} | {task.priority} | {task.completed} | {task.deadline}")
        else:
            print("No tasks found with that name.")
    elif choice == "EXIT":
        x=False
    elif choice == "HELP":
        print("Available commands:")
        print("CREATE - Create a new task")
        print("LIST - List all tasks")
        print("UPDATE - Update an existing task")
        print("DELETE - Delete a task")
        print("DONE - Mark a task as completed")
        print("SEARCH - Search for tasks by name")
        print("HISTORY - Show completed tasks")
        print("EXIT - Exit the task manager")
    elif choice == "HISTORY":
        if history:
            print(f"ID | NAME | PRIORITY | COMPLETED | DEADLINE")
            for task in history.values():
                print(f"{task.id} | {task.name} | {task.priority} | {task.completed} | {task.deadline}")
        else:
            print("No completed tasks.")
    else:
        print("Invalid command. Please try again.")
        print("Type 'help' to see the list of available commands.")

#write operation
task_dict = {}
for i in tasks:
    task = tasks[i]
    task_dict[task.id] = task.to_dict()
data = {
    "last_id": last_id,
    "history": {task.id: task.to_dict() for task in history.values()},
    "available_ids": available_ids,
    "tasks": task_dict
}
with open("task.json", "w") as f:
    json.dump(data, f, indent=4) 

