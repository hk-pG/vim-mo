; ===========================================================================
; highlights.scm — Tree-sitter highlight queries for VimMo
; Used by Neovim (nvim-treesitter) and other Tree-sitter-aware editors.
; ===========================================================================

; ---------------------------------------------------------------------------
; Keywords
; ---------------------------------------------------------------------------

(function_declaration "fn" @keyword.function)
(function_declaration "async" @keyword.coroutine)
(class_declaration "class" @keyword.type)

(variable_declaration "let" @keyword)
(variable_declaration "const" @keyword)

(return_statement "return" @keyword.return)
(echo_statement "echo" @keyword)

(if_statement "if" @keyword.conditional)
(if_statement "else" @keyword.conditional)

(for_statement "for" @keyword.repeat)
(for_statement "in" @keyword.operator)
(while_statement "while" @keyword.repeat)

(break_statement "break" @keyword)
(continue_statement "continue" @keyword)

(import_statement "import" @keyword.import)
(import_statement "from" @keyword.import)

(new_expression "new" @keyword)
(await_expression "await" @keyword.coroutine)

; ---------------------------------------------------------------------------
; Types
; ---------------------------------------------------------------------------

[
  "number"
  "string"
  "bool"
  "list"
  "dict"
  "any"
  "void"
] @type.builtin

; ---------------------------------------------------------------------------
; Functions & methods
; ---------------------------------------------------------------------------

(function_declaration name: (identifier) @function)

(call_expression
  function: (identifier) @function.call)

(call_expression
  function: (member_expression
    property: (identifier) @method.call))

(arrow_function) @function.lambda

; ---------------------------------------------------------------------------
; Classes
; ---------------------------------------------------------------------------

(class_declaration name: (identifier) @type)
(new_expression class: (identifier) @type)

; ---------------------------------------------------------------------------
; Variables & parameters
; ---------------------------------------------------------------------------

(variable_declaration name: (identifier) @variable)
(parameter name: (identifier) @variable.parameter)
(for_statement variable: (identifier) @variable)

; `self` is a builtin variable reference
((identifier) @variable.builtin
  (#eq? @variable.builtin "self"))

; ---------------------------------------------------------------------------
; Operators
; ---------------------------------------------------------------------------

"|>"  @operator
"=>"  @operator

(binary_expression operator: _ @operator)
(unary_expression operator: _ @operator)
(assignment_expression operator: _ @operator)

; ---------------------------------------------------------------------------
; Literals
; ---------------------------------------------------------------------------

(number)  @number
(string)  @string
(boolean) @boolean
(null)    @constant.builtin

; ---------------------------------------------------------------------------
; Punctuation
; ---------------------------------------------------------------------------

["{" "}"] @punctuation.bracket
["[" "]"] @punctuation.bracket
["(" ")"] @punctuation.bracket

["," ":" "."] @punctuation.delimiter

; ---------------------------------------------------------------------------
; Comments
; ---------------------------------------------------------------------------

(comment) @comment
