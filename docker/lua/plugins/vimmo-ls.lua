return {
  "AstroNvim/astrolsp",
  opts = {
    -- vimmo_ls は Mason 管理外のため手動で有効化
    servers = { "vimmo_ls" },
    config = {
      vimmo_ls = {
        cmd = { "vimmo-ls" },
        filetypes = { "vmo" },
        root_dir = function()
          return vim.loop.cwd()
        end,
      },
    },
  },
}
