#!/usr/bin/env python3
"""
ТЕСТОВЫЙ РАННЕР ДЛЯ СИНТАКСИЧЕСКОГО АНАЛИЗАТОРА
Лабораторная работа №2
"""

import os
import sys

# Добавляем путь к src для импортов
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from analyzer import PseudocodeAnalyzer
from parser import Parser, ASTValidator

class SyntaxTestSuite:
    """Комплексный тестовый набор для синтаксического анализатора."""
    
    def __init__(self):
        self.analyzer = PseudocodeAnalyzer()
        self.test_results = []
    
    def run_basic_syntax_tests(self):
        """Запускает базовые тесты синтаксиса."""
        print("🧪 БАЗОВЫЕ СИНТАКСИЧЕСКИЕ ТЕСТЫ")
        print("=" * 50)
        
        test_cases = [
            {
                'name': 'Простое присваивание',
                'code': 'x = 42;',
                'should_pass': True
            },
            {
                'name': 'Арифметические выражения',
                'code': 'result = (a + b) * c / 2;',
                'should_pass': True
            },
            {
                'name': 'Условный оператор',
                'code': 'if (x > 5) { y = 1; }',
                'should_pass': True
            },
            {
                'name': 'Цикл for',
                'code': 'for i in range(1, 5) { print(i); }',
                'should_pass': True
            },
            {
                'name': 'Цикл while',
                'code': 'while (x > 0) { x = x - 1; }',
                'should_pass': True
            },
            {
                'name': 'Незакрытый блок',
                'code': 'if (x > 5) { y = 1;',
                'should_pass': False
            },
            {
                'name': 'Незакрытая скобка',
                'code': 'x = (5 + 3;',
                'should_pass': False
            }
        ]
        
        passed = 0
        for test in test_cases:
            print(f"\n🔸 {test['name']}")
            print(f"   Код: {test['code']}")
            
            result = self.analyzer.analyze(test['code'])
            
            if result['success'] == test['should_pass']:
                print("   ✅ ТЕСТ ПРОЙДЕН")
                passed += 1
            else:
                print("   ❌ ТЕСТ НЕ ПРОЙДЕН")
                if result['errors']:
                    print(f"      Ошибки: {result['errors']}")
        
        self.test_results.append(('Базовые синтаксические тесты', passed, len(test_cases)))
        return passed == len(test_cases)
    
    def run_ast_structure_tests(self):
        """Тестирует структуру AST."""
        print("\n🌳 ТЕСТЫ СТРУКТУРЫ AST")
        print("=" * 50)
        
        test_cases = [
            {
                'name': 'AST присваивания',
                'code': 'x = 10;',
                'expected_nodes': ['PROGRAM', 'ASSIGNMENT', 'VARIABLE', 'NUMBER']
            },
            {
                'name': 'AST условия',
                'code': 'if (x > 5) { y = 1; }',
                'expected_nodes': ['PROGRAM', 'CONDITIONAL', 'CONDITION', 'BLOCK', 'ASSIGNMENT']
            },
            {
                'name': 'AST цикла for',
                'code': 'for i in range(1, 5) { print(i); }',
                'expected_nodes': ['PROGRAM', 'FOR_LOOP', 'BLOCK', 'OUTPUT']
            }
        ]
        
        passed = 0
        for test in test_cases:
            print(f"\n🔸 {test['name']}")
            print(f"   Код: {test['code']}")
            
            result = self.analyzer.analyze(test['code'])
            
            if result['success'] and result['ast']:
                # Проверяем наличие ожидаемых узлов в AST
                ast_json = result['ast_json']
                found_nodes = self._collect_node_types(ast_json)
                
                missing_nodes = [node for node in test['expected_nodes'] if node not in found_nodes]
                
                if not missing_nodes:
                    print("   ✅ Структура AST корректна")
                    passed += 1
                else:
                    print(f"   ❌ Отсутствуют узлы: {missing_nodes}")
                    print(f"      Найдены: {found_nodes}")
            else:
                print("   ❌ Не удалось построить AST")
        
        self.test_results.append(('Тесты структуры AST', passed, len(test_cases)))
        return passed == len(test_cases)
    
    def _collect_node_types(self, node, collected=None):
        """Рекурсивно собирает типы узлов AST."""
        if collected is None:
            collected = set()
        
        if isinstance(node, dict):
            if 'node_type' in node:
                collected.add(node['node_type'])
            
            # Рекурсивно обходим все поля
            for key, value in node.items():
                if key != 'node_type':  # Избегаем бесконечной рекурсии
                    if isinstance(value, dict):
                        self._collect_node_types(value, collected)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                self._collect_node_types(item, collected)
        
        return collected
    
    def run_validation_tests(self):
        """Тестирует валидацию структуры."""
        print("\n🔍 ТЕСТЫ ВАЛИДАЦИИ СТРУКТУРЫ")
        print("=" * 50)
        
        test_cases = [
            {
                'name': 'Корректная структура',
                'code': """
                if (x > 5) {
                    y = 10;
                } else {
                    y = 0;
                }
                """,
                'should_validate': True
            },
            {
                'name': 'Пустой блок then',
                'code': 'if (x > 5) { }',
                'should_validate': True
            },
            {
                'name': 'Цикл без тела',
                'code': 'while (x > 0);',
                'should_validate': True
            }
        ]
        
        passed = 0
        for test in test_cases:
            print(f"\n🔸 {test['name']}")
            print(f"   Код: {test['code']}")
            
            result = self.analyzer.analyze(test['code'])
            validation_ok = len(result['errors']) == 0
            
            if validation_ok == test['should_validate']:
                print("   ✅ ВАЛИДАЦИЯ ПРОЙДЕНА")
                passed += 1
            else:
                print("   ❌ ВАЛИДАЦИЯ НЕ ПРОЙДЕНА")
                if result['errors']:
                    print(f"      Ошибки валидации: {result['errors']}")
        
        self.test_results.append(('Тесты валидации', passed, len(test_cases)))
        return passed == len(test_cases)
    
    def run_integration_tests(self):
        """Запускает интеграционные тесты на файлах."""
        print("\n📁 ИНТЕГРАЦИОННЫЕ ТЕСТЫ")
        print("=" * 50)
        
        test_files = [
            'test_cases/basic.pseudo',
            'test_cases/arithmetic.pseudo',
            'test_cases/loops.pseudo'
        ]
        
        passed = 0
        for file_path in test_files:
            full_path = os.path.join(os.path.dirname(__file__), file_path)
            
            if os.path.exists(full_path):
                print(f"\n🔸 Анализ {file_path}")
                result = self.analyzer.analyze_file(full_path)
                
                if result['success']:
                    print("   ✅ Файл успешно проанализирован")
                    passed += 1
                else:
                    print(f"   ❌ Ошибки анализа: {result['errors']}")
            else:
                print(f"   ❌ Файл не найден: {file_path}")
        
        self.test_results.append(('Интеграционные тесты', passed, len(test_files)))
        return passed == len(test_files)
    
    def print_summary(self):
        """Выводит итоговый отчет по всем тестам."""
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ПО ТЕСТИРОВАНИЮ СИНТАКСИЧЕСКОГО АНАЛИЗАТОРА")
        print("=" * 60)
        
        total_passed = 0
        total_tests = 0
        
        for category, passed, total in self.test_results:
            percentage = (passed / total) * 100 if total > 0 else 0
            status = "✅" if passed == total else "❌"
            print(f"{status} {category}: {passed}/{total} ({percentage:.1f}%)")
            total_passed += passed
            total_tests += total
        
        overall_percentage = (total_passed / total_tests) * 100 if total_tests > 0 else 0
        print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {total_passed}/{total_tests} ({overall_percentage:.1f}%)")
        
        if total_passed == total_tests:
            print("\n🎉 ВСЕ ТЕСТЫ СИНТАКСИЧЕСКОГО АНАЛИЗАТОРА ПРОЙДЕНЫ УСПЕШНО!")
        else:
            print(f"\n💥 НЕ ПРОЙДЕНО: {total_tests - total_passed} тестов")
    
    def run_all_tests(self):
        """Запускает все тесты синтаксического анализатора."""
        print("🎯 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ СИНТАКСИЧЕСКОГО АНАЛИЗАТОРА")
        print("=" * 60)
        
        self.run_basic_syntax_tests()
        self.run_ast_structure_tests()
        self.run_validation_tests()
        self.run_integration_tests()
        
        self.print_summary()
        
        return all(passed == total for _, passed, total in self.test_results)


def main():
    """Основная функция тестирования."""
    test_suite = SyntaxTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n" + "🎉" * 20)
        print("СИНТАКСИЧЕСКИЙ АНАЛИЗАТОР ГОТОВ К ИСПОЛЬЗОВАНИЮ!")
        print("ЛР2 ВЫПОЛНЕНА УСПЕШНО!")
        print("🎉" * 20)
        return 0
    else:
        print("\n⚠️  Для успешного завершения ЛР2 необходимо исправить ошибки")
        return 1


if __name__ == '__main__':
    sys.exit(main())