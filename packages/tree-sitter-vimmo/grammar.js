/**
 * Tree-sitter grammar for VimMo (.vmo)
 *
 * Run `npm run build` (requires tree-sitter-cli) to regenerate src/parser.c.
 */

// Operator precedence table
const PREC = {
  ASSIGN: 1,
  PIPELINE: 2,
  OR: 3,
  AND: 4,
  EQUALITY: 5,
  COMPARISON: 6,
  CONCAT: 7,
  ADD: 8,
  MULTIPLY: 9,
  UNARY: 10,
  CALL: 11,
  MEMBER: 12,
};

module.exports = grammar({
  name: 'vimmo',

  // Whitespace and comments are ignored between tokens
  extras: ($) => [/[ \t\r\n]+/, $.comment],

  // Used for keyword extraction from identifiers
  word: ($) => $.identifier,

  // Explicit conflict resolution
  conflicts: ($) => [
    // `(x)` inside arrow_function params: `x` is both an identifier expr and a parameter
    [$.parameter, $._expression],
    // `return {` is ambiguous: `return <dict>` vs `return` followed by a block statement
    [$.return_statement],
    // `=> {` is ambiguous: block body vs dict literal expression body
    [$.block, $.dict],
  ],

  rules: {
    source_file: ($) => repeat($._statement),

    // ---------- Comments ----------
    comment: (_) => token(seq('//', /.*/)),

    // ---------- Statements ----------
    _statement: ($) =>
      choice(
        $.variable_declaration,
        $.function_declaration,
        $.class_declaration,
        $.if_statement,
        $.for_statement,
        $.while_statement,
        $.return_statement,
        $.echo_statement,
        $.import_statement,
        $.break_statement,
        $.continue_statement,
        $._expression,
      ),

    variable_declaration: ($) =>
      seq(
        field('kind', choice('let', 'const')),
        field('name', $.identifier),
        optional(seq(':', field('type', $._type))),
        '=',
        field('value', $._expression),
      ),

    function_declaration: ($) =>
      seq(
        optional(field('async_modifier', 'async')),
        'fn',
        field('name', $.identifier),
        field('parameters', $.parameter_list),
        optional(seq(':', field('return_type', $._type))),
        field('body', $.block),
      ),

    class_declaration: ($) =>
      seq(
        'class',
        field('name', $.identifier),
        field('body', $.class_body),
      ),

    class_body: ($) =>
      seq(
        '{',
        repeat(choice($.variable_declaration, $.function_declaration)),
        '}',
      ),

    parameter_list: ($) =>
      seq('(', optional(commaSep($.parameter)), ')'),

    parameter: ($) =>
      seq(
        field('name', $.identifier),
        optional(seq(':', field('type', $._type))),
      ),

    block: ($) => seq('{', repeat($._statement), '}'),

    if_statement: ($) =>
      prec.right(
        0,
        seq(
          'if',
          field('condition', $._expression),
          field('consequence', $.block),
          optional(
            seq(
              'else',
              field('alternative', choice($.if_statement, $.block)),
            ),
          ),
        ),
      ),

    for_statement: ($) =>
      seq(
        'for',
        field('variable', $.identifier),
        'in',
        field('iterable', $._expression),
        field('body', $.block),
      ),

    while_statement: ($) =>
      seq(
        'while',
        field('condition', $._expression),
        field('body', $.block),
      ),

    return_statement: ($) => seq('return', optional($._expression)),

    echo_statement: ($) => seq('echo', $._expression),

    import_statement: ($) =>
      seq(
        'import',
        '{',
        field('names', commaSep1($.identifier)),
        '}',
        'from',
        field('source', $.string),
      ),

    break_statement: (_) => 'break',
    continue_statement: (_) => 'continue',

    // ---------- Expressions ----------
    _expression: ($) =>
      choice(
        $.assignment_expression,
        $.pipeline_expression,
        $.binary_expression,
        $.unary_expression,
        $.await_expression,
        $.new_expression,
        $.call_expression,
        $.member_expression,
        $.index_expression,
        $.arrow_function,
        $.parenthesized_expression,
        $.identifier,
        $.number,
        $.string,
        $.boolean,
        $.null,
        $.array,
        $.dict,
      ),

    assignment_expression: ($) =>
      prec.right(
        PREC.ASSIGN,
        seq(
          field('left', $._expression),
          field('operator', choice('=', '+=', '-=')),
          field('right', $._expression),
        ),
      ),

    pipeline_expression: ($) =>
      prec.left(
        PREC.PIPELINE,
        seq(
          field('left', $._expression),
          '|>',
          field('right', $._expression),
        ),
      ),

    binary_expression: ($) =>
      choice(
        prec.left(PREC.OR, seq(field('left', $._expression), '||', field('right', $._expression))),
        prec.left(PREC.AND, seq(field('left', $._expression), '&&', field('right', $._expression))),
        prec.left(PREC.EQUALITY, seq(field('left', $._expression), choice('==', '!='), field('right', $._expression))),
        prec.left(PREC.COMPARISON, seq(field('left', $._expression), choice('<', '>', '<=', '>='), field('right', $._expression))),
        prec.left(PREC.CONCAT, seq(field('left', $._expression), '..', field('right', $._expression))),
        prec.left(PREC.ADD, seq(field('left', $._expression), choice('+', '-'), field('right', $._expression))),
        prec.left(PREC.MULTIPLY, seq(field('left', $._expression), choice('*', '/', '%'), field('right', $._expression))),
      ),

    unary_expression: ($) =>
      prec(
        PREC.UNARY,
        seq(
          field('operator', choice('!', '-')),
          field('operand', $._expression),
        ),
      ),

    await_expression: ($) => seq('await', field('value', $._expression)),

    new_expression: ($) =>
      seq(
        'new',
        field('class', $.identifier),
        '(',
        optional(commaSep($._expression)),
        ')',
      ),

    call_expression: ($) =>
      prec(
        PREC.CALL,
        seq(
          field('function', $._expression),
          '(',
          optional(commaSep($._expression)),
          ')',
        ),
      ),

    member_expression: ($) =>
      prec(
        PREC.MEMBER,
        seq(
          field('object', $._expression),
          '.',
          field('property', $.identifier),
        ),
      ),

    index_expression: ($) =>
      prec(
        PREC.MEMBER,
        seq(
          field('object', $._expression),
          '[',
          field('index', $._expression),
          ']',
        ),
      ),

    // (x) => expr  or  (x, y) => { ... }  or  x => expr
    arrow_function: ($) =>
      prec.right(
        0,
        seq(
          field(
            'parameters',
            choice(
              $.identifier,
              seq('(', optional(commaSep($.parameter)), ')'),
            ),
          ),
          '=>',
          field('body', choice($.block, $._expression)),
        ),
      ),

    parenthesized_expression: ($) => seq('(', $._expression, ')'),

    // ---------- Types ----------
    _type: (_) => choice('number', 'string', 'bool', 'list', 'dict', 'any', 'void'),

    // ---------- Literals ----------
    array: ($) => seq('[', optional(commaSep($._expression)), ']'),

    dict: ($) => seq('{', optional(commaSep($.dict_entry)), '}'),

    dict_entry: ($) =>
      seq(
        field('key', $.identifier),
        ':',
        field('value', $._expression),
      ),

    identifier: (_) => /[A-Za-z_][A-Za-z0-9_]*/,

    number: (_) => /[0-9]+(\.[0-9]+)?/,

    string: (_) =>
      choice(
        seq('"', /([^"\\]|\\.)*/, '"'),
        seq("'", /([^'\\]|\\.)*/, "'"),
      ),

    boolean: (_) => choice('true', 'false'),

    null: (_) => 'null',
  },
});

// Helper: zero-or-more comma-separated
function commaSep(rule) {
  return optional(commaSep1(rule));
}

// Helper: one-or-more comma-separated
function commaSep1(rule) {
  return seq(rule, repeat(seq(',', rule)));
}
