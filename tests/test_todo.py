"""TodoItemとTodoListのテスト"""

import pytest
from src.todo import TodoItem, TodoList


class TestTodoItem:
    """TodoItemデータクラスのテスト"""

    def test_デフォルト値が正しく設定される(self):
        """idとtitleのみ指定した場合、done=False・category=Noneになること"""
        item = TodoItem(id=1, title="タスク")
        assert item.id == 1
        assert item.title == "タスク"
        assert item.done is False
        assert item.category is None

    def test_全フィールドを明示的に指定できる(self):
        """全フィールドを明示的に指定して正しく格納されること"""
        item = TodoItem(id=5, title="買い物", done=True, category="プライベート")
        assert item.id == 5
        assert item.title == "買い物"
        assert item.done is True
        assert item.category == "プライベート"

    def test_デフォルトカテゴリはNone(self):
        """categoryを省略した場合、Noneになること"""
        item = TodoItem(id=1, title="タスク")
        assert item.category is None

    def test_カテゴリを設定できる(self):
        """categoryに文字列を設定できること"""
        item = TodoItem(id=1, title="タスク", category="仕事")
        assert item.category == "仕事"


class TestTodoListAdd:
    """TodoList.add() のテスト"""

    def test_カテゴリなしで追加できる(self):
        """categoryを省略してTodoを追加するとcategoryがNoneになること"""
        todo = TodoList()
        item = todo.add("タスク")
        assert item.category is None

    def test_カテゴリ付きで追加できる(self):
        """categoryを指定してTodoを追加するとcategoryが反映されること"""
        todo = TodoList()
        item = todo.add("報告書を書く", category="仕事")
        assert item.category == "仕事"

    def test_追加するとidが自動採番される(self):
        """複数追加した場合、idが1から連番で採番されること"""
        todo = TodoList()
        item1 = todo.add("タスクA")
        item2 = todo.add("タスクB")
        item3 = todo.add("タスクC")
        assert item1.id == 1
        assert item2.id == 2
        assert item3.id == 3

    def test_追加したアイテムのdoneはFalse(self):
        """追加直後のTodoItemはdone=Falseであること"""
        todo = TodoList()
        item = todo.add("未完了タスク")
        assert item.done is False

    def test_追加したアイテムがリストに存在する(self):
        """add後にlist_allで追加したアイテムが取得できること"""
        todo = TodoList()
        added = todo.add("確認タスク", category="確認")
        items = todo.list_all()
        assert len(items) == 1
        assert items[0].title == "確認タスク"
        assert items[0].id == added.id


class TestTodoListListAll:
    """TodoList.list_all() のテスト"""

    def test_空リストで全件取得すると空リストを返す(self):
        """アイテムが0件のとき、list_allは空リストを返すこと"""
        todo = TodoList()
        assert todo.list_all() == []

    def test_複数追加した後に全件取得できる(self):
        """複数のTodoを追加した後、list_allで全件取得できること"""
        todo = TodoList()
        todo.add("タスクA")
        todo.add("タスクB")
        items = todo.list_all()
        assert len(items) == 2
        assert items[0].title == "タスクA"
        assert items[1].title == "タスクB"

    def test_list_allは元のリストのコピーを返す(self):
        """list_allが返すリストを変更しても内部リストに影響しないこと"""
        todo = TodoList()
        todo.add("タスク")
        returned = todo.list_all()
        returned.clear()
        # 内部リストには影響しない
        assert len(todo.list_all()) == 1


class TestTodoListByCategory:
    """TodoList.list_by_category() のテスト"""

    def setup_method(self):
        """各テスト前に共通のTodoリストを用意する"""
        self.todo = TodoList()
        self.todo.add("報告書を書く", category="仕事")
        self.todo.add("買い物をする", category="プライベート")
        self.todo.add("会議の準備", category="仕事")
        self.todo.add("メモ")  # カテゴリなし

    def test_仕事カテゴリのみ返す(self):
        """list_by_category('仕事')で仕事カテゴリのアイテムのみ返ること"""
        items = self.todo.list_by_category("仕事")
        assert len(items) == 2
        assert all(i.category == "仕事" for i in items)

    def test_プライベートカテゴリのみ返す(self):
        """list_by_category('プライベート')でプライベートのアイテムのみ返ること"""
        items = self.todo.list_by_category("プライベート")
        assert len(items) == 1
        assert items[0].title == "買い物をする"

    def test_存在しないカテゴリは空リストを返す(self):
        """存在しないカテゴリを指定すると空リストが返ること"""
        items = self.todo.list_by_category("趣味")
        assert items == []

    def test_カテゴリなしのアイテムはNoneカテゴリ検索でヒットしない(self):
        """list_by_category('')では、categoryがNoneのアイテムはヒットしないこと"""
        # categoryがNoneのアイテムは空文字列検索でも返らない
        items = self.todo.list_by_category("")
        assert items == []


