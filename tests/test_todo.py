"""TodoList クラスのテスト。

正常系・異常系・エッジケースを網羅する。

【確認済みバグ一覧】
  B1: load() でファイルが存在しない場合 FileNotFoundError が発生する
  B2: get_stats() でアイテム0件のとき ZeroDivisionError が発生する
  B3: delete() でIDが見つからない場合 False ではなく None を返す
  B4: complete() でIDが見つからない場合 None を返す
  B5: add() に空文字列タイトルを渡すと登録されてしまう
  B6: search() に None を渡すと TypeError が発生する
  B7: list_all() が内部リストへの参照を返すため外部から内部データが壊れる
"""

import json
import pytest
from src.todo import TodoList


# ---------------------------------------------------------------------------
# フィクスチャ
# ---------------------------------------------------------------------------

@pytest.fixture
def todo(tmp_path):
    """一時ファイルを使った空の TodoList を返す。"""
    filepath = str(tmp_path / "todos.json")
    with open(filepath, "w") as f:
        json.dump({"todos": [], "next_id": 1}, f)
    return TodoList(filepath=filepath)


@pytest.fixture
def todo_with_items(tmp_path):
    """3件のアイテムを追加済みの TodoList を返す。"""
    filepath = str(tmp_path / "todos.json")
    with open(filepath, "w") as f:
        json.dump({"todos": [], "next_id": 1}, f)
    tl = TodoList(filepath=filepath)
    tl.add("タスクA")
    tl.add("タスクB")
    tl.add("タスクC")
    return tl


# ===========================================================================
# 正常系テスト
# ===========================================================================

class TestAdd:
    """add() のテスト"""

    def test_追加するとidが1から採番される(self, todo):
        """add() を呼ぶと id=1 のアイテムが返ること"""
        item = todo.add("最初のタスク")
        assert item["id"] == 1
        assert item["title"] == "最初のタスク"
        assert item["done"] is False

    def test_複数追加すると連番でidが振られる(self, todo):
        """複数回 add() すると id が連番で増加すること"""
        item1 = todo.add("タスク1")
        item2 = todo.add("タスク2")
        item3 = todo.add("タスク3")
        assert item1["id"] == 1
        assert item2["id"] == 2
        assert item3["id"] == 3

    def test_追加直後のdoneはFalse(self, todo):
        """add() した直後のアイテムは done=False であること"""
        item = todo.add("未完了タスク")
        assert item["done"] is False


class TestListAll:
    """list_all() のテスト"""

    def test_空リストのとき空リストを返す(self, todo):
        """アイテムが0件の場合 list_all() は空リストを返すこと"""
        assert todo.list_all() == []

    def test_追加したアイテムが全件取得できる(self, todo_with_items):
        """3件追加後に list_all() で3件取得できること"""
        items = todo_with_items.list_all()
        assert len(items) == 3

    def test_追加した順序でアイテムが返る(self, todo):
        """list_all() は追加した順序でアイテムを返すこと"""
        todo.add("先に追加")
        todo.add("後に追加")
        items = todo.list_all()
        assert items[0]["title"] == "先に追加"
        assert items[1]["title"] == "後に追加"


class TestComplete:
    """complete() のテスト"""

    def test_存在するIDをcompleteするとdoneがTrueになる(self, todo):
        """complete() 後にアイテムの done が True になること"""
        item = todo.add("完了するタスク")
        result = todo.complete(item["id"])
        assert result is not None
        assert result["done"] is True

    def test_complete後もリストにアイテムが残る(self, todo):
        """complete() 後もアイテムは list_all() で取得できること"""
        item = todo.add("完了タスク")
        todo.complete(item["id"])
        assert len(todo.list_all()) == 1

    def test_completeは指定したIDのアイテムだけ完了にする(self, todo):
        """complete() は指定IDのアイテムのみ done=True にし、他は変更しないこと"""
        item1 = todo.add("タスク1")
        item2 = todo.add("タスク2")
        todo.complete(item1["id"])
        items = todo.list_all()
        assert items[0]["done"] is True
        assert items[1]["done"] is False


class TestDelete:
    """delete() のテスト"""

    def test_存在するIDをdeleteするとTrueを返す(self, todo):
        """delete() が成功すると True を返すこと"""
        item = todo.add("削除するタスク")
        result = todo.delete(item["id"])
        assert result is True

    def test_deleteするとリストからアイテムが消える(self, todo):
        """delete() 後にアイテムが list_all() から消えること"""
        item = todo.add("消えるタスク")
        todo.delete(item["id"])
        assert len(todo.list_all()) == 0

    def test_複数アイテムから指定IDだけ削除される(self, todo):
        """delete() は指定IDのアイテムのみ削除し、他はリストに残ること"""
        item1 = todo.add("残すタスク")
        item2 = todo.add("削除するタスク")
        todo.delete(item2["id"])
        remaining = todo.list_all()
        assert len(remaining) == 1
        assert remaining[0]["id"] == item1["id"]


class TestSearch:
    """search() のテスト"""

    def test_キーワードにマッチするアイテムを返す(self, todo):
        """search() はタイトルにキーワードを含むアイテムを返すこと"""
        todo.add("書類を整理する")
        todo.add("報告書を書く")
        todo.add("買い物リスト")
        result = todo.search("書")
        assert len(result) == 2

    def test_マッチしないキーワードのとき空リストを返す(self, todo):
        """search() でマッチするアイテムがない場合は空リストを返すこと"""
        todo.add("タスクA")
        result = todo.search("存在しないキーワード")
        assert result == []

    def test_空文字列で全件マッチする(self, todo):
        """search('') は全アイテムを返すこと（空文字列はすべてのタイトルに含まれる）"""
        todo.add("タスク1")
        todo.add("タスク2")
        result = todo.search("")
        assert len(result) == 2


class TestGetStats:
    """get_stats() のテスト"""

    def test_アイテムがある場合に正しい統計を返す(self, todo):
        """get_stats() が total/done/pending/rate を正しく計算すること"""
        todo.add("タスク1")
        item2 = todo.add("タスク2")
        todo.complete(item2["id"])
        stats = todo.get_stats()
        assert stats["total"] == 2
        assert stats["done"] == 1
        assert stats["pending"] == 1
        assert stats["rate"] == 0.5

    def test_全件完了のときrate1点0(self, todo):
        """全アイテム完了時に rate=1.0 が返ること"""
        item = todo.add("タスク")
        todo.complete(item["id"])
        stats = todo.get_stats()
        assert stats["rate"] == 1.0

    def test_完了なしのときrate0点0(self, todo):
        """完了アイテムが0件のとき rate=0.0 が返ること"""
        todo.add("タスク")
        stats = todo.get_stats()
        assert stats["rate"] == 0.0


# ===========================================================================
# 異常系・エッジケーステスト（バグの確認を含む）
# ===========================================================================

class TestLoadBug:
    """B1: load() のバグ確認"""

    def test_存在しないファイルでFileNotFoundErrorが発生する(self, tmp_path):
        """【バグB1】ファイルが存在しない場合 FileNotFoundError が発生すること"""
        filepath = str(tmp_path / "nonexistent.json")
        with pytest.raises(FileNotFoundError):
            TodoList(filepath=filepath)


class TestGetStatsBug:
    """B2: get_stats() のゼロ除算バグ確認"""

    @pytest.mark.xfail(raises=ZeroDivisionError, strict=True,
                       reason="【バグB2】アイテム0件のとき ZeroDivisionError が発生する既知バグ")
    def test_アイテム0件でget_statsを呼ぶとゼロ除算が発生する(self, todo):
        """【バグB2】アイテムが0件のとき get_stats() が ZeroDivisionError を発生させること"""
        todo.get_stats()


