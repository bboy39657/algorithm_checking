#!/usr/bin/env python3
"""
СИНТАКСИЧЕСКИЙ АНАЛИЗАТОР ПСЕВДОКОДА
Лабораторная работа №2

Реализация парсера и построение AST (Abstract Syntax Tree)
для учебного языка псевдокода.
"""

import os
import sys
from typing import List, Dict, Any, Optional, Union
from enum import Enum

class NodeType(Enum):
    """Типы узлов AST."""
    PROGRAM = "PROGRAM"
    ASSIGNMENT = "ASSIGNMENT"
    CONDITIONAL = "CONDITIONAL"
    WHILE_LOOP = "WHILE_LOOP"
    FOR_LOOP = "FOR_LOOP"
    OUTPUT = "OUTPUT"
    BLOCK = "BLOCK"
    EXPRESSION = "EXPRESSION"
    CONDITION = "CONDITION"
    VARIABLE = "VARIABLE"
    NUMBER = "NUMBER"
    STRING = "STRING"
    BINARY_OP = "BINARY_OP"
    UNARY_OP = "UNARY_OP"
    ARRAY = "ARRAY"
    ARRAY_ACCESS = "ARRAY_ACCESS"


class ASTNode:
    """Базовый класс для узлов AST."""
    
    def __init__(self, node_type: NodeType, **kwargs):
        self.node_type = node_type
        self.line = kwargs.get('line', 0)
        self.column = kwargs.get('column', 0)
        
        # Динамически устанавливаем атрибуты
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        attrs = []
        for attr in dir(self):
            if not attr.startswith('_') and attr not in ['node_type', 'line', 'column']:
                value = getattr(self, attr)
                if value is not None:
                    attrs.append(f"{attr}={value}")
        
        return f"{self.node_type.value}({', '.join(attrs)})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует узел в словарь для сериализации."""
        result = {
            'node_type': self.node_type.value,
            'line': self.line,
            'column': self.column
        }
        
        for attr in dir(self):
            if not attr.startswith('_') and attr not in ['node_type', 'line', 'column', 'to_dict']:
                value = getattr(self, attr)
                if value is not None:
                    if isinstance(value, ASTNode):
                        result[attr] = value.to_dict()
                    elif isinstance(value, list):
                        result[attr] = [item.to_dict() if isinstance(item, ASTNode) else item 
                                      for item in value]
                    else:
                        result[attr] = value
        
        return result


