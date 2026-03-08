.PHONY: ci lint test lsp-test install-hooks

# ─── ローカル CI 実行 (act) ───────────────────────────────────────────────────
## フル CI  — GitHub Actions と同じジョブをコンテナで実行
ci:
	act push

## 特定ジョブのみ実行
ci-lint:
	act push -j lint

ci-test:
	act push -j test

ci-lsp:
	act push -j lsp-test

# ─── ダイレクト実行 (コンテナ不使用 / 高速確認用) ──────────────────────────
## flake8 lint
lint:
	flake8 packages/vimmo-core/src/ packages/vimmo-ls/src/ --max-line-length=100

## E2E テスト (Docker Compose)
test:
	docker compose run --rm test

## LSP ユニットテスト
lsp-test:
	pip install -q -e packages/vimmo-core -e "packages/vimmo-ls[test]"
	pytest packages/vimmo-ls/tests/

# ─── Git hooks セットアップ ───────────────────────────────────────────────────
install-hooks:
	@bash scripts/install-hooks.sh