class TestDeleteEdgeCase:
    """B3: delete() が存在しないIDに対して None を返す問題"""

    def test_存在しないIDをdeleteするとNoneが返る(self, todo):
        """【バグB3】存在しないIDを delete() すると False ではなく None が返ること"""
        result = todo.delete(999)
        assert result is None

    def test_空リストに対してdeleteするとNoneが返る(self, todo):
        """【バグB3】アイテムが0件の状態で delete() すると None が返ること"""
        result = todo.delete(1)
        assert result is None

    def test_同じIDを2回deleteすると2回目はNoneが返る(self, todo):
        """【バグB3】削除済みIDを再度 delete() すると None が返ること"""
        item = todo.add("タスク")
        todo.delete(item["id"])
        result = todo.delete(item["id"])
        assert result is None


class TestCompleteEdgeCase:
    """B4: complete() が存在しないIDに対して None を返す問題"""

    def test_存在しないIDをcompleteするとNoneが返る(self, todo):
        """【バグB4】存在しないIDを complete() すると None が返ること"""
        result = todo.complete(999)
        assert result is None

    def test_空リストに対してcompleteするとNoneが返る(self, todo):
        """【バグB4】アイテムが0件の状態で complete() すると None が返ること"""
        result = todo.complete(1)
        assert result is None

    def test_削除済みIDをcompleteするとNoneが返る(self, todo):
        """【バグB4】削除済みアイテムのIDを complete() すると None が返ること"""
        item = todo.add("タスク")
        todo.delete(item["id"])
        result = todo.complete(item["id"])
        assert result is None


class TestAddEmptyTitle:
    """B5: add() に空文字列タイトルを渡す問題"""

    def test_空文字列タイトルが登録されてしまう(self, todo):
        """【バグB5】add('') を呼ぶと空タイトルのアイテムが登録されること"""
        item = todo.add("")
        assert item is not None
        assert item["title"] == ""
        assert len(todo.list_all()) == 1


class TestSearchNoneBug:
    """B6: search() に None を渡すと TypeError が発生する問題"""

    def test_Noneを渡すとTypeErrorが発生する(self, todo):
        """【バグB6】search(None) を呼ぶと TypeError が発生すること"""
        todo.add("タスク")
        with pytest.raises(TypeError):
            todo.search(None)


class TestListAllMutability:
    """B7: list_all() が内部リストへの参照を返す問題"""

    def test_返り値を変更すると内部データが破壊される(self, todo):
        """【バグB7】list_all() の返り値を clear() すると内部リストも空になること"""
        todo.add("タスク")
        returned = todo.list_all()
        returned.clear()
        assert len(todo.list_all()) == 0


# ===========================================================================
# 永続化（save/load）のテスト
# ===========================================================================

class TestPersistence:
    """save() と load() の連携テスト"""

    def test_addしたアイテムがファイルに保存される(self, tmp_path):
        """add() 後にファイルを再度ロードしても同じアイテムが取得できること"""
        filepath = str(tmp_path / "todos.json")
        with open(filepath, "w") as f:
            json.dump({"todos": [], "next_id": 1}, f)

        tl1 = TodoList(filepath=filepath)
        tl1.add("永続化タスク")

        tl2 = TodoList(filepath=filepath)
        items = tl2.list_all()
        assert len(items) == 1
        assert items[0]["title"] == "永続化タスク"

    def test_deleteしたアイテムがファイルにも反映される(self, tmp_path):
        """delete() 後にファイルを再ロードしても削除済みのアイテムが存在しないこと"""
        filepath = str(tmp_path / "todos.json")
        with open(filepath, "w") as f:
            json.dump({"todos": [], "next_id": 1}, f)

        tl1 = TodoList(filepath=filepath)
        item = tl1.add("削除するタスク")
        tl1.delete(item["id"])

        tl2 = TodoList(filepath=filepath)
        assert len(tl2.list_all()) == 0

    def test_completeしたアイテムがファイルに反映される(self, tmp_path):
        """complete() 後に再ロードすると done=True のアイテムが取得できること"""
        filepath = str(tmp_path / "todos.json")
        with open(filepath, "w") as f:
            json.dump({"todos": [], "next_id": 1}, f)

        tl1 = TodoList(filepath=filepath)
        item = tl1.add("完了タスク")
        tl1.complete(item["id"])

        tl2 = TodoList(filepath=filepath)
        assert tl2.list_all()[0]["done"] is True
