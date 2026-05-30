"""Todoリストを管理するモジュール"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TodoItem:
    id: int
    title: str
    done: bool = False
    category: Optional[str] = None


class TodoList:
    """Todoリストを管理するクラス"""

    def __init__(self) -> None:
        self._items: list[TodoItem] = []
        self._next_id: int = 1

    def add(self, title: str, category: Optional[str] = None) -> TodoItem:
        """Todoを追加する"""
        item = TodoItem(id=self._next_id, title=title, category=category)
        self._items.append(item)
        self._next_id += 1
        return item

    def list_all(self) -> list[TodoItem]:
        """全Todoを返す"""
        return list(self._items)

    def list_by_category(self, category: str) -> list[TodoItem]:
        """指定カテゴリのTodoを返す"""
        return [i for i in self._items if i.category == category]

    def complete(self, todo_id: int) -> Optional[TodoItem]:
        """指定IDのTodoを完了にする。見つからない場合はNoneを返す"""
        item = self._find(todo_id)
        if item is not None:
            item.done = True
        return item

    def delete(self, todo_id: int) -> bool:
        """指定IDのTodoを削除する。削除できた場合はTrueを返す"""
        item = self._find(todo_id)
        if item is None:
            return False
        self._items.remove(item)
        return True

    def __str__(self) -> str:
        """TodoListの中身を文字列で返す"""
        if not self._items:
            return "Todoリストは空です"
        lines = []
        for item in self._items:
            mark = "✓ " if item.done else "  "
            status = "完了" if item.done else "未完了"
            cat = f" [{item.category}]" if item.category else ""
            lines.append(f"{mark}[{item.id}] {item.title}{cat} ({status})")
        return "\n".join(lines)

    def _find(self, todo_id: int) -> Optional[TodoItem]:
        return next((i for i in self._items if i.id == todo_id), None)
