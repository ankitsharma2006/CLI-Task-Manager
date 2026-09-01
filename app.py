import json
from datetime import datetime

#read operation
#with open("task.json", "r") as f:
   #data=json.load(f)

last_id = 0

def generate_id():
    global last_id
    last_id += 1
    return last_id

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
  
tasks = {}
# for i in data["tasks"]:
#     task_data = data["tasks"][i]
#     task = Task.from_dict(task_data)
#     tasks[task.id] = task

x=True
print("Welcome to the Task Manager!")
while x:
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Exit")
    choice = input("Enter your choice: ")
    
    if choice == "1":
        name = input("Enter task name: ")
        priority = int(input("Enter task priority (1-3): "))
        deadline = input("Enter task deadline (YYYY-MM-DD): ")
        task = Task(name, priority, deadline)
        tasks[task.id] = task
        print(f"Task '{task.name}' added with ID {task.id}.")
    
    elif choice == "2":
        for task in tasks.values():
            print(f"ID: {task.id}, Name: {task.name}, Priority: {task.priority}, Completed: {task.completed}, Deadline: {task.deadline}")
    
    elif choice == "3":
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
    
    elif choice == "4":
        task_id = int(input("Enter task ID to delete: "))
        if task_id in tasks:
            del tasks[task_id]
            print(f"Task ID {task_id} deleted.")
        else:
            print("Task ID not found.")
    
    elif choice == "5":
        x=False
    else:
        print("Invalid choice. Please try again.")

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

