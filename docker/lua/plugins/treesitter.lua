return {
    "nvim-treesitter/nvim-treesitter",
    opts = function(_, opts)
        local parser_config = require("nvim-treesitter.parsers").get_parser_configs()
        parser_config.vimmo = {
            install_info = {
                url = "/app/packages/tree-sitter-vimmo",
                files = { "src/parser.c" },
                generate_requires_npm = false,
                requires_generate_from_grammar = false,
            },
            filetype = "vmo",
        }
        vim.filetype.add({ extension = { vmo = "vmo" } })
    end,
}
