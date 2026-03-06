# ADR-002: Docker テスト環境の追加

**ステータス:** 草案

**日付:** 2026-03-06

## 決定事項

docker-compose.yml に test サービスを追加し、開発環境とテスト環境で同一の Docker イメージを使用する。

## 背景

- 06_import テストがローカル環境で失敗 (相対パス解決の問題)
- Docker コンテナ内でテストを実行すれば解決可能
- 開発環境 (vimmo) とテスト環境 (test) を同一イメージで運用可能

## 変更されたファイル

- `docker-compose.yml` - test サービス追加

## 技術詳細

### 変更前

```yaml
services:
  vimmo:
    build: .
    command: sleep infinity
    volumes:
      - .:/app
    tty: true
    stdin_open: true
```

### 変更後

```yaml
services:
  vimmo:
    build: .
    command: sleep infinity
    volumes:
      - .:/app
    tty: true
    stdin_open: true

  test:
    build: .
    command: python tests/run_tests.py
    volumes:
      - .:/app
    working_dir: /app
```

## 使用方法

```bash
# テスト実行
docker-compose run --rm test

# または
docker-compose up test
```

## テスト結果

- 9/10 テストパス
- 06_import: 失敗 (codegen で import 関数のスコープ処理が必要)
- 09_closure: 失敗 (VimScript の funcref 制約により不可)

## 次のステップ

- Tree-sitter 基盤構築へ進む