class TestTodoListComplete:
    """TodoList.complete() のテスト"""

    def setup_method(self):
        """各テスト前にTodoリストを用意する"""
        self.todo = TodoList()

    # --- 正常系 ---
    def test_正常_存在するIDのTodoをcompleteで完了にできる(self):
        """completeを呼んだTodoItemのdoneがTrueになること"""
        item = self.todo.add("レポート提出")
        result = self.todo.complete(item.id)
        assert result is not None
        assert result.done is True
        assert result.id == item.id

    def test_正常_complete後もlist_allに残る(self):
        """completeした後もlist_allでアイテムが取得できること"""
        item = self.todo.add("完了タスク")
        self.todo.complete(item.id)
        items = self.todo.list_all()
        assert len(items) == 1
        assert items[0].done is True

    def test_正常_completeは対象アイテムのみ完了にする(self):
        """completeで指定したID以外のdoneは変化しないこと"""
        item1 = self.todo.add("タスク1")
        item2 = self.todo.add("タスク2")
        self.todo.complete(item1.id)
        assert item1.done is True
        assert item2.done is False

    # --- 異常系 ---
    def test_異常_存在しないIDをcompleteするとNoneを返す(self):
        """存在しないIDを指定するとcompleteがNoneを返すこと"""
        result = self.todo.complete(999)
        assert result is None

    def test_異常_空リストに対してcompleteするとNoneを返す(self):
        """アイテムが0件の状態でcompleteするとNoneを返すこと"""
        result = self.todo.complete(1)
        assert result is None

    def test_異常_削除済みIDをcompleteするとNoneを返す(self):
        """削除したアイテムのIDを指定するとcompleteがNoneを返すこと"""
        item = self.todo.add("削除後に完了を試みるタスク")
        self.todo.delete(item.id)
        result = self.todo.complete(item.id)
        assert result is None


class TestTodoListDelete:
    """TodoList.delete() のテスト"""

    def setup_method(self):
        """各テスト前にTodoリストを用意する"""
        self.todo = TodoList()

    # --- 正常系 ---
    def test_正常_存在するIDのTodoをdeleteで削除できる(self):
        """deleteが成功するとTrueを返し、リストからアイテムが消えること"""
        item = self.todo.add("削除するタスク")
        deleted = self.todo.delete(item.id)
        assert deleted is True
        assert len(self.todo.list_all()) == 0

    def test_正常_複数アイテムから対象のみ削除される(self):
        """deleteで指定したID以外のアイテムはリストに残ること"""
        item1 = self.todo.add("残すタスク")
        item2 = self.todo.add("削除するタスク")
        self.todo.delete(item2.id)
        remaining = self.todo.list_all()
        assert len(remaining) == 1
        assert remaining[0].id == item1.id

    def test_正常_削除後に新しいアイテムを追加できる(self):
        """deleteで削除した後、新しいアイテムを追加できること"""
        item = self.todo.add("削除対象")
        self.todo.delete(item.id)
        new_item = self.todo.add("新しいタスク")
        assert len(self.todo.list_all()) == 1
        assert new_item.title == "新しいタスク"

    # --- 異常系 ---
    def test_異常_存在しないIDをdeleteするとFalseを返す(self):
        """存在しないIDを指定するとdeleteがFalseを返すこと"""
        result = self.todo.delete(999)
        assert result is False

    def test_異常_空リストに対してdeleteするとFalseを返す(self):
        """アイテムが0件の状態でdeleteするとFalseを返すこと"""
        result = self.todo.delete(1)
        assert result is False

    def test_異常_同じIDを2回deleteすると2回目はFalseを返す(self):
        """同じIDを2回deleteすると、2回目はFalseを返すこと"""
        item = self.todo.add("二重削除テスト")
        self.todo.delete(item.id)
        result = self.todo.delete(item.id)
        assert result is False


class TestTodoListStr:
    """TodoList.__str__() のテスト"""

    def test_空リストのとき専用メッセージを返す(self):
        """アイテムが0件のとき、「Todoリストは空です」を返すこと"""
        todo = TodoList()
        assert str(todo) == "Todoリストは空です"

    def test_カテゴリが文字列に含まれる(self):
        """categoryを持つアイテムは文字列中に[カテゴリ]が表示されること"""
        todo = TodoList()
        todo.add("報告書を書く", category="仕事")
        assert "[仕事]" in str(todo)

    def test_カテゴリなしはブラケットなし(self):
        """categoryがNoneのアイテムは文字列中にカテゴリ用ブラケットが表示されないこと"""
        todo = TodoList()
        todo.add("メモ")
        result = str(todo)
        # IDの[1]のみが含まれ、カテゴリブラケットは含まれない
        assert "[" not in result or result.count("[") == 1

    def test_完了済みにはチェックマークとカテゴリ両方表示(self):
        """完了済みアイテムはチェックマークとカテゴリが両方表示されること"""
        todo = TodoList()
        item = todo.add("タスク", category="仕事")
        todo.complete(item.id)
        result = str(todo)
        assert "✓" in result
        assert "[仕事]" in result

    def test_未完了アイテムにはチェックマークが表示されない(self):
        """未完了アイテムの文字列にはチェックマークが含まれないこと"""
        todo = TodoList()
        todo.add("未完了タスク")
        result = str(todo)
        assert "✓" not in result
        assert "未完了" in result

    def test_複数アイテムが改行区切りで表示される(self):
        """複数アイテムは改行区切りで表示されること"""
        todo = TodoList()
        todo.add("タスクA")
        todo.add("タスクB")
        result = str(todo)
        lines = result.split("\n")
        assert len(lines) == 2
