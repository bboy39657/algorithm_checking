#!/usr/bin/env python3
"""
ИНТЕГРИРОВАННЫЙ АНАЛИЗАТОР ПСЕВДОКОДА
Лабораторная работа №2

Объединяет лексический и синтаксический анализ,
построение AST и валидацию структуры.
"""

import os
import sys
import json
from typing import List, Dict, Any

# Добавляем путь для импортов
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.lexer import PseudocodeLexer, LexerAnalyzer
from src.parser import Parser, ASTValidator, ASTNode


class PseudocodeAnalyzer:
    """
    Интегрированный анализатор псевдокода.
    
    Объединяет все этапы анализа:
    1. Лексический анализ
    2. Синтаксический анализ  
    3. Построение AST
    4. Валидация структуры
    """
    
    def __init__(self):
        """Инициализация анализатора."""
        self.lexer_analyzer = LexerAnalyzer()
        self.ast_validator = ASTValidator()
        self.tokens = []
        self.ast = None
        self.validation_errors = []
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Выполняет полный анализ кода.
        
        Args:
            code: Исходный код на псевдокоде
            
        Returns:
            Словарь с результатами анализа
        """
        try:
            # Лексический анализ
            self.tokens = self.lexer_analyzer.analyze(code)
            
            if not self.tokens:
                return {
                    'success': False,
                    'errors': ['Лексический анализ не дал результатов'],
                    'tokens': [],
                    'ast': None
                }
            
            # Синтаксический анализ и построение AST
            parser = Parser(self.tokens)
            self.ast = parser.parse()
            
            # Валидация AST
            self.validation_errors = self.ast_validator.validate(self.ast)
            
            return {
                'success': len(self.validation_errors) == 0,
                'errors': self.validation_errors,
                'tokens': self.tokens,
                'ast': self.ast,
                'token_count': len(self.tokens),
                'ast_json': self.ast.to_dict() if self.ast else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [f"Ошибка анализа: {str(e)}"],
                'tokens': self.tokens,
                'ast': None,
                'token_count': len(self.tokens),
                'ast_json': None
            }
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Анализирует код из файла.
        
        Args:
            file_path: Путь к файлу с кодом
            
        Returns:
            Словарь с результатами анализа
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            return self.analyze(code)
        except FileNotFoundError:
            return {
                'success': False,
                'errors': [f"Файл не найден: {file_path}"],
                'tokens': [],
                'ast': None
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [f"Ошибка чтения файла: {str(e)}"],
                'tokens': [],
                'ast': None
            }
    
    def print_ast(self, node: ASTNode, level: int = 0):
        """
        Рекурсивно выводит AST в читаемом формате.
        
        Args:
            node: Узел AST для вывода
            level: Текущий уровень вложенности
        """
        indent = "  " * level
        node_info = f"{node.node_type.value}"
        
        # Добавляем специфичную информацию для разных типов узлов
        if node.node_type.value == 'VARIABLE':
            node_info += f"({node.name})"
        elif node.node_type.value == 'NUMBER':
            node_info += f"({node.value})"
        elif node.node_type.value == 'STRING':
            node_info += f"('{node.value}')"
        elif node.node_type.value == 'ASSIGNMENT':
            node_info += f"({node.variable.name})"
        elif node.node_type.value == 'BINARY_OP':
            node_info += f"({node.operator})"
        elif node.node_type.value == 'ARRAY':
            node_info += f"[{len(node.elements) if hasattr(node, 'elements') else 0} elements]"
        elif node.node_type.value == 'ARRAY_ACCESS':
            node_info += f"(access)"
        
        print(f"{indent}├─ {node_info}")
        
        # Рекурсивно обходим дочерние узлы
        for attr_name in dir(node):
            if not attr_name.startswith('_') and attr_name not in ['node_type', 'line', 'column']:
                attr_value = getattr(node, attr_name)
                
                if isinstance(attr_value, ASTNode):
                    print(f"{indent}│  └─ {attr_name}:")
                    self.print_ast(attr_value, level + 2)
                elif isinstance(attr_value, list) and attr_value:
                    print(f"{indent}│  └─ {attr_name}:")
                    for i, item in enumerate(attr_value):
                        if isinstance(item, ASTNode):
                            print(f"{indent}│     [{i}]:")
                            self.print_ast(item, level + 3)
                        else:
                            print(f"{indent}│     [{i}]: {item}")
    
    def print_analysis_report(self, result: Dict[str, Any], title: str = "АНАЛИЗ ПСЕВДОКОДА"):
        """
        Выводит подробный отчет анализа.
        
        Args:
            result: Результат анализа
            title: Заголовок отчета
        """
        print("=" * 80)
        print(title)
        print("=" * 80)
        
        # Статус анализа
        if result['success']:
            print("✅ АНАЛИЗ УСПЕШЕН")
        else:
            print("❌ ОБНАРУЖЕНЫ ОШИБКИ")
        
        # Информация о токенах
        print(f"\n📊 ЛЕКСИЧЕСКИЙ АНАЛИЗ:")
        print(f"   Найдено токенов: {result['token_count']}")
        
        # Ошибки
        if result['errors']:
            print(f"\n🚨 ОШИБКИ ВАЛИДАЦИИ:")
            for error in result['errors']:
                print(f"   • {error}")
        
        # AST
        if result['ast']:
            print(f"\n🌳 АБСТРАКТНОЕ СИНТАКСИЧЕСКОЕ ДЕРЕВО (AST):")
            self.print_ast(result['ast'])
        
        # JSON представление
        if result.get('ast_json'):
            print(f"\n📄 JSON ПРЕДСТАВЛЕНИЕ AST:")
            print(json.dumps(result['ast_json'], indent=2, ensure_ascii=False))
    
    def export_ast_json(self, file_path: str):
        """
        Экспортирует AST в JSON файл.
        
        Args:
            file_path: Путь для сохранения JSON
        """
        if self.ast:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.ast.to_dict(), f, indent=2, ensure_ascii=False)
                print(f"✅ AST экспортирован в: {file_path}")
            except Exception as e:
                print(f"❌ Ошибка экспорта: {e}")
        else:
            print("❌ Нет AST для экспорта")


def demonstrate_parser_capabilities():
    """
    Демонстрирует возможности синтаксического анализатора.
    """
    print("🎯 ДЕМОНСТРАЦИЯ СИНТАКСИЧЕСКОГО АНАЛИЗАТОРА")
    print("=" * 60)
    
    test_cases = [
        {
            'name': 'Простая программа',
            'code': """
