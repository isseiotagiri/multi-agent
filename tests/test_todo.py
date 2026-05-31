"""todo.py モジュールのテスト"""

import pytest
import sys
import os

# src ディレクトリをパスに追加する
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from todo import AlreadyDoneError, TodoItem, TodoList


# ─────────────────────────────────────────────
# フィクスチャ
# ─────────────────────────────────────────────

@pytest.fixture
def todo_list() -> TodoList:
    """各テスト用に空の TodoList を返すフィクスチャ"""
    return TodoList()


# ─────────────────────────────────────────────
# 正常系: add
# ─────────────────────────────────────────────

class TestAdd:
    def test_通常のタイトルでアイテムを追加できる(self, todo_list: TodoList) -> None:
        """add に有効なタイトルを渡すと TodoItem が返り、リストに追加される"""
        アイテム = todo_list.add("牛乳を買う")
        assert アイテム.id == 1
        assert アイテム.title == "牛乳を買う"
        assert アイテム.done is False
        assert アイテム.category is None

    def test_前後の空白はtrimされる(self, todo_list: TodoList) -> None:
        """add のタイトルは strip() されて保存される"""
        アイテム = todo_list.add("  掃除機をかける  ")
        assert アイテム.title == "掃除機をかける"

    def test_カテゴリを指定して追加できる(self, todo_list: TodoList) -> None:
        """add に category を渡すと TodoItem の category に設定される"""
        アイテム = todo_list.add("読書する", category="趣味")
        assert アイテム.category == "趣味"

    def test_カテゴリの前後空白はtrimされる(self, todo_list: TodoList) -> None:
        """category の前後空白は strip() されて保存される"""
        アイテム = todo_list.add("映画を見る", category="  エンタメ  ")
        assert アイテム.category == "エンタメ"

    def test_カテゴリに空白文字列を渡すとNoneになる(self, todo_list: TodoList) -> None:
        """カテゴリに空白文字列を渡すと None として扱われる（指摘事項7）"""
        アイテム = todo_list.add("散歩する", category="   ")
        assert アイテム.category is None

    def test_複数追加するとIDが連番になる(self, todo_list: TodoList) -> None:
        """add を複数回呼ぶと ID が 1, 2, 3 ... と増える"""
        a1 = todo_list.add("タスク1")
        a2 = todo_list.add("タスク2")
        a3 = todo_list.add("タスク3")
        assert a1.id == 1
        assert a2.id == 2
        assert a3.id == 3

    def test_ちょうど200文字のタイトルは追加できる(self, todo_list: TodoList) -> None:
        """境界値: タイトルが200文字ちょうどの場合は ValueError にならない"""
        タイトル = "あ" * 200
        アイテム = todo_list.add(タイトル)
        assert len(アイテム.title) == 200


# ─────────────────────────────────────────────
# 異常系: add
# ─────────────────────────────────────────────

class TestAddError:
    def test_空文字列のタイトルはValueErrorになる(self, todo_list: TodoList) -> None:
        """空文字列を渡すと ValueError が発生する（指摘事項1）"""
        with pytest.raises(ValueError, match="タイトルは空にできません"):
            todo_list.add("")

    def test_空白のみのタイトルはValueErrorになる(self, todo_list: TodoList) -> None:
        """空白のみのタイトルを渡すと ValueError が発生する（指摘事項1）"""
        with pytest.raises(ValueError, match="タイトルは空にできません"):
            todo_list.add("   ")

    def test_201文字のタイトルはValueErrorになる(self, todo_list: TodoList) -> None:
        """タイトルが201文字（上限超過）の場合に ValueError が発生する（指摘事項2）"""
        タイトル = "あ" * 201
        with pytest.raises(ValueError, match="200文字以内"):
            todo_list.add(タイトル)

    def test_大幅に超えたタイトルもValueErrorになる(self, todo_list: TodoList) -> None:
        """タイトルが大幅に長い場合でも ValueError が発生する（境界値外）"""
        タイトル = "x" * 1000
        with pytest.raises(ValueError):
            todo_list.add(タイトル)


# ─────────────────────────────────────────────
# 正常系: list_all / list_by_category
# ─────────────────────────────────────────────

class TestList:
    def test_空リストのlist_allは空リストを返す(self, todo_list: TodoList) -> None:
        """アイテムが無いとき list_all は空リストを返す"""
        assert todo_list.list_all() == []

    def test_追加したアイテムがlist_allで取得できる(self, todo_list: TodoList) -> None:
        """add したアイテムが list_all に含まれる"""
        todo_list.add("タスクA")
        todo_list.add("タスクB")
        全件 = todo_list.list_all()
        assert len(全件) == 2
        タイトル一覧 = [i.title for i in 全件]
        assert "タスクA" in タイトル一覧
        assert "タスクB" in タイトル一覧

    def test_list_allの戻り値を変更しても内部状態は変わらない(self, todo_list: TodoList) -> None:
        """list_all の戻り値リストを操作しても内部 dict は影響を受けない（指摘事項5）"""
        todo_list.add("タスクA")
        取得リスト = todo_list.list_all()
        取得リスト.clear()  # 外部リストをクリアする
        assert len(todo_list.list_all()) == 1  # 内部は変わっていないこと

    def test_frozenなアイテムのフィールドは変更できない(self, todo_list: TodoList) -> None:
        """frozen=True により TodoItem のフィールド書き換えは FrozenInstanceError になる（指摘事項5）"""
        アイテム = todo_list.add("変更不可タスク")
        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError は Exception のサブクラス
            アイテム.title = "書き換え"  # type: ignore[misc]

    def test_カテゴリでフィルタできる(self, todo_list: TodoList) -> None:
        """list_by_category は指定カテゴリのアイテムだけ返す"""
        todo_list.add("仕事A", category="仕事")
        todo_list.add("趣味A", category="趣味")
        todo_list.add("仕事B", category="仕事")
        仕事一覧 = todo_list.list_by_category("仕事")
        assert len(仕事一覧) == 2
        assert all(i.category == "仕事" for i in 仕事一覧)

    def test_存在しないカテゴリは空リストを返す(self, todo_list: TodoList) -> None:
        """存在しないカテゴリを指定すると空リストが返る"""
        todo_list.add("タスク", category="仕事")
        assert todo_list.list_by_category("存在しないカテゴリ") == []


