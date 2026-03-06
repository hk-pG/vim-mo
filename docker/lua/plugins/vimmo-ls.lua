return {
  "neovim/nvim-lspconfig",
  opts = {
    servers = {
      vimmo_ls = {
        cmd = { "vimmo-ls" },
        filetypes = { "vmo" },
        root_dir = function(fname)
          return vim.loop.cwd()
        end,
      },
    },
  },
}
