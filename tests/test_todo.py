"""TodoItemとTodoListのテスト"""

import pytest
from src.todo import TodoItem, TodoList


class TestTodoItemCategory:
    def test_デフォルトカテゴリはNone(self):
        item = TodoItem(id=1, title="タスク")
        assert item.category is None

    def test_カテゴリを設定できる(self):
        item = TodoItem(id=1, title="タスク", category="仕事")
        assert item.category == "仕事"


class TestTodoListAdd:
    def test_カテゴリなしで追加できる(self):
        todo = TodoList()
        item = todo.add("タスク")
        assert item.category is None

    def test_カテゴリ付きで追加できる(self):
        todo = TodoList()
        item = todo.add("報告書を書く", category="仕事")
        assert item.category == "仕事"


class TestTodoListByCategory:
    def setup_method(self):
        self.todo = TodoList()
        self.todo.add("報告書を書く", category="仕事")
        self.todo.add("買い物をする", category="プライベート")
        self.todo.add("会議の準備", category="仕事")
        self.todo.add("メモ")

    def test_仕事カテゴリのみ返す(self):
        items = self.todo.list_by_category("仕事")
        assert len(items) == 2
        assert all(i.category == "仕事" for i in items)

    def test_プライベートカテゴリのみ返す(self):
        items = self.todo.list_by_category("プライベート")
        assert len(items) == 1
        assert items[0].title == "買い物をする"

    def test_存在しないカテゴリは空リストを返す(self):
        items = self.todo.list_by_category("趣味")
        assert items == []


class TestTodoListStr:
    def test_カテゴリが文字列に含まれる(self):
        todo = TodoList()
        todo.add("報告書を書く", category="仕事")
        assert "[仕事]" in str(todo)

    def test_カテゴリなしはブラケットなし(self):
        todo = TodoList()
        todo.add("メモ")
        result = str(todo)
        assert "[" not in result or result.count("[") == 1  # IDの[1]のみ

    def test_完了済みにはチェックマークとカテゴリ両方表示(self):
        todo = TodoList()
        item = todo.add("タスク", category="仕事")
        todo.complete(item.id)
        result = str(todo)
        assert "✓" in result
        assert "[仕事]" in result