# ─────────────────────────────────────────────
# 正常系: complete
# ─────────────────────────────────────────────

class TestComplete:
    def test_未完了のアイテムを完了にできる(self, todo_list: TodoList) -> None:
        """complete を呼ぶと done=True の新しい TodoItem が返る"""
        追加済み = todo_list.add("完了するタスク")
        完了済み = todo_list.complete(追加済み.id)
        assert 完了済み.done is True
        assert 完了済み.id == 追加済み.id
        assert 完了済み.title == 追加済み.title

    def test_complete後にlist_allでもdoneがTrueになっている(self, todo_list: TodoList) -> None:
        """complete 後、list_all で取得しても done=True が反映されている"""
        アイテム = todo_list.add("確認タスク")
        todo_list.complete(アイテム.id)
        全件 = todo_list.list_all()
        assert 全件[0].done is True


# ─────────────────────────────────────────────
# 異常系: complete
# ─────────────────────────────────────────────

class TestCompleteError:
    def test_存在しないIDにcompleteするとKeyErrorになる(self, todo_list: TodoList) -> None:
        """存在しない ID に complete すると KeyError が発生する（指摘事項3）"""
        with pytest.raises(KeyError):
            todo_list.complete(999)

    def test_既完了アイテムにcompleteするとAlreadyDoneErrorになる(self, todo_list: TodoList) -> None:
        """already done のアイテムに complete すると AlreadyDoneError が発生する（指摘事項4）"""
        アイテム = todo_list.add("二重完了タスク")
        todo_list.complete(アイテム.id)
        with pytest.raises(AlreadyDoneError):
            todo_list.complete(アイテム.id)


# ─────────────────────────────────────────────
# 正常系 / 異常系: delete
# ─────────────────────────────────────────────

class TestDelete:
    def test_存在するIDを削除するとTrueが返る(self, todo_list: TodoList) -> None:
        """存在する ID を delete するとTrueが返りアイテムが消える"""
        アイテム = todo_list.add("削除対象")
        結果 = todo_list.delete(アイテム.id)
        assert 結果 is True

    def test_削除後にlist_allに含まれない(self, todo_list: TodoList) -> None:
        """delete 後、list_all に該当アイテムが含まれない"""
        アイテム = todo_list.add("削除後確認")
        todo_list.delete(アイテム.id)
        assert todo_list.list_all() == []

    def test_削除後にfindがNoneを返す(self, todo_list: TodoList) -> None:
        """delete 後、_find で同IDを検索すると None が返る（指摘事項6）"""
        アイテム = todo_list.add("_find確認")
        todo_list.delete(アイテム.id)
        assert todo_list._find(アイテム.id) is None

    def test_存在しないIDを削除するとFalseが返る(self, todo_list: TodoList) -> None:
        """存在しない ID を delete すると False が返る"""
        結果 = todo_list.delete(999)
        assert 結果 is False

    def test_削除後に同じIDでcompleteするとKeyErrorになる(self, todo_list: TodoList) -> None:
        """delete したアイテムのIDに complete すると KeyError が発生する"""
        アイテム = todo_list.add("削除後complete確認")
        todo_list.delete(アイテム.id)
        with pytest.raises(KeyError):
            todo_list.complete(アイテム.id)


# ─────────────────────────────────────────────
# 正常系: __str__
# ─────────────────────────────────────────────

class TestStr:
    def test_空リストの文字列表現(self, todo_list: TodoList) -> None:
        """アイテムが無いとき __str__ は空リストメッセージを返す"""
        assert str(todo_list) == "Todoリストは空です"

    def test_未完了アイテムの文字列表現に未完了が含まれる(self, todo_list: TodoList) -> None:
        """未完了アイテムが文字列に '未完了' として含まれる"""
        todo_list.add("未完了タスク")
        assert "未完了" in str(todo_list)

    def test_完了アイテムの文字列表現に完了が含まれる(self, todo_list: TodoList) -> None:
        """complete したアイテムが文字列に '完了' として含まれる"""
        アイテム = todo_list.add("完了タスク")
        todo_list.complete(アイテム.id)
        assert "完了" in str(todo_list)

    def test_カテゴリ付きアイテムの文字列表現にカテゴリが含まれる(self, todo_list: TodoList) -> None:
        """category を設定したアイテムが文字列中に [カテゴリ名] 形式で表示される"""
        todo_list.add("カテゴリ付きタスク", category="仕事")
        assert "[仕事]" in str(todo_list)