class Parser:
    """
    Синтаксический анализатор для псевдокода.
    
    Преобразует последовательность токенов в AST (Abstract Syntax Tree).
    """
    
    def __init__(self, tokens: List[Dict[str, Any]]):
        """
        Инициализация парсера.
        
        Args:
            tokens: Список токенов от лексического анализатора
        """
        self.tokens = tokens
        self.current_pos = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def error(self, message: str):
        """Генерирует ошибку синтаксического анализа."""
        line = self.current_token.get('line', 0) if self.current_token else 0
        column = self.current_token.get('column', 0) if self.current_token else 0
        raise SyntaxError(f"Синтаксическая ошибка на строке {line}, позиция {column}: {message}")
    
    def eat(self, token_type: str) -> Dict[str, Any]:
        """
        Потребляет токен ожидаемого типа.
        
        Args:
            token_type: Ожидаемый тип токена
            
        Returns:
            Потребленный токен
        """
        if self.current_token and self.current_token['type'] == token_type:
            token = self.current_token
            self.current_pos += 1
            self.current_token = self.tokens[self.current_pos] if self.current_pos < len(self.tokens) else None
            return token
        else:
            expected = token_type
            actual = self.current_token['type'] if self.current_token else 'EOF'
            self.error(f"Ожидался {expected}, но получен {actual}")
    
    def peek(self, token_type: str) -> bool:
        """Проверяет, является ли следующий токен указанного типа."""
        return self.current_token and self.current_token['type'] == token_type
    
    def peek_next(self, token_type: str) -> bool:
        """Проверяет тип следующего токена без потребления текущего."""
        if self.current_pos + 1 < len(self.tokens):
            return self.tokens[self.current_pos + 1]['type'] == token_type
        return False
    
    def parse(self) -> ASTNode:
        """
        Запускает синтаксический анализ.
        
        Returns:
            Корневой узел AST (программа)
        """
        statements = []
        
        while self.current_token:
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
        
        return ASTNode(NodeType.PROGRAM, statements=statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Разбирает оператор."""
        if not self.current_token:
            return None
            
        token_type = self.current_token['type']
        
        if token_type == 'IF':
            return self.parse_conditional()
        elif token_type == 'WHILE':
            return self.parse_while_loop()
        elif token_type == 'FOR':
            return self.parse_for_loop()
        elif token_type == 'PRINT':
            return self.parse_output()
        elif token_type == 'LBRACE':
            return self.parse_block()
        elif token_type == 'ID' and self.peek_next('ASSIGN'):
            return self.parse_assignment()
        else:
            self.error(f"Неожиданный оператор: {token_type}")
    
    def parse_assignment(self) -> ASTNode:
        """Разбирает оператор присваивания."""
        variable_token = self.eat('ID')
        self.eat('ASSIGN')
        expr = self.parse_expression()
        self.eat('SEMI')
        
        return ASTNode(
            NodeType.ASSIGNMENT,
            variable=ASTNode(
                NodeType.VARIABLE,
                name=variable_token['text'],
                line=variable_token['line'],
                column=variable_token['column']
            ),
            value=expr,
            line=variable_token['line'],
            column=variable_token['column']
        )
    
    def parse_conditional(self) -> ASTNode:
        """Разбирает условный оператор."""
        if_token = self.eat('IF')
        self.eat('LPAREN')
        condition = self.parse_condition()
        self.eat('RPAREN')
        
        then_block = self.parse_block()
        
        else_block = None
        if self.peek('ELSE'):
            self.eat('ELSE')
            else_block = self.parse_block()
        
        return ASTNode(
            NodeType.CONDITIONAL,
            condition=condition,
            then_block=then_block,
            else_block=else_block,
            line=if_token['line'],
            column=if_token['column']
        )
    
    def parse_while_loop(self) -> ASTNode:
        """Разбирает цикл while."""
        while_token = self.eat('WHILE')
        self.eat('LPAREN')
        condition = self.parse_condition()
        self.eat('RPAREN')
        
        # Проверяем, есть ли тело цикла или просто точка с запятой
        if self.peek('SEMI'):
            # Цикл без тела - просто потребляем точку с запятой
            self.eat('SEMI')
            body = ASTNode(
                NodeType.BLOCK,
                statements=[],
                line=while_token['line'],
                column=while_token['column']
            )
        else:
            # Цикл с телом
            body = self.parse_block()
        
        return ASTNode(
            NodeType.WHILE_LOOP,
            condition=condition,
            body=body,
            line=while_token['line'],
            column=while_token['column']
        )
    
    def parse_for_loop(self) -> ASTNode:
        """Разбирает цикл for."""
        for_token = self.eat('FOR')
        variable_token = self.eat('ID')
        self.eat('IN')
        self.eat('RANGE')
        self.eat('LPAREN')
        start = self.parse_expression()
        self.eat('COMMA')
        end = self.parse_expression()
        self.eat('RPAREN')
        
        # Проверяем, есть ли тело цикла или просто точка с запятой
        if self.peek('SEMI'):
            # Цикл без тела - просто потребляем точку с запятой
            self.eat('SEMI')
            body = ASTNode(
                NodeType.BLOCK,
                statements=[],
                line=for_token['line'],
                column=for_token['column']
            )
        else:
            # Цикл с телом
            body = self.parse_block()
        
        return ASTNode(
            NodeType.FOR_LOOP,
            variable=ASTNode(
                NodeType.VARIABLE,
                name=variable_token['text'],
                line=variable_token['line'],
                column=variable_token['column']
            ),
            start=start,
            end=end,
            body=body,
            line=for_token['line'],
            column=for_token['column']
        )
    
    def parse_output(self) -> ASTNode:
        """Разбирает оператор вывода."""
        print_token = self.eat('PRINT')
        self.eat('LPAREN')
        expr = self.parse_expression()
        self.eat('RPAREN')
        self.eat('SEMI')
        
        return ASTNode(
            NodeType.OUTPUT,
            expression=expr,
            line=print_token['line'],
            column=print_token['column']
        )
    
    def parse_block(self) -> ASTNode:
        """Разбирает блок кода."""
        if self.peek('LBRACE'):
            lbrace_token = self.eat('LBRACE')
            statements = []
            
            while not self.peek('RBRACE') and self.current_token:
                statement = self.parse_statement()
                if statement:
                    statements.append(statement)
            
            self.eat('RBRACE')
            
            return ASTNode(
                NodeType.BLOCK,
                statements=statements,
                line=lbrace_token['line'],
                column=lbrace_token['column']
            )
        else:
            # Одиночный оператор как блок
            statement = self.parse_statement()
            return ASTNode(
                NodeType.BLOCK,
                statements=[statement] if statement else [],
                line=statement.line if statement else 0,
                column=statement.column if statement else 0
            )
    
    def parse_condition(self) -> ASTNode:
        """Разбирает условие."""
        left = self.parse_expression()
        
        # Проверяем операторы сравнения
        if self.current_token and self.current_token['type'] in ['EQ', 'NEQ', 'LT', 'GT', 'LEQ', 'GEQ']:
            operator = self.eat(self.current_token['type'])
            right = self.parse_expression()
            
            return ASTNode(
                NodeType.CONDITION,
                left=left,
                operator=operator['type'],
                right=right,
                line=left.line,
                column=left.column
            )
        else:
            # Одиночное выражение как условие
            return ASTNode(
                NodeType.CONDITION,
                left=left,
                operator=None,
                right=None,
                line=left.line,
                column=left.column
            )
    
    def parse_expression(self) -> ASTNode:
        """Разбирает выражение."""
        return self.parse_additive()
    
    def parse_additive(self) -> ASTNode:
        """Разбирает аддитивные операции."""
        node = self.parse_multiplicative()
        
        while self.current_token and self.current_token['type'] in ['PLUS', 'MINUS']:
            operator = self.eat(self.current_token['type'])
            right = self.parse_multiplicative()
            
            node = ASTNode(
                NodeType.BINARY_OP,
                left=node,
                operator=operator['type'],
                right=right,
                line=node.line,
                column=node.column
            )
        
        return node
    
    def parse_multiplicative(self) -> ASTNode:
        """Разбирает мультипликативные операции."""
        node = self.parse_primary()
        
        while self.current_token and self.current_token['type'] in ['MUL', 'DIV', 'MOD']:
            operator = self.eat(self.current_token['type'])
            right = self.parse_primary()
            
            node = ASTNode(
                NodeType.BINARY_OP,
                left=node,
                operator=operator['type'],
                right=right,
                line=node.line,
                column=node.column
            )
        
        return node
    
    def parse_primary(self) -> ASTNode:
        """Разбирает первичные выражения."""
        if not self.current_token:
            self.error("Неожиданный конец файла")
        
        token = self.current_token
        
        if token['type'] == 'NUMBER':
            self.eat('NUMBER')
            return ASTNode(
                NodeType.NUMBER,
                value=int(token['text']),
                line=token['line'],
                column=token['column']
            )
        elif token['type'] == 'STRING':
            self.eat('STRING')
            return ASTNode(
                NodeType.STRING,
                value=token['text'],
                line=token['line'],
                column=token['column']
            )
        elif token['type'] == 'ID':
            return self.parse_variable_or_array_access()
        elif token['type'] == 'LPAREN':
            self.eat('LPAREN')
            expr = self.parse_expression()
            self.eat('RPAREN')
            return expr
        elif token['type'] == 'LBRACKET':
            return self.parse_array_literal()
        else:
            self.error(f"Неожиданный токен в выражении: {token['type']}")

    def parse_variable_or_array_access(self) -> ASTNode:
        """Разбирает переменную или доступ к элементу массива."""
        variable_token = self.eat('ID')
        base_node = ASTNode(
            NodeType.VARIABLE,
            name=variable_token['text'],
            line=variable_token['line'],
            column=variable_token['column']
        )
        
        # Обработка цепочки доступов к массиву: arr[i][j]...
        while self.peek('LBRACKET'):
            self.eat('LBRACKET')
            index = self.parse_expression()
            self.eat('RBRACKET')
            base_node = ASTNode(
                NodeType.ARRAY_ACCESS,
                array=base_node,
                index=index,
                line=variable_token['line'],
                column=variable_token['column']
            )
        
        return base_node

    def parse_array_literal(self) -> ASTNode:
        """Разбирает литерал массива [element1, element2, ...]."""
        lbrace_token = self.eat('LBRACKET')
        elements = []
        
        # Если массив не пустой
        if not self.peek('RBRACKET'):
            elements.append(self.parse_expression())
            while self.peek('COMMA'):
                self.eat('COMMA')
                elements.append(self.parse_expression())
        
        self.eat('RBRACKET')
        
        return ASTNode(
            NodeType.ARRAY,
            elements=elements,
            line=lbrace_token['line'],
            column=lbrace_token['column']
        )


class ASTValidator:
    """
    Валидатор AST для проверки корректности структуры.
    """
    
    def __init__(self):
        self.errors = []
    
    def validate(self, ast: ASTNode) -> List[str]:
        """
        Валидирует AST.
        
        Args:
            ast: Корневой узел AST
            
        Returns:
            Список ошибок (пустой если все корректно)
        """
        self.errors = []
        self._validate_node(ast)
        return self.errors
    
    def _validate_node(self, node: ASTNode):
        """Рекурсивно валидирует узел AST."""
        if node.node_type == NodeType.PROGRAM:
            self._validate_program(node)
        elif node.node_type == NodeType.ASSIGNMENT:
            self._validate_assignment(node)
        elif node.node_type == NodeType.CONDITIONAL:
            self._validate_conditional(node)
        elif node.node_type == NodeType.WHILE_LOOP:
            self._validate_while_loop(node)
        elif node.node_type == NodeType.FOR_LOOP:
            self._validate_for_loop(node)
        elif node.node_type == NodeType.BLOCK:
            self._validate_block(node)
        
        # Рекурсивная валидация дочерних узлов
        for attr_name in dir(node):
            if not attr_name.startswith('_'):
                attr_value = getattr(node, attr_name)
                if isinstance(attr_value, ASTNode):
                    self._validate_node(attr_value)
                elif isinstance(attr_value, list):
                    for item in attr_value:
                        if isinstance(item, ASTNode):
                            self._validate_node(item)
    
    def _validate_program(self, node: ASTNode):
        """Валидирует программу."""
        if not hasattr(node, 'statements') or not node.statements:
            self.errors.append("Программа не должна быть пустой")
    
    def _validate_assignment(self, node: ASTNode):
        """Валидирует присваивание."""
        if not hasattr(node, 'variable') or not node.variable:
            self.errors.append(f"Присваивание без переменной на строке {node.line}")
        if not hasattr(node, 'value') or not node.value:
            self.errors.append(f"Присваивание без значения на строке {node.line}")
    
    def _validate_conditional(self, node: ASTNode):
        """Валидирует условный оператор."""
        if not hasattr(node, 'condition') or not node.condition:
            self.errors.append(f"Условный оператор без условия на строке {node.line}")
        if not hasattr(node, 'then_block') or not node.then_block:
            # Пустой блок - это нормально
            pass
    
    def _validate_while_loop(self, node: ASTNode):
        """Валидирует цикл while."""
        if not hasattr(node, 'condition') or not node.condition:
            self.errors.append(f"Цикл while без условия на строке {node.line}")
        if not hasattr(node, 'body') or not node.body:
            # Пустое тело цикла - это нормально
            pass
    
    def _validate_for_loop(self, node: ASTNode):
        """Валидирует цикл for."""
        if not hasattr(node, 'variable') or not node.variable:
            self.errors.append(f"Цикл for без переменной на строке {node.line}")
        if not hasattr(node, 'start') or not node.start:
            self.errors.append(f"Цикл for без начального значения на строке {node.line}")
        if not hasattr(node, 'end') or not node.end:
            self.errors.append(f"Цикл for без конечного значения на строке {node.line}")
        if not hasattr(node, 'body') or not node.body:
            # Пустое тело цикла - это нормально
            pass
    
    def _validate_block(self, node: ASTNode):
        """Валидирует блок кода."""
        if not hasattr(node, 'statements'):
            self.errors.append(f"Блок без операторов на строке {node.line}")


    def print_ast(node: ASTNode, level: int = 0):
        """
        Рекурсивно выводит AST в читаемом формате.
        
        Args:
            node: Узел AST для вывода
            level: Текущий уровень вложенности
        """
        indent = "  " * level
        node_info = f"{node.node_type.value}"
        
        # Добавляем специфичную информацию для разных типов узлов
        if node.node_type == NodeType.VARIABLE:
            node_info += f"({node.name})"
        elif node.node_type == NodeType.NUMBER:
            node_info += f"({node.value})"
        elif node.node_type == NodeType.STRING:
            node_info += f"('{node.value}')"
        elif node.node_type == NodeType.ASSIGNMENT:
            node_info += f"({node.variable.name})"
        elif node.node_type == NodeType.BINARY_OP:
            node_info += f"({node.operator})"
        elif node.node_type == NodeType.ARRAY:
            node_info += f"[{len(node.elements) if hasattr(node, 'elements') else 0} elements]"
        elif node.node_type == NodeType.ARRAY_ACCESS:
            node_info += f"(access)"
        
        print(f"{indent}├─ {node_info}")
        
        # Рекурсивно обходим дочерние узлы
        for attr_name in dir(node):
            if not attr_name.startswith('_') and attr_name not in ['node_type', 'line', 'column']:
                attr_value = getattr(node, attr_name)
                
                if isinstance(attr_value, ASTNode):
                    print(f"{indent}│  └─ {attr_name}:")
                    print_ast(attr_value, level + 2)
                elif isinstance(attr_value, list) and attr_value:
                    print(f"{indent}│  └─ {attr_name}:")
                    for i, item in enumerate(attr_value):
                        if isinstance(item, ASTNode):
                            print(f"{indent}│     [{i}]:")
                            print_ast(item, level + 3)
                        else:
                            print(f"{indent}│     [{i}]: {item}")