FROM python:3.14-slim

RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LO https://github.com/neovim/neovim/releases/download/v0.11.6/nvim-linux-arm64.tar.gz \
    && tar xzf nvim-linux-arm64.tar.gz \
    && mv nvim-linux-arm64/bin/nvim /usr/local/bin/ \
    && mv nvim-linux-arm64/lib/nvim /usr/local/lib/ \
    && mv nvim-linux-arm64/share/nvim /usr/local/share/ \
    && rm -rf nvim-linux-arm64*

COPY docker/nvim /root/.config/nvim

COPY docker/lua /root/.config/nvim/lua

WORKDIR /app

COPY . /app

RUN pip install -e /app/packages/vimmo-core -e /app/packages/vimmo-ls

# Neovim プラグインをビルド時にインストール (lazy.nvim headless sync)
RUN nvim --headless "+Lazy! sync" +qa || true

# vimmo Tree-sitter パーサーをビルド時にコンパイル
RUN nvim --headless -c "TSInstall! vimmo" -c "qa" || true

ENV PYTHONPATH=/app/packages/vimmo-core/src
ENV XDG_CONFIG_HOME=/root/.config
