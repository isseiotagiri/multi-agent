"""Todoリストを管理するモジュール。

このモジュールは、シンプルなTodoリストの作成・取得・更新・削除（CRUD）機能を提供する。

提供するクラス:
    TodoItem: 1件のTodoアイテムを表す不変データクラス。
    AlreadyDoneError: 既完了のTodoに対して complete を呼んだ場合に送出される例外。
    TodoList: Todoアイテムを管理するクラス。追加・取得・完了・削除の操作をサポートする。
"""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class TodoItem:
    """1件のTodoアイテムを表す不変データクラス。

    ``frozen=True`` により、インスタンス生成後に属性を直接変更することはできない。
    完了状態の更新など値を変える場合は ``dataclasses.replace`` を使って新しい
    インスタンスを生成する。

    Attributes:
        id: アイテムを一意に識別する正の整数。``TodoList`` が自動で採番する。
        title: タスクの内容を表す文字列。前後の空白はトリム済みで保存される。
            空文字または200文字超は許可されない。
        done: 完了フラグ。``True`` のとき完了済み。デフォルトは ``False``。
        category: タスクのカテゴリを表す任意の文字列。
            未設定の場合または空白文字列が渡された場合は ``None``。

    Example:
        >>> item = TodoItem(id=1, title="牛乳を買う")
        >>> item.id
        1
        >>> item.done
        False
        >>> item.category is None
        True
    """

    id: int
    title: str
    done: bool = False
    category: str | None = None


class AlreadyDoneError(Exception):
    """既に完了済みのTodoに対して complete を呼んだ場合に送出される例外。

    ``Exception`` のサブクラスとして定義されており、
    ``TodoList.complete`` 内で ``done=True`` のアイテムへの再完了操作を検知した際に
    送出される。

    Example:
        >>> todo_list = TodoList()
        >>> item = todo_list.add("テストタスク")
        >>> todo_list.complete(item.id)  # 1回目は成功
        TodoItem(...)
        >>> todo_list.complete(item.id)  # 2回目は AlreadyDoneError
        Traceback (most recent call last):
            ...
        AlreadyDoneError: ID 1 のTodoは既に完了しています
    """


