; ===========================================================================
; locals.scm — Tree-sitter scope queries for VimMo
; Used for symbol lookup (go-to-definition, rename, etc.) in editors that
; support nvim-treesitter's locals feature.
; ===========================================================================

; ---------------------------------------------------------------------------
; Scopes
; ---------------------------------------------------------------------------

(source_file) @local.scope
(function_declaration body: (block) @local.scope)
(class_body) @local.scope
(arrow_function body: (block) @local.scope)
(if_statement consequence: (block) @local.scope)
(if_statement alternative: (block) @local.scope)
(for_statement body: (block) @local.scope)
(while_statement body: (block) @local.scope)

; ---------------------------------------------------------------------------
; Definitions
; ---------------------------------------------------------------------------

(variable_declaration name: (identifier) @local.definition)
(function_declaration name: (identifier) @local.definition)
(class_declaration name: (identifier) @local.definition)
(parameter name: (identifier) @local.definition)
(for_statement variable: (identifier) @local.definition)

; ---------------------------------------------------------------------------
; References
; ---------------------------------------------------------------------------

(identifier) @local.reference
