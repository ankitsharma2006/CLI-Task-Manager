import json
from datetime import datetime

#read operation
with open("task.json", "r") as f:
   data=json.load(f)

last_id = data["last_id"]

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
for i in data["tasks"]:
    task_data = data["tasks"][i]
    task = Task.from_dict(task_data)
    tasks[task.id] = task

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