class TodoList:
    """Todoアイテムを管理するクラス。

    内部ストレージとして ``dict[int, TodoItem]`` を使用することで、
    IDによる検索・削除を O(1) で行う。IDは追加のたびに自動採番される（1から連番）。

    Attributes:
        MAX_TITLE_LENGTH (int): タイトルの最大文字数。200文字固定。

    Example:
        >>> tl = TodoList()

        # アイテムの追加
        >>> item = tl.add("買い物をする", category="家事")
        >>> item.id
        1
        >>> item.title
        '買い物をする'
        >>> item.category
        '家事'

        # 一覧取得
        >>> tl.add("レポートを書く", category="仕事")
        TodoItem(id=2, title='レポートを書く', done=False, category='仕事')
        >>> all_items = tl.list_all()
        >>> len(all_items)
        2

        # カテゴリフィルタ
        >>> 家事リスト = tl.list_by_category("家事")
        >>> len(家事リスト)
        1

        # 完了にする
        >>> done_item = tl.complete(1)
        >>> done_item.done
        True

        # 削除する
        >>> tl.delete(2)
        True
        >>> len(tl.list_all())
        1

        # 文字列表現
        >>> print(tl)
        ✓ [1] 買い物をする [家事] (完了)
    """

    MAX_TITLE_LENGTH = 200

    def __init__(self) -> None:
        """TodoList を初期化する。

        内部ストレージ（空の辞書）と次に使うIDカウンタを初期化する。
        """
        self._items: dict[int, TodoItem] = {}
        self._next_id: int = 1

    def add(self, title: str, category: str | None = None) -> TodoItem:
        """Todoアイテムを追加して返す。

        タイトルは前後の空白がトリムされて保存される。
        カテゴリも同様にトリムされ、空白文字列のみの場合は ``None`` として扱われる。

        Args:
            title: タスクのタイトル。前後の空白はトリムされる。
                空文字または空白のみは不可。トリム後200文字以内であること。
            category: タスクのカテゴリ（省略可）。前後の空白はトリムされる。
                空白のみの文字列を渡した場合は ``None`` として保存される。

        Returns:
            新しく生成された ``TodoItem``。IDは1から始まる連番が自動で設定される。

        Raises:
            ValueError: ``title`` が空文字・空白のみ、またはトリム後に
                ``MAX_TITLE_LENGTH``（200文字）を超える場合。

        Example:
            >>> tl = TodoList()
            >>> item = tl.add("牛乳を買う")
            >>> item.title
            '牛乳を買う'
            >>> item.id
            1

            # カテゴリ付きで追加
            >>> item2 = tl.add("  掃除機をかける  ", category="家事")
            >>> item2.title  # 前後の空白がトリムされる
            '掃除機をかける'
            >>> item2.category
            '家事'

            # 空白のみのカテゴリは None になる
            >>> item3 = tl.add("散歩する", category="   ")
            >>> item3.category is None
            True
        """
        stripped = title.strip()
        if not stripped:
            raise ValueError("タイトルは空にできません")
        if len(stripped) > self.MAX_TITLE_LENGTH:
            raise ValueError(f"タイトルは{self.MAX_TITLE_LENGTH}文字以内にしてください")

        # カテゴリをトリムし、空白のみの場合は None に変換する
        cat = category.strip() if category is not None else None
        if cat == "":
            cat = None

        item = TodoItem(id=self._next_id, title=stripped, category=cat)
        self._items[self._next_id] = item
        self._next_id += 1
        return item

    def list_all(self) -> list[TodoItem]:
        """全Todoアイテムをリストで返す。

        返却されるリストは内部辞書のコピーであるため、
        リスト自体を変更しても内部状態には影響しない。
        ただし各 ``TodoItem`` は ``frozen=True`` の不変オブジェクトである。

        Returns:
            全 ``TodoItem`` を追加順に格納したリスト。
            アイテムが存在しない場合は空リストを返す。

        Example:
            >>> tl = TodoList()
            >>> tl.list_all()
            []
            >>> tl.add("タスクA")
            TodoItem(id=1, title='タスクA', done=False, category=None)
            >>> tl.add("タスクB")
            TodoItem(id=2, title='タスクB', done=False, category=None)
            >>> len(tl.list_all())
            2
        """
        return list(self._items.values())

    def list_by_category(self, category: str) -> list[TodoItem]:
        """指定したカテゴリのTodoアイテムのみをリストで返す。

        Args:
            category: フィルタするカテゴリ文字列。完全一致で検索する。

        Returns:
            指定カテゴリに一致する ``TodoItem`` のリスト。
            一致するアイテムが存在しない場合は空リストを返す。

        Example:
            >>> tl = TodoList()
            >>> tl.add("仕事A", category="仕事")
            TodoItem(...)
            >>> tl.add("趣味A", category="趣味")
            TodoItem(...)
            >>> 仕事リスト = tl.list_by_category("仕事")
            >>> len(仕事リスト)
            1
            >>> tl.list_by_category("存在しないカテゴリ")
            []
        """
        return [item for item in self._items.values() if item.category == category]

    def complete(self, todo_id: int) -> TodoItem:
        """指定IDのTodoアイテムを完了状態にして返す。

        ``TodoItem`` は不変（``frozen=True``）のため、内部では ``dataclasses.replace``
        を用いて ``done=True`` の新しいインスタンスを生成し、内部ストレージを更新する。

        Args:
            todo_id: 完了にするTodoアイテムのID。

        Returns:
            ``done=True`` に更新された新しい ``TodoItem`` インスタンス。
            ID・タイトル・カテゴリは変更されない。

        Raises:
            KeyError: 指定した ``todo_id`` に対応するTodoが存在しない場合。
            AlreadyDoneError: 指定した ``todo_id`` のTodoが既に完了済み（``done=True``）の場合。

        Example:
            >>> tl = TodoList()
            >>> item = tl.add("完了するタスク")
            >>> item.done
            False
            >>> done_item = tl.complete(item.id)
            >>> done_item.done
            True

            # 存在しないIDには KeyError
            >>> tl.complete(999)
            Traceback (most recent call last):
                ...
            KeyError: 'ID 999 のTodoが見つかりません'

            # 既完了のアイテムには AlreadyDoneError
            >>> tl.complete(item.id)
            Traceback (most recent call last):
                ...
            AlreadyDoneError: ID 1 のTodoは既に完了しています
        """
        item = self._find(todo_id)
        if item is None:
            raise KeyError(f"ID {todo_id} のTodoが見つかりません")
        if item.done:
            raise AlreadyDoneError(f"ID {todo_id} のTodoは既に完了しています")
        updated = replace(item, done=True)
        self._items[todo_id] = updated
        return updated

    def delete(self, todo_id: int) -> bool:
        """指定IDのTodoアイテムを削除する。

        指定したIDのアイテムが存在しない場合は何もせず ``False`` を返す。
        例外は送出しない。

        Args:
            todo_id: 削除するTodoアイテムのID。

        Returns:
            削除に成功した場合は ``True``、指定IDのアイテムが存在しない場合は ``False``。

        Example:
            >>> tl = TodoList()
            >>> item = tl.add("削除対象タスク")
            >>> tl.delete(item.id)
            True
            >>> tl.list_all()
            []

            # 存在しないIDは False
            >>> tl.delete(999)
            False
        """
        if todo_id not in self._items:
            return False
        del self._items[todo_id]
        return True

    def __str__(self) -> str:
        """TodoListの内容を人間が読みやすい文字列で返す。

        各アイテムを1行で表現し、改行で結合して返す。
        1行のフォーマットは以下の通り:

        - 完了済み: ``✓ [ID] タイトル [カテゴリ] (完了)``
        - 未完了:   ``  [ID] タイトル [カテゴリ] (未完了)``
        - カテゴリが ``None`` の場合は ``[カテゴリ]`` 部分は省略される。

        Returns:
            アイテムが存在する場合は各アイテムを改行で連結した文字列。
            アイテムが存在しない場合は ``"Todoリストは空です"``。

        Example:
            >>> tl = TodoList()
            >>> print(tl)
            Todoリストは空です
            >>> tl.add("買い物", category="家事")
            TodoItem(...)
            >>> item = tl.add("レポート提出")
            >>> tl.complete(item.id)
            TodoItem(...)
            >>> print(tl)
              [1] 買い物 [家事] (未完了)
            ✓ [2] レポート提出 (完了)
        """
        if not self._items:
            return "Todoリストは空です"

        def _line(item: TodoItem) -> str:
            """1件のTodoアイテムを1行の文字列に変換する内部ヘルパー。"""
            mark = "✓ " if item.done else "  "
            cat = f" [{item.category}]" if item.category else ""
            status = "完了" if item.done else "未完了"
            return f"{mark}[{item.id}] {item.title}{cat} ({status})"

        return "\n".join(_line(i) for i in self._items.values())

    def _find(self, todo_id: int) -> TodoItem | None:
        """指定IDのTodoアイテムを返す内部ヘルパー。

        Args:
            todo_id: 検索するTodoアイテムのID。

        Returns:
            該当する ``TodoItem``。存在しない場合は ``None``。
        """
        return self._items.get(todo_id)
