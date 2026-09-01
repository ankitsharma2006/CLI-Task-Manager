import json
import os
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
      task.id = data["id"]
      task.completed = data["completed"]
      task.date_created = data["date_created"]
      return task
  
#read operation
try:
  with open("task.json", "r") as f:
    data=json.load(f)

  last_id = data["last_id"]

  tasks = {}
  for i in data["tasks"]:
      task_data = data["tasks"][i]
      task = Task.from_dict(task_data)
      tasks[task.id] = task

except (FileNotFoundError, json.JSONDecodeError):
  last_id = 0
  tasks = {}

def generate_id():
    global last_id
    last_id += 1
    return last_id

x=True
print("Welcome to the Task Manager!")
while x:
    print("CREATE Task")
    print("LIST Tasks")
    print("UPDATE Task")
    print("DELETE Task")
    print("DONE Task")
    print("SEARCH Task")
    print("EXIT the task manager")
    choice = input("Enter command: ").upper()
    
    if choice == "CREATE":
        name = input("Enter task name: ")
        priority = int(input("Enter task priority (1-3): "))
        deadline = input("Enter task deadline (YYYY-MM-DD): ")
        task = Task(name, priority, deadline)
        tasks[task.id] = task
        print(f"Task '{task.name}' added with ID {task.id}.")
    
    elif choice == "LIST":
        print(f"ID | NAME | PRIORITY | COMPLETED | DEADLINE")
        for task in tasks.values():
            print(f"{task.id} | {task.name} | {task.priority} | {task.completed} | {task.deadline}")
    
    elif choice == "UPDATE":
        task_id = int(input("Enter task ID to update: "))
        update=int(input("Enter 1 to update name, 2 to update priority, 3 to update deadline, 4 to update completed status, 5 to update all: "))
        if task_id in tasks:
            task = tasks[task_id]
            if update == 1:
                task.name = input(f"Enter new name (current: {task.name}): ") or task.name
            elif update == 2:
                task.priority = int(input(f"Enter new priority (current: {task.priority}): ") or task.priority)
            elif update == 3:
                task.deadline = input(f"Enter new deadline (current: {task.deadline}): ") or task.deadline
            elif update == 4:
                completed_input = input(f"Is the task completed? (yes/no, current: {'yes' if task.completed else 'no'}): ")
                if completed_input.lower() == 'yes':
                    task.completed = True
                elif completed_input.lower() == 'no':
                    task.completed = False
            elif update == 5:
                task.name = input(f"Enter new name (current: {task.name}): ") or task.name
                task.priority = int(input(f"Enter new priority (current: {task.priority}): ") or task.priority)
                task.deadline = input(f"Enter new deadline (current: {task.deadline}): ") or task.deadline
                completed_input = input(f"Is the task completed? (yes/no, current: {'yes' if task.completed else 'no'}): ")
                if completed_input.lower() == 'yes':
                    task.completed = True
                elif completed_input.lower() == 'no':
                    task.completed = False
            print(f"Task ID {task.id} updated.")
        else:
            print("Task ID not found.")
    
    elif choice == "DELETE":
        task_id = int(input("Enter task ID to delete: "))
        if task_id in tasks:
            del tasks[task_id]
            print(f"Task ID {task_id} deleted.")
        else:
            print("Task ID not found.")
    
    elif choice == "DONE":
        task_id = int(input("Enter task ID to mark as done: "))
        if task_id in tasks:
            tasks[task_id].completed = True
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
    else:
        print("Invalid command. Please try again.")

#write operation
task_dict = {}
for i in tasks:
    task = tasks[i]
    task_dict[task.id] = task.to_dict()
data = {
    "last_id": last_id,
    "tasks": task_dict
}
with open("task.json", "w") as f:
    json.dump(data, f, indent=4) 

