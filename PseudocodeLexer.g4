grammar PseudocodeLexer;

// Лексемы
NUMBER    : [0-9]+;
ID        : [a-zA-Z_][a-zA-Z_0-9]*;
ASSIGN    : '=';
PLUS      : '+';
MINUS     : '-';  
MUL       : '*';
DIV       : '/';
EQ        : '==';
NEQ       : '!=';
LT        : '<';
GT        : '>';
LEQ       : '<=';
GEQ       : '>=';
AND       : '&&';
OR        : '||';
NOT       : '!';
IF        : 'if';
ELSE      : 'else';
WHILE     : 'while';
FOR       : 'for';
IN        : 'in';
RANGE     : 'range';
PRINT     : 'print';
LBRACE    : '{';
RBRACE    : '}';
LPAREN    : '(';
RPAREN    : ')';
SEMI      : ';';
COMMA     : ',';
STRING    : '"' ~["]* '"';
WS        : [ \t\r\n]+ -> skip;

// Синтаксис
program     : statement+;
statement   : assignment | conditional | loop | output;
assignment  : ID ASSIGN expression SEMI;
conditional : IF condition block (ELSE block)?;
loop        : WHILE condition block | FOR ID IN RANGE LPAREN NUMBER COMMA NUMBER RPAREN block;
output      : PRINT LPAREN expression RPAREN SEMI;

condition   : expression (comparison expression)?;
comparison  : EQ | NEQ | LT | GT | LEQ | GEQ;
expression  : term ( (PLUS | MINUS) term )*;
term        : factor ( (MUL | DIV) factor )*;
factor      : NUMBER | ID | LPAREN expression RPAREN | string;
string      : STRING;

block       : LBRACE statement* RBRACE | statement;
