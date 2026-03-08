#!/usr/bin/env bash
# git hooks をリポジトリの .git/hooks/ にインストールするスクリプト

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOKS_SRC="${REPO_ROOT}/scripts/git-hooks"
HOOKS_DST="${REPO_ROOT}/.git/hooks"

if [[ ! -d "${HOOKS_DST}" ]]; then
    echo "❌ .git/hooks ディレクトリが見つかりません。git リポジトリのルートで実行してください。"
    exit 1
fi

installed=0
for hook in "${HOOKS_SRC}"/*; do
    name="$(basename "${hook}")"
    dst="${HOOKS_DST}/${name}"

    if [[ -e "${dst}" && ! -L "${dst}" ]]; then
        echo "⚠️  ${name}: 既存のカスタム hook があるためスキップします (${dst})"
        continue
    fi

    ln -sf "${hook}" "${dst}"
    chmod +x "${hook}"
    echo "✓  ${name} をインストールしました → ${dst}"
    installed=$((installed + 1))
done

if [[ ${installed} -gt 0 ]]; then
    echo ""
    echo "✅ ${installed} 件の hook をインストールしました。"
    echo "   スキップ方法: SKIP_CI=1 git push  または  git push --no-verify"
else
    echo "ℹ️  インストールする hook はありませんでした。"
fi
