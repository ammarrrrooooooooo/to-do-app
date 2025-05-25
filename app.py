from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import re

app = Flask(__name__)

@dataclass
class Task:
    id: str
    title: str
    description: str
    creation_date: str
    due_date: str
    priority: str
    status: str
    tags: List[str]
    completion_date: Optional[str] = None

    def __init__(self, title: str, description: str, due_date: str, priority: str = "Medium", status: str = "Pending", tags: List[str] = None):
        self.id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.title = title
        self.description = description
        self.creation_date = datetime.now(timezone.utc).isoformat()
        self.due_date = due_date
        self.priority = priority
        self.status = status
        self.tags = tags or []
        self.completion_date = None

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        task = cls(
            title=data["title"],
            description=data["description"],
            due_date=data["due_date"],
            priority=data["priority"],
            status=data["status"],
            tags=data.get("tags", [])
        )
        task.id = data["id"]
        task.creation_date = data["creation_date"]
        task.completion_date = data.get("completion_date")
        return task

class TaskManager:
    def __init__(self):
        self.tasks: List[Task] = []
        # Update path for Replit
        self.filename = os.path.join(os.getcwd(), 'data', 'tasks.json')
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        self.load_tasks()

    def add_task(self, title: str, description: str, due_date: str, priority: str = "Medium", tags: List[str] = None) -> Dict:
        task = Task(title, description, due_date, priority, tags=tags)
        self.tasks.append(task)
        self.save_tasks()
        return task.to_dict()

    def get_tasks(self, status: str = None, search: str = None, sort_by: str = None) -> List[Dict]:
        filtered_tasks = self.tasks

        # Filter by status
        if status and status != "all":
            filtered_tasks = [task for task in filtered_tasks if task.status == status]

        # Search functionality
        if search:
            search = search.lower()
            filtered_tasks = [
                task for task in filtered_tasks
                if search in task.title.lower()
                or search in task.description.lower()
                or any(search in tag.lower() for tag in task.tags)
            ]

        # Sort functionality
        if sort_by:
            if sort_by == "date-desc":
                filtered_tasks.sort(key=lambda x: x.creation_date, reverse=True)
            elif sort_by == "date-asc":
                filtered_tasks.sort(key=lambda x: x.creation_date)
            elif sort_by == "priority-desc":
                priority_order = {"High": 3, "Medium": 2, "Low": 1}
                filtered_tasks.sort(key=lambda x: priority_order[x.priority], reverse=True)
            elif sort_by == "priority-asc":
                priority_order = {"High": 3, "Medium": 2, "Low": 1}
                filtered_tasks.sort(key=lambda x: priority_order[x.priority])
            elif sort_by == "due-date":
                filtered_tasks.sort(key=lambda x: x.due_date)

        return [task.to_dict() for task in filtered_tasks]

    def get_task(self, task_id: str) -> Optional[Dict]:
        for task in self.tasks:
            if task.id == task_id:
                return task.to_dict()
        return None

    def update_task(self, task_id: str, updates: Dict) -> Optional[Dict]:
        for task in self.tasks:
            if task.id == task_id:
                task.title = updates.get('title', task.title)
                task.description = updates.get('description', task.description)
                task.due_date = updates.get('due_date', task.due_date)
                task.priority = updates.get('priority', task.priority)
                task.tags = updates.get('tags', task.tags)
                self.save_tasks()
                return task.to_dict()
        return None

    def complete_task(self, task_id: str) -> Optional[Dict]:
        for task in self.tasks:
            if task.id == task_id:
                task.status = "Completed"
                task.completion_date = datetime.now(timezone.utc).isoformat()
                self.save_tasks()
                return task.to_dict()
        return None

    def delete_task(self, task_id: str) -> Optional[Dict]:
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                deleted_task = self.tasks.pop(i)
                self.save_tasks()
                return deleted_task.to_dict()
        return None

    def get_statistics(self) -> Dict:
        total_tasks = len(self.tasks)
        completed_tasks = len([task for task in self.tasks if task.status == "Completed"])
        active_tasks = total_tasks - completed_tasks
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "active_tasks": active_tasks,
            "completion_rate": round(completion_rate, 1)
        }

    def save_tasks(self) -> None:
        with open(self.filename, 'w', encoding='utf-8') as f:
            json_data = [task.to_dict() for task in self.tasks]
            json.dump(json_data, f, ensure_ascii=False, indent=2)

    def load_tasks(self) -> None:
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task_data) for task_data in data]
                except json.JSONDecodeError:
                    self.tasks = []

task_manager = TaskManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    status = request.args.get('status')
    search = request.args.get('search')
    sort_by = request.args.get('sort')
    return jsonify(task_manager.get_tasks(status, search, sort_by))

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    tags = [tag.strip() for tag in data.get('tags', '').split(',') if tag.strip()]
    task = task_manager.add_task(
        data['title'],
        data['description'],
        data['due_date'],
        data['priority'],
        tags
    )
    return jsonify(task)

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    task = task_manager.get_task(task_id)
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    if 'tags' in data:
        data['tags'] = [tag.strip() for tag in data['tags'].split(',') if tag.strip()]
    task = task_manager.update_task(task_id, data)
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/tasks/<task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    task = task_manager.complete_task(task_id)
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = task_manager.delete_task(task_id)
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    return jsonify(task_manager.get_statistics())

if __name__ == '__main__':
    # Get port from Replit environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Run with host='0.0.0.0' to make it accessible from Replit
    app.run(host='0.0.0.0', port=port)

# Add this for PythonAnywhere WSGI
application = app 