# マルチエージェント

Claude Code のマルチエージェント機能を実習するプロジェクトです。

---

## 目次

1. [プロジェクト概要](#プロジェクト概要)
2. [技術スタック](#技術スタック)
3. [セットアップ手順](#セットアップ手順)
4. [使い方](#使い方)
5. [テスト実行](#テスト実行)
6. [ディレクトリ構成](#ディレクトリ構成)
7. [API リファレンス](#api-リファレンス)

---

## プロジェクト概要

このプロジェクトは Claude Code のマルチエージェント機能を段階的に実習することを目的としています。

現在実装済みの機能として、シンプルな **Todoリスト管理モジュール**（`src/todo.py`）があります。
Todoアイテムの追加・取得・完了・削除という基本的な CRUD 操作を提供しており、
後続のセクションで FastAPI を使った Web API への拡張を予定しています。

---

## 技術スタック

| 用途 | ツール・ライブラリ |
|------|------------------|
| 言語 | Python 3.13 |
| パッケージ管理 | [uv](https://docs.astral.sh/uv/)（pip は使用しない） |
| テスト | pytest |
| Web フレームワーク（予定） | FastAPI（セクション7で使用） |
| HTTP クライアント | httpx |

---

## セットアップ手順

### 前提条件

- Python 3.13 以上
- [uv](https://docs.astral.sh/uv/) がインストール済みであること

### 手順

```bash
# リポジトリのクローン
git clone <repository-url>
cd multi-agent

# 依存パッケージのインストール（.venv も自動作成される）
uv sync

# 開発用依存関係も含めてインストールする場合
uv sync --all-groups
```

パッケージを追加する場合は `pip install` ではなく `uv add` を使います。

```bash
# 本番依存として追加
uv add <パッケージ名>

# 開発用依存として追加
uv add --dev <パッケージ名>
```

---

## 使い方

スクリプトの実行には `uv run python` を使います。

### TodoList の基本操作

```python
from todo import TodoList, AlreadyDoneError

tl = TodoList()

# ── アイテムの追加 ──────────────────────────────
item1 = tl.add("牛乳を買う")
print(item1.id)        # 1
print(item1.title)     # 牛乳を買う
print(item1.done)      # False
print(item1.category)  # None

# カテゴリを指定して追加
item2 = tl.add("レポートを書く", category="仕事")
item3 = tl.add("掃除機をかける", category="家事")

# ── 一覧取得 ────────────────────────────────────
all_items = tl.list_all()
print(len(all_items))  # 3

# カテゴリでフィルタ
仕事リスト = tl.list_by_category("仕事")
print(len(仕事リスト))  # 1

# ── 完了にする ──────────────────────────────────
done_item = tl.complete(item1.id)
print(done_item.done)  # True

# ── 削除する ────────────────────────────────────
result = tl.delete(item3.id)
print(result)  # True（削除成功）

result = tl.delete(999)
print(result)  # False（存在しないIDは False を返す）

# ── 文字列表現 ──────────────────────────────────
print(tl)
# ✓ [1] 牛乳を買う (完了)
#   [2] レポートを書く [仕事] (未完了)
```

### 例外のハンドリング

```python
from todo import TodoList, AlreadyDoneError

tl = TodoList()
item = tl.add("タスク")
tl.complete(item.id)

# 既完了アイテムへの再完了は AlreadyDoneError
try:
    tl.complete(item.id)
except AlreadyDoneError as e:
    print(e)  # ID 1 のTodoは既に完了しています

# 存在しないIDへの操作は KeyError
try:
    tl.complete(999)
except KeyError as e:
    print(e)  # 'ID 999 のTodoが見つかりません'

# タイトルのバリデーション
try:
    tl.add("")
except ValueError as e:
    print(e)  # タイトルは空にできません

try:
    tl.add("あ" * 201)
except ValueError as e:
    print(e)  # タイトルは200文字以内にしてください
```

### スクリプトとして実行

```bash
uv run python src/todo.py
```

---

## テスト実行

```bash
# 全テストを実行
uv run pytest

# 詳細出力付きで実行
uv run pytest -v

# 特定のテストクラスのみ実行
uv run pytest tests/test_todo.py::TestAdd -v
```

### テスト構成

| テストクラス | テスト件数 | 内容 |
|-------------|-----------|------|
| `TestAdd` | 7件 | `add` メソッドの正常系 |
| `TestAddError` | 4件 | `add` メソッドの異常系（ValueError） |
| `TestList` | 6件 | `list_all` / `list_by_category` の動作確認 |
| `TestComplete` | 2件 | `complete` メソッドの正常系 |
| `TestCompleteError` | 2件 | `complete` メソッドの異常系（KeyError / AlreadyDoneError） |
| `TestDelete` | 5件 | `delete` メソッドの正常系・異常系 |
| `TestStr` | 4件 | `__str__` メソッドの出力確認 |
| **合計** | **30件** | |

---

## ディレクトリ構成

```
multi-agent/
├── src/                  # メインのソースコード
│   └── todo.py           # Todoリスト管理モジュール
├── tests/                # テストコード
│   ├── test_todo.py      # todo.py のテスト（30件）
│   └── CLAUDE.md         # テスト固有のルール
├── docs/                 # ドキュメント（必要に応じて追加）
├── .venv/                # uv が管理する仮想環境（git 管理外）
├── pyproject.toml        # プロジェクト設定・依存関係
├── CLAUDE.md             # プロジェクトルール（Claude Code 向け）
└── README.md             # このファイル
```

---

## API リファレンス

### クラス一覧

| クラス | 説明 |
|--------|------|
| `TodoItem` | 1件のTodoアイテムを表す不変データクラス（`frozen=True`） |
| `TodoList` | Todoアイテムを管理するクラス |
| `AlreadyDoneError` | 既完了アイテムへ `complete` を呼んだときの例外 |

---

### `TodoItem`

`frozen=True` の不変データクラスです。外部から属性を直接変更することはできません。

| フィールド | 型 | デフォルト | 説明 |
|-----------|-----|-----------|------|
| `id` | `int` | （必須） | アイテムを一意に識別するID |
| `title` | `str` | （必須） | タスクのタイトル |
| `done` | `bool` | `False` | 完了フラグ |
| `category` | `str \| None` | `None` | カテゴリ名 |

---

### `TodoList` メソッド一覧

#### `add(title, category=None) -> TodoItem`

Todoアイテムを追加して返す。

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `title` | `str` | タスクのタイトル（前後の空白はトリムされる） |
| `category` | `str \| None` | カテゴリ（省略可。空白のみの場合は `None` として保存） |

**送出される例外:**

| 例外 | 条件 |
|------|------|
| `ValueError` | `title` が空・空白のみ、またはトリム後に200文字超の場合 |

---

#### `list_all() -> list[TodoItem]`

全Todoアイテムをリストで返す。アイテムが存在しない場合は空リスト。

---

#### `list_by_category(category) -> list[TodoItem]`

指定したカテゴリのTodoアイテムのみをリストで返す。一致しない場合は空リスト。

---

#### `complete(todo_id) -> TodoItem`

指定IDのTodoアイテムを完了状態（`done=True`）にして返す。

**送出される例外:**

| 例外 | 条件 |
|------|------|
| `KeyError` | 指定した `todo_id` が存在しない場合 |
| `AlreadyDoneError` | 指定した `todo_id` のアイテムが既に完了済みの場合 |

---

#### `delete(todo_id) -> bool`

指定IDのTodoアイテムを削除する。

| 戻り値 | 条件 |
|--------|------|
| `True` | 削除成功 |
| `False` | 指定した `todo_id` が存在しない場合（例外は送出しない） |

---

### 例外一覧

| 例外クラス | 基底クラス | 送出されるメソッド | 説明 |
|-----------|-----------|-----------------|------|
| `AlreadyDoneError` | `Exception` | `TodoList.complete` | 既完了アイテムへの再完了操作 |

---

## 開発ルール

- コメントとドキュメントは日本語で記述する
- パッケージの追加は `uv add` を使う（`pip install` は使用しない）
- スクリプト実行は `uv run python` を使う
- テスト実行は `uv run pytest` を使う
