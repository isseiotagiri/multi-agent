import json


class TodoList:
    """JSONファイルを永続化ストアとして使うTodoリスト管理クラス。

    インスタンス生成時に指定されたJSONファイルを読み込み、
    アイテムの追加・完了・削除・検索・統計取得を行う。
    各操作後は自動的にファイルへ保存される。

    JSONファイルのデータ形式::

        {
            "todos": [
                {"id": 1, "title": "タスク名", "done": false}
            ],
            "next_id": 2
        }

    Args:
        filepath (str): Todoデータを保存するJSONファイルのパス。
            デフォルトは ``"todos.json"``。

    Attributes:
        filepath (str): JSONファイルのパス。
        todos (list[dict]): Todoアイテムのリスト。
        next_id (int): 次に割り当てるID。

    Example:
        >>> import json, tempfile, os
        >>> with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        ...     json.dump({"todos": [], "next_id": 1}, f)
        ...     path = f.name
        >>> tl = TodoList(filepath=path)
        >>> item = tl.add("はじめてのタスク")
        >>> item["title"]
        'はじめてのタスク'
        >>> os.unlink(path)
    """

    def __init__(self, filepath="todos.json"):
        self.filepath = filepath
        self.todos = []
        self.next_id = 1
        self.load()

    def load(self):
        """JSONファイルからTodoデータを読み込む。

        ``self.filepath`` が指すJSONファイルを開き、
        ``todos`` リストと ``next_id`` を初期化する。
        このメソッドは ``__init__`` から自動的に呼ばれる。

        Raises:
            FileNotFoundError: 指定したファイルが存在しない場合。
            json.JSONDecodeError: ファイルの内容が不正なJSON形式の場合。
            KeyError: JSONに ``"todos"`` または ``"next_id"`` キーがない場合。

        Note:
            【バグB1】ファイルが存在しない場合に ``FileNotFoundError`` が発生する。
            ファイルが存在しないときは空のTodoリストで初期化するよう修正が必要。
        """
        f = open(self.filepath, "r")
        data = json.load(f)
        self.todos = data["todos"]
        self.next_id = data["next_id"]
        f.close()

    def save(self):
        """現在のTodoデータをJSONファイルへ書き込む。

        ``self.todos`` と ``self.next_id`` を ``self.filepath`` へ
        JSON形式で上書き保存する。
        ``add()`` / ``complete()`` / ``delete()`` から自動的に呼ばれる。

        Raises:
            OSError: ファイルへの書き込みに失敗した場合（権限不足など）。

        Example:
            >>> # save() は各変更メソッドから自動的に呼ばれるため、
            >>> # 通常は直接呼び出す必要はない。
            >>> tl.save()  # 明示的に保存したい場合のみ使用する
        """
        f = open(self.filepath, "w")
        json.dump({"todos": self.todos, "next_id": self.next_id}, f)
        f.close()

    def add(self, title):
        """新しいTodoアイテムを追加する。

        指定したタイトルでアイテムを作成し、IDを採番してリストへ追加する。
        追加後は自動的にファイルへ保存する。

        Args:
            title (str): Todoアイテムのタイトル。

        Returns:
            dict: 追加したTodoアイテム。キーは ``"id"``（int）、
                ``"title"``（str）、``"done"``（bool）。

        Note:
            【バグB5】空文字列 ``""`` を ``title`` に渡してもバリデーションなしに
            登録されてしまう。空文字列は拒否するよう修正が必要。

        Example:
            >>> item = tl.add("買い物をする")
            >>> item
            {'id': 1, 'title': '買い物をする', 'done': False}
        """
        todo = {"id": self.next_id, "title": title, "done": False}
        self.todos.append(todo)
        self.next_id += 1
        self.save()
        return todo

    def list_all(self):
        """全てのTodoアイテムを取得する。

        内部リストをそのまま返す。追加順（IDの昇順）で返される。

        Returns:
            list[dict]: 全Todoアイテムのリスト。
                アイテムが0件の場合は空リスト ``[]`` を返す。

        Note:
            【バグB7】内部リスト自体への参照を返すため、呼び出し元が返り値を
            変更（例: ``clear()`` や ``pop()``）すると内部データが破壊される。
            ``return list(self.todos)`` のようにコピーを返すよう修正が必要。

        Example:
            >>> tl.add("タスク1")
            >>> tl.add("タスク2")
            >>> items = tl.list_all()
            >>> len(items)
            2
        """
        return self.todos

    def complete(self, todo_id):
        """指定IDのTodoアイテムを完了状態にする。

        ``todo_id`` に一致するアイテムを検索し、``done`` を ``True`` に更新する。
        更新後は自動的にファイルへ保存する。

        Args:
            todo_id (int): 完了にするTodoアイテムのID。

        Returns:
            dict | None: 完了状態に更新したアイテム。
                IDが見つからない場合は ``None`` を返す。

        Note:
            【バグB4】IDが見つからない場合に明示的な ``return False`` や
            例外がなく、暗黙的に ``None`` が返る。
            呼び出し元は戻り値が ``None`` かどうかを確認して処理する必要がある。

        Example:
            >>> item = tl.add("レポートを提出する")
            >>> result = tl.complete(item["id"])
            >>> result["done"]
            True
            >>> tl.complete(999)  # 存在しないID -> None が返る
        """
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["done"] = True
                self.save()
                return todo

    def delete(self, todo_id):
        """指定IDのTodoアイテムを削除する。

        ``todo_id`` に一致するアイテムをリストから取り除く。
        削除後は自動的にファイルへ保存する。

        Args:
            todo_id (int): 削除するTodoアイテムのID。

        Returns:
            bool | None: 削除に成功した場合は ``True``。
                IDが見つからない場合は ``None`` を返す（``False`` ではない）。

        Note:
            【バグB3】IDが見つからない場合に ``False`` ではなく ``None`` が返る。
            呼び出し元で ``result is False`` と判定しても正しく動作しないため、
            ``result is None`` または ``not result`` で判定する必要がある。

        Example:
            >>> item = tl.add("不要なタスク")
            >>> tl.delete(item["id"])
            True
            >>> tl.delete(999)  # 存在しないID -> None が返る
        """
        for i, todo in enumerate(self.todos):
            if todo["id"] == todo_id:
                self.todos.pop(i)
                self.save()
                return True

    def search(self, keyword):
        """キーワードでTodoアイテムを検索する。

        タイトルに ``keyword`` を含む全アイテムを返す（部分一致）。
        大文字・小文字は区別される。

        Args:
            keyword (str): 検索キーワード。空文字列 ``""`` を渡すと全件返る。

        Returns:
            list[dict]: キーワードにマッチしたTodoアイテムのリスト。
                マッチするアイテムがない場合は空リスト ``[]`` を返す。

        Raises:
            TypeError: ``keyword`` に ``None`` を渡した場合（``in`` 演算子が失敗する）。

        Note:
            【バグB6】``keyword`` に ``None`` を渡すと ``TypeError`` が発生する。
            引数の型チェックを追加するか、呼び出し元で ``None`` を渡さないよう注意する。

        Example:
            >>> tl.add("買い物リストを作る")
            >>> tl.add("報告書を書く")
            >>> tl.search("書")
            [{'id': 1, 'title': '買い物リストを作る', 'done': False},
             {'id': 2, 'title': '報告書を書く', 'done': False}]
            >>> tl.search("存在しないワード")
            []
        """
        result = []
        for todo in self.todos:
            if keyword in todo["title"]:
                result.append(todo)
        return result

    def get_stats(self):
        """Todoリストの統計情報を取得する。

        全件数・完了件数・未完了件数・完了率を計算して返す。

        Returns:
            dict: 統計情報を格納した辞書。キーと値は以下の通り:

                - ``"total"`` (int): 全アイテム数。
                - ``"done"`` (int): 完了済みアイテム数。
                - ``"pending"`` (int): 未完了アイテム数。
                - ``"rate"`` (float): 完了率（``done / total``）。

        Raises:
            ZeroDivisionError: アイテムが0件のとき ``done / total`` の計算で発生する。

        Note:
            【バグB2】アイテムが0件のとき ``ZeroDivisionError`` が発生する。
            ``total == 0`` のときは ``rate`` を ``0.0`` として返すよう修正が必要。

        Example:
            >>> tl.add("タスク1")
            >>> item = tl.add("タスク2")
            >>> tl.complete(item["id"])
            >>> tl.get_stats()
            {'total': 2, 'done': 1, 'pending': 1, 'rate': 0.5}
        """
        total = len(self.todos)
        done = 0
        for todo in self.todos:
            if todo["done"]:
                done += 1
        return {"total": total, "done": done, "pending": total - done, "rate": done / total}
