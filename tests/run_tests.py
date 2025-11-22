#!/usr/bin/env python3
"""
ТЕСТОВЫЙ РАННЕР ДЛЯ ЛЕКСИЧЕСКОГО АНАЛИЗАТОРА
Лабораторная работа №1

Запускает комплексное тестирование всех возможностей лексического анализатора.
"""

import os
import sys

# Добавляем путь к src для импортов
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from lexer import PseudocodeLexer, LexerAnalyzer

class LexerTestSuite:
    """Комплексный тестовый набор для лексического анализатора."""
    
    def __init__(self):
        self.lexer = PseudocodeLexer()
        self.analyzer = LexerAnalyzer()
        self.test_results = []
    
    def run_basic_tests(self):
        """Запускает базовые тесты на простых конструкциях."""
        print("🧪 БАЗОВЫЕ ТЕСТЫ")
        print("=" * 50)
        
        test_cases = [
            {
                'name': 'Простое присваивание',
                'code': 'x = 42;',
                'expected_tokens': ['ID', 'ASSIGN', 'NUMBER', 'SEMI'],
                'expected_count': 4
            },
            {
                'name': 'Арифметические операции',
                'code': 'result = (a + b) * c / 2;',
                'expected_tokens': ['ID', 'ASSIGN', 'LPAREN', 'ID', 'PLUS', 'ID', 'RPAREN', 'MUL', 'ID', 'DIV', 'NUMBER', 'SEMI'],
                'expected_count': 12
            },
            {
                'name': 'Условный оператор',
                'code': 'if (x > 5) { y = 1; }',
                'expected_tokens': ['IF', 'LPAREN', 'ID', 'GT', 'NUMBER', 'RPAREN', 'LBRACE', 'ID', 'ASSIGN', 'NUMBER', 'SEMI', 'RBRACE'],
                'expected_count': 12
            },
            {
                'name': 'Вывод строки',
                'code': 'print("Hello");',
                'expected_tokens': ['PRINT', 'LPAREN', 'STRING', 'RPAREN', 'SEMI'],
                'expected_count': 5
            },
            {
                'name': 'Комментарии',
                'code': '# комментарий\nx = 10;',
                'expected_tokens': ['ID', 'ASSIGN', 'NUMBER', 'SEMI'],
                'expected_count': 4
            },
        ]
        
        passed = 0
        for test in test_cases:
            print(f"\n🔸 {test['name']}")
            print(f"   Код: {test['code']}")
            
            tokens = self.lexer.tokenize(test['code'])
            token_types = [token['type'] for token in tokens]
            
            # Проверяем количество и типы токенов
            count_ok = len(tokens) == test['expected_count']
            types_ok = token_types == test['expected_tokens']
            
            if count_ok and types_ok:
                print("   ✅ ТЕСТ ПРОЙДЕН")
                passed += 1
            else:
                print("   ❌ ТЕСТ НЕ ПРОЙДЕН")
                if not count_ok:
                    print(f"      Ожидалось токенов: {test['expected_count']}, получено: {len(tokens)}")
                if not types_ok:
                    print(f"      Ожидалось: {test['expected_tokens']}")
                    print(f"      Получено:  {token_types}")
        
        self.test_results.append(('Базовые тесты', passed, len(test_cases)))
        return passed == len(test_cases)
    
    def run_operator_tests(self):
        """Тестирует все операторы сравнения и логические операторы."""
        print("\n🔧 ТЕСТЫ ОПЕРАТОРОВ")
        print("=" * 50)
        
        operator_tests = [
            ('>=', 'GEQ'), ('<=', 'LEQ'), ('==', 'EQ'), ('!=', 'NEQ'),
            ('>', 'GT'), ('<', 'LT'), ('&&', 'AND'), ('||', 'OR')
        ]
        
        passed = 0
        for operator, expected_type in operator_tests:
            code = f"x {operator} y"
            tokens = self.lexer.tokenize(code)
            
            # Должно быть 3 токена: ID, OPERATOR, ID
            if len(tokens) == 3 and tokens[1]['type'] == expected_type:
                print(f"   ✅ {operator} -> {expected_type}")
                passed += 1
            else:
                print(f"   ❌ {operator} -> ожидалось {expected_type}")
        
        self.test_results.append(('Тесты операторов', passed, len(operator_tests)))
        return passed == len(operator_tests)
    
    def run_keyword_tests(self):
        """Тестирует распознавание ключевых слов."""
        print("\n📚 ТЕСТЫ КЛЮЧЕВЫХ СЛОВ")
        print("=" * 50)
        
        keywords = [
            ('if', 'IF'), ('else', 'ELSE'), ('while', 'WHILE'),
            ('for', 'FOR'), ('in', 'IN'), ('range', 'RANGE'), ('print', 'PRINT')
        ]
        
        passed = 0
        for keyword, expected_type in keywords:
            code = f"{keyword} test"
            tokens = self.lexer.tokenize(code)
            
            if tokens and tokens[0]['type'] == expected_type:
                print(f"   ✅ {keyword} -> {expected_type}")
                passed += 1
            else:
                print(f"   ❌ {keyword} -> ожидалось {expected_type}")
        
        self.test_results.append(('Тесты ключевых слов', passed, len(keywords)))
        return passed == len(keywords)
    
    def run_file_tests(self):
        """Запускает тесты на файлах из test_cases."""
        print("\n📁 ТЕСТЫ НА ФАЙЛАХ")
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
                tokens = self.analyzer.analyze_file(full_path)
                if tokens:
                    print(f"   ✅ {file_path} -> {len(tokens)} токенов")
                    passed += 1
                else:
                    print(f"   ❌ {file_path} -> ошибка анализа")
            else:
                print(f"   ❌ {file_path} -> файл не найден")
        
        self.test_results.append(('Тесты на файлах', passed, len(test_files)))
        return passed == len(test_files)
    
    def run_error_handling_tests(self):
        """Тестирует обработку ошибок."""
        print("\n🚨 ТЕСТЫ ОБРАБОТКИ ОШИБОК")
        print("=" * 50)
        
        error_cases = [
            {
                'name': 'Неизвестный символ',
                'code': 'x = @ 5;',
                'should_fail': True
            },
            {
                'name': 'Корректный код',
                'code': 'x = 5;',
                'should_fail': False
            }
        ]
        
        passed = 0
        for test in error_cases:
            try:
                tokens = self.lexer.tokenize(test['code'])
                if not test['should_fail']:
                    print(f"   ✅ {test['name']} -> корректно обработан")
                    passed += 1
                else:
                    print(f"   ❌ {test['name']} -> ожидалась ошибка")
            except RuntimeError as e:
                if test['should_fail']:
                    print(f"   ✅ {test['name']} -> ошибка перехвачена: {e}")
                    passed += 1
                else:
                    print(f"   ❌ {test['name']} -> неожиданная ошибка: {e}")
        
        self.test_results.append(('Тесты обработки ошибок', passed, len(error_cases)))
        return passed == len(error_cases)
    
    def print_summary(self):
        """Выводит итоговый отчет по всем тестам."""
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ПО ТЕСТИРОВАНИЮ")
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
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        else:
            print(f"\n💥 НЕ ПРОЙДЕНО: {total_tests - total_passed} тестов")
    
    def run_all_tests(self):
        """Запускает все тесты."""
        print("🎯 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ ЛЕКСИЧЕСКОГО АНАЛИЗАТОРА")
        print("=" * 60)
        
        self.run_basic_tests()
        self.run_operator_tests()
        self.run_keyword_tests()
        self.run_file_tests()
        self.run_error_handling_tests()
        
        self.print_summary()
        
        return all(passed == total for _, passed, total in self.test_results)


def main():
    """Основная функция тестирования."""
    test_suite = LexerTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n" + "🎉" * 20)
        print("ЛЕКСИЧЕСКИЙ АНАЛИЗАТОР ГОТОВ К ИСПОЛЬЗОВАНИЮ!")
        print("ЛР1 ВЫПОЛНЕНА УСПЕШНО!")
        print("🎉" * 20)
        return 0
    else:
        print("\n⚠️  Для успешного завершения ЛР1 необходимо исправить ошибки")
        return 1


if __name__ == '__main__':
    sys.exit(main())