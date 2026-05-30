"""Todoリストを管理するモジュール"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TodoItem:
    id: int
    title: str
    done: bool = False


class TodoList:
    """Todoリストを管理するクラス"""

    def __init__(self) -> None:
        self._items: list[TodoItem] = []
        self._next_id: int = 1

    def add(self, title: str) -> TodoItem:
        """Todoを追加する"""
        item = TodoItem(id=self._next_id, title=title)
        self._items.append(item)
        self._next_id += 1
        return item

    def list_all(self) -> list[TodoItem]:
        """全Todoを返す"""
        return list(self._items)

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

    def _find(self, todo_id: int) -> Optional[TodoItem]:
        return next((i for i in self._items if i.id == todo_id), None)
