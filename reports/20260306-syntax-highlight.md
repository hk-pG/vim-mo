**モデル:** claude-sonnet-4-5

# 20260306 - syntax-highlight

## 完了したタスク

VS Code 拡張 (`vscode-vimmo`) にシンタクスハイライトを実装した。

`package.json` には既に `syntaxes/vimmo.tmLanguage.json` と `language-configuration.json` への参照が記載されていたが、ファイル自体が存在しなかったため、ハイライトが一切機能していなかった。

## 新規作成したファイル

| ファイル | 内容 |
|---------|------|
| `packages/vscode-vimmo/syntaxes/vimmo.tmLanguage.json` | TextMate 文法ファイル（スコープ名 `source.vmo`） |
| `packages/vscode-vimmo/language-configuration.json` | ブラケット補完・インデント・コメント設定 |
| `reports/ADR-004-vscode-syntax-highlight.md` | 設計決定の記録 |

## ハイライト対象

- **コメント**: `// ...`
- **文字列**: `"..."`, `'...'`（エスケープシーケンス含む）
- **数値**: 整数・浮動小数点
- **制御キーワード**: `if`, `else`, `for`, `in`, `while`, `break`, `continue`, `return`
- **宣言キーワード**: `let`, `const`, `fn`, `class`, `async`, `await`
- **その他キーワード**: `import`, `from`, `echo`, `new`, `self`
- **型**: `number`, `string`, `bool`, `list`, `dict`, `any`, `void`
- **リテラル**: `true`, `false`, `null`
- **演算子**: `|>`, `=>`, `==`, `!=`, `+=`, `-=`, `&&`, `||` 等
- **関数名**: `fn name(...)` の定義および呼び出し
- **クラス名**: `class Name`

## テスト結果

JSON 構文検証を Python で実施し、両ファイルが正常にパースされることを確認。

```
tmLanguage.json is valid JSON
language-configuration.json is valid JSON
```

## 次のステップ

- VS Code でローカル動作確認（`vsce package` → VSIX インストール、または Extension Development Host で確認）
- 必要に応じてスコープ名の調整
- VS Code Marketplace への公開準備（`README.md`, `icon` 等の追加）
