import datetime
import json
from typing import List, Dict
import os

class Task:
    def __init__(self, title: str, description: str, due_date: str, priority: str = "Medium", status: str = "Pending"):
        self.title = title
        self.description = description
        self.creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.due_date = due_date
        self.priority = priority
        self.status = status
        self.completion_date = None

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "description": self.description,
            "creation_date": self.creation_date,
            "due_date": self.due_date,
            "priority": self.priority,
            "status": self.status,
            "completion_date": self.completion_date
        }

    @classmethod
    def from_dict(cls, data: Dict):
        task = cls(
            title=data["title"],
            description=data["description"],
            due_date=data["due_date"],
            priority=data["priority"],
            status=data["status"]
        )
        task.creation_date = data["creation_date"]
        task.completion_date = data["completion_date"]
        return task

class TaskManager:
    def __init__(self):
        self.tasks: List[Task] = []
        self.filename = "tasks.json"
        self.load_tasks()

    def add_task(self, title: str, description: str, due_date: str, priority: str = "Medium") -> None:
        """إضافة مهمة جديدة"""
        task = Task(title, description, due_date, priority)
        self.tasks.append(task)
        self.save_tasks()
        print(f"\n✅ تمت إضافة المهمة: {title}")

    def complete_task(self, task_index: int) -> None:
        """تحديد مهمة كمكتملة"""
        if 0 <= task_index < len(self.tasks):
            task = self.tasks[task_index]
            task.status = "Completed"
            task.completion_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_tasks()
            print(f"\n✅ تم إكمال المهمة: {task.title}")
        else:
            print("\n❌ رقم المهمة غير صحيح")

    def delete_task(self, task_index: int) -> None:
        """حذف مهمة"""
        if 0 <= task_index < len(self.tasks):
            deleted_task = self.tasks.pop(task_index)
            self.save_tasks()
            print(f"\n🗑️ تم حذف المهمة: {deleted_task.title}")
        else:
            print("\n❌ رقم المهمة غير صحيح")

    def list_tasks(self, filter_status: str = None) -> None:
        """عرض قائمة المهام"""
        if not self.tasks:
            print("\n📝 لا توجد مهام حالياً")
            return

        filtered_tasks = self.tasks
        if filter_status:
            filtered_tasks = [task for task in self.tasks if task.status == filter_status]

        print("\n=== قائمة المهام ===")
        for i, task in enumerate(filtered_tasks):
            print(f"\nمهمة {i + 1}:")
            print(f"العنوان: {task.title}")
            print(f"الوصف: {task.description}")
            print(f"تاريخ الإنشاء: {task.creation_date}")
            print(f"تاريخ الاستحقاق: {task.due_date}")
            print(f"الأولوية: {task.priority}")
            print(f"الحالة: {task.status}")
            if task.completion_date:
                print(f"تاريخ الإكمال: {task.completion_date}")
            print("-" * 30)

    def save_tasks(self) -> None:
        """حفظ المهام في ملف"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json_data = [task.to_dict() for task in self.tasks]
            json.dump(json_data, f, ensure_ascii=False, indent=2)

    def load_tasks(self) -> None:
        """تحميل المهام من الملف"""
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task_data) for task_data in data]
                except json.JSONDecodeError:
                    self.tasks = []

def main():
    task_manager = TaskManager()
    
    while True:
        print("\n=== نظام إدارة المهام ===")
        print("1. إضافة مهمة جديدة")
        print("2. عرض جميع المهام")
        print("3. عرض المهام المعلقة")
        print("4. عرض المهام المكتملة")
        print("5. إكمال مهمة")
        print("6. حذف مهمة")
        print("0. خروج")

        choice = input("\nالرجاء اختيار رقم العملية: ")

        if choice == "1":
            title = input("\nعنوان المهمة: ")
            description = input("وصف المهمة: ")
            due_date = input("تاريخ الاستحقاق (YYYY-MM-DD): ")
            priority = input("الأولوية (High/Medium/Low): ").capitalize()
            task_manager.add_task(title, description, due_date, priority)

        elif choice == "2":
            task_manager.list_tasks()

        elif choice == "3":
            task_manager.list_tasks("Pending")

        elif choice == "4":
            task_manager.list_tasks("Completed")

        elif choice == "5":
            task_manager.list_tasks("Pending")
            task_index = int(input("\nأدخل رقم المهمة لإكمالها: ")) - 1
            task_manager.complete_task(task_index)

        elif choice == "6":
            task_manager.list_tasks()
            task_index = int(input("\nأدخل رقم المهمة لحذفها: ")) - 1
            task_manager.delete_task(task_index)

        elif choice == "0":
            print("\n👋 شكراً لاستخدام نظام إدارة المهام!")
            break

        else:
            print("\n❌ اختيار غير صحيح، الرجاء المحاولة مرة أخرى")

if __name__ == "__main__":
    main() 