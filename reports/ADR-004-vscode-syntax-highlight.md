# ADR-004: VS Code シンタクスハイライト実装

## ステータス

承認済み

## 背景

VimMo は `.vmo` 拡張子を持つ TypeScript 風言語であり、VS Code 拡張 (`vscode-vimmo`) に TextMate 文法ファイルが存在しなかった。
`package.json` には `syntaxes/vimmo.tmLanguage.json` と `language-configuration.json` の参照が既に記述されていたが、ファイル自体が存在しなかったため、シンタクスハイライトが機能しない状態だった。

## 決定事項

以下の2ファイルを `packages/vscode-vimmo/` に追加することでシンタクスハイライトを実装する。

### `syntaxes/vimmo.tmLanguage.json`

TextMate 文法ファイル。スコープ名 `source.vmo` で以下のトークンを定義:

| カテゴリ | スコープ名 | 対象 |
|---------|-----------|-----|
| コメント | `comment.line.double-slash.vmo` | `// ...` |
| 文字列 | `string.quoted.double/single.vmo` | `"..."` / `'...'` |
| エスケープ | `constant.character.escape.vmo` | `\n`, `\t` 等 |
| 数値 | `constant.numeric.float/integer.vmo` | `3.14`, `42` |
| 制御キーワード | `keyword.control.vmo` | `if`, `else`, `for`, `in`, `while`, `break`, `continue`, `return` |
| 宣言キーワード | `keyword.declaration.vmo` | `let`, `const`, `fn`, `class`, `async`, `await` |
| その他キーワード | `keyword.other.vmo` | `import`, `from`, `echo`, `new`, `self` |
| 型 | `support.type.primitive.vmo` | `number`, `string`, `bool`, `list`, `dict`, `any`, `void` |
| 真偽値 | `constant.language.boolean.vmo` | `true`, `false` |
| null | `constant.language.null.vmo` | `null` |
| パイプライン演算子 | `keyword.operator.pipeline.vmo` | `\|>` |
| アロー演算子 | `keyword.operator.arrow.vmo` | `=>` |
| 比較演算子 | `keyword.operator.comparison.vmo` | `==`, `!=`, `<=`, `>=`, `<`, `>` |
| 論理演算子 | `keyword.operator.logical.vmo` | `&&`, `\|\|`, `!` |
| 代入演算子 | `keyword.operator.assignment.vmo` | `=`, `+=`, `-=` |
| 算術演算子 | `keyword.operator.arithmetic.vmo` | `+`, `-`, `*`, `/`, `%` |
| 文字列結合 | `keyword.operator.string-concat.vmo` | `..` |
| 関数名 | `entity.name.function.vmo` | `fn name(...)` 定義・呼び出し |
| クラス名 | `entity.name.type.class.vmo` | `class Name` |
| 変数 | `variable.other.vmo` | 識別子全般 |

### `language-configuration.json`

言語設定ファイル。以下を定義:
- `//` 行コメント
- `{}`, `[]`, `()`, `""`, `''` の自動補完・サラウンド
- `{` でインデント増加、`}` でインデント減少

## 変更されたファイル

- `packages/vscode-vimmo/syntaxes/vimmo.tmLanguage.json` (新規)
- `packages/vscode-vimmo/language-configuration.json` (新規)

## テスト結果

JSON の構文検証を Python で実施し、両ファイルが正常にパースされることを確認。
VS Code での動作確認はローカル環境での手動テストが必要。