x = 10;
y = x + 5;
print("Result: " + y);
"""
        },
        {
            'name': 'Условные операторы',
            'code': """
if (x > 5) {
    print("x is large");
} else {
    print("x is small");
}
"""
        },
        {
            'name': 'Циклы',
            'code': """
for i in range(1, 5) {
    print("Number: " + i);
}

counter = 3;
while (counter > 0) {
    print("Counter: " + counter);
    counter = counter - 1;
}
"""
        },
        {
            'name': 'Комплексная программа',
            'code': """
# Вычисление суммы четных чисел
sum = 0;
n = 10;

for i in range(1, n + 1) {
    if (i % 2 == 0) {
        sum = sum + i;
        print("Added: " + i);
    }
}

print("Total sum: " + sum);
"""
        }
    ]
    
    analyzer = PseudocodeAnalyzer()
    
    for test_case in test_cases:
        print(f"\n🔹 {test_case['name']}:")
        print("-" * 40)
        result = analyzer.analyze(test_case['code'])
        
        if result['success']:
            print(f"   ✅ Успешно! Токенов: {result['token_count']}")
        else:
            print(f"   ❌ Ошибки: {len(result['errors'])}")
            for error in result['errors']:
                print(f"      • {error}")


def analyze_example_files():
    """
    Анализирует примеры из файлов.
    """
    print("\n📁 АНАЛИЗ ПРИМЕРОВ ИЗ ФАЙЛОВ")
    print("=" * 60)
    
    analyzer = PseudocodeAnalyzer()
    test_files = [
        'tests/test_cases/basic.pseudo',
        'tests/test_cases/arithmetic.pseudo',
        'tests/test_cases/loops.pseudo',
        'examples/factorial.pseudo',
        'examples/max_finder.pseudo'
    ]
    
    for file_path in test_files:
        full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
        
        if os.path.exists(full_path):
            print(f"\n📄 Анализ файла: {file_path}")
            result = analyzer.analyze_file(full_path)
            
            if result['success']:
                print(f"   ✅ Успешно! Токенов: {result['token_count']}")
                # Краткая информация об AST
                if result['ast']:
                    statements_count = len(result['ast'].statements) if hasattr(result['ast'], 'statements') else 0
                    print(f"   🌳 AST узлов: {statements_count} операторов")
            else:
                print(f"   ❌ Ошибки: {len(result['errors'])}")
                for error in result['errors']:
                    print(f"      • {error}")
        else:
            print(f"   ❌ Файл не найден: {full_path}")


def main():
    """
    Основная функция - демонстрация работы синтаксического анализатора.
    """
    print("🎯 СИНТАКСИЧЕСКИЙ АНАЛИЗАТОР ПСЕВДОКОДА - ЛР2")
    print("=" * 60)
    
    # Демонстрация возможностей
    demonstrate_parser_capabilities()
    
    # Анализ файлов
    analyze_example_files()
    
    # Детальный анализ примера
    print("\n" + "=" * 60)
    print("📊 ДЕТАЛЬНЫЙ АНАЛИЗ ПРИМЕРА")
    print("=" * 60)
    
    example_code = """
# Программа вычисления факториала с проверками
n = 5;
factorial = 1;

print("Calculating factorial of " + n);

if (n > 0) {
    for i in range(1, n + 1) {
        factorial = factorial * i;
        print("Step " + i + ": factorial = " + factorial);
    }
    print("Result: " + n + "! = " + factorial);
} else if (n == 0) {
    print("0! = 1");
} else {
    print("Cannot calculate factorial of negative number");
}
"""

    analyzer = PseudocodeAnalyzer()
    result = analyzer.analyze(example_code)
    analyzer.print_analysis_report(result, "ДЕТАЛЬНЫЙ АНАЛИЗ ПРОГРАММЫ")
    
    # Экспорт AST (опционально)
    # analyzer.export_ast_json("ast_export.json")
    
    print("\n" + "=" * 60)
    if result['success']:
        print("✅ СИНТАКСИЧЕСКИЙ АНАЛИЗАТОР РАБОТАЕТ КОРРЕКТНО!")
    else:
        print("❌ ТРЕБУЮТСЯ ИСПРАВЛЕНИЯ")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()