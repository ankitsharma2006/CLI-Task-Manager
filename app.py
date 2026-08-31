import json
from datetime import datetime

with open("task.json", "r") as f:
   data=json.load(f)

last_id = 0

def generate_id():
    global last_id
    last_id += 1
    return last_id

class Task:
  def __init__(self,name: str, priority: int, deadline: str):
    self.id = generate_id()
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
      task = cls(data["name"], data["priority"], data["deadline"])
      task.id = data["id"]
      task.completed = data["completed"]
      task.date_created = data["date_created"]
      return task

tasks={1: Task("Finish project", 1, "2026-12-31 18:00"),2: Task("Buy groceries", 2, "2026-09-15 12:00"),3: Task("Call mom", 3, "2026-09-01 20:00")}

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

