# multi-agent

Claude Code のマルチエージェント機能を実習するプロジェクトです。
現在は `TodoList` モジュールを中心に、Python による Todoリスト管理の実装とテストを行っています。

---

## 機能一覧

`src/todo.py` に実装されている `TodoList` クラスのメソッド一覧です。

| メソッド | 説明 |
| --- | --- |
| `add(title)` | タイトルを指定して新しいTodoアイテムを追加する |
| `list_all()` | 全件取得する |
| `complete(todo_id)` | 指定IDのアイテムを完了状態にする |
| `delete(todo_id)` | 指定IDのアイテムを削除する |
| `search(keyword)` | タイトルのキーワード部分一致で検索する |
| `get_stats()` | 全件数・完了数・未完了数・完了率を取得する |
| `save()` | 現在の状態をJSONファイルへ保存する（各操作後に自動呼び出し） |
| `load()` | JSONファイルからデータを読み込む（初期化時に自動呼び出し） |

---

## セットアップ手順

### 前提条件

- Python 3.13 以上
- [uv](https://github.com/astral-sh/uv) がインストール済みであること

### インストール

```bash
# リポジトリをクローン
git clone <リポジトリURL>
cd multi-agent

# 依存パッケージをインストール
uv sync
```

---

## 使い方

### 基本的な使用例

```python
import json
from src.todo import TodoList

# 初期化用のJSONファイルを用意する
with open("todos.json", "w") as f:
    json.dump({"todos": [], "next_id": 1}, f)

# TodoListのインスタンスを作成する
tl = TodoList(filepath="todos.json")

# アイテムを追加する
item1 = tl.add("買い物をする")
item2 = tl.add("報告書を書く")
item3 = tl.add("部屋を掃除する")

# 全件取得する
items = tl.list_all()
print(items)
# [{'id': 1, 'title': '買い物をする', 'done': False}, ...]

# アイテムを完了にする
tl.complete(item1["id"])

# キーワードで検索する
results = tl.search("書")
print(results)
# [{'id': 2, 'title': '報告書を書く', 'done': False}]

# アイテムを削除する
tl.delete(item3["id"])

# 統計情報を取得する（アイテムが1件以上のとき有効）
stats = tl.get_stats()
print(stats)
# {'total': 2, 'done': 1, 'pending': 1, 'rate': 0.5}
```

### スクリプトの実行

```bash
uv run python src/todo.py
```

---

## テスト実行方法

```bash
# 全テストを詳細表示で実行する
uv run pytest tests/test_todo.py -v

# 特定のクラスだけ実行する例
uv run pytest tests/test_todo.py::TestAdd -v
```

---

## テスト結果サマリー

| 項目 | 件数 |
| --- | --- |
| 総テスト数 | 32件 |
| passed | 31件 |
| xfailed（既知バグ） | 1件 |

xfailed は `get_stats()` のゼロ除算バグ（B2）をテストコード上で既知バグとしてマークしたものです。
現時点でバグは修正されていないため、テスト自体は期待通り失敗し `xfailed` として記録されます。

---

## 既知の問題

コードレビューで判明しているバグの一覧です。

| バグID | 対象メソッド | 内容 |
| --- | --- | --- |
| B1 | `load()` | ファイルが存在しない場合に `FileNotFoundError` が発生する。存在しない場合は空リストで初期化すべき。 |
| B2 | `get_stats()` | アイテムが0件のとき `ZeroDivisionError` が発生する。`total == 0` のときは `rate` を `0.0` で返すべき。 |
| B3 | `delete()` | IDが見つからない場合に `False` ではなく `None` を返す。 |
| B4 | `complete()` | IDが見つからない場合に明示的な `return` がなく `None` を返す。 |
| B5 | `add()` | 空文字列 `""` をバリデーションせず登録してしまう。 |
| B6 | `search()` | `keyword` に `None` を渡すと `TypeError` が発生する。 |
| B7 | `list_all()` | 内部リストへの参照を返すため、呼び出し元が変更すると内部データが破壊される。 |

---

## ディレクトリ構成

```text
multi-agent/
├── src/            # メインのソースコード
│   └── todo.py     # TodoList クラスの実装
├── tests/          # テストコード
│   └── test_todo.py
├── docs/           # ドキュメント
├── pyproject.toml  # プロジェクト設定・依存関係
└── README.md
```

---

## 技術スタック

| 項目 | 内容 |
| --- | --- |
| 言語 | Python 3.13 |
| パッケージ管理 | uv（pip は使用しない） |
| テスト | pytest |
| HTTP クライアント | httpx |
