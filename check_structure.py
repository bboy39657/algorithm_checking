#!/usr/bin/env python3
"""
ПРОВЕРКА СТРУКТУРЫ ПРОЕКТА
Утилита для проверки корректности структуры репозитория.
"""

import os
import sys

def check_structure():
    """Проверяет структуру проекта."""
    print("🔍 ПРОВЕРКА СТРУКТУРЫ ПРОЕКТА")
    print("=" * 60)
    
    # Обязательные директории
    required_dirs = [
        'docs',
        'src',
        'src/grammars',
        'tests', 
        'tests/test_cases',
        'examples'
    ]
    
    # Обязательные файлы
    required_files = [
        '.gitignore',
        'requirements.txt',
        'README.md',
        'src/lexer.py',
        'src/grammars/Pseudocode.g4',
        'tests/run_tests.py',
        'tests/test_cases/basic.pseudo',
        'tests/test_cases/arithmetic.pseudo', 
        'tests/test_cases/loops.pseudo',
        'examples/factorial.pseudo',
        'examples/max_finder.pseudo',
        'src/parser.py',
        'src/analyzer.py', 
        'tests/run_syntax_tests.py'
    ]
    
    print("📁 ПРОВЕРКА ДИРЕКТОРИЙ:")
    all_dirs_ok = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ❌ {dir_path}/")
            all_dirs_ok = False
    
    print("\n📄 ПРОВЕРКА ФАЙЛОВ:")
    all_files_ok = True
    for file_path in required_files:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            all_files_ok = False
    
    # Проверка отсутствия нежелательных файлов (исключая .venv)
    print("\n🚫 ПРОВЕРКА ОТСУТСТВИЯ НЕНУЖНЫХ ФАЙЛОВ:")
    unwanted_items = [
        'venv', '__pycache__',
        'FixedPseudocodeLexer.py', 'FixedPseudocodeParser.py',
        'PseudocodeLexer.py', 'PseudocodeParser.py'
    ]
    
    unwanted_found = False
    for item in unwanted_items:
        if os.path.exists(item):
            print(f"  ⚠️  Найден нежелательный элемент: {item}")
            unwanted_found = True
        else:
            print(f"  ✅ {item} отсутствует")
    
    # .venv - это нормально, но сообщим о нем
    if os.path.exists('.venv'):
        print("  ℹ️  .venv присутствует (это нормально для виртуального окружения)")
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("📊 ИТОГИ ПРОВЕРКИ СТРУКТУРЫ:")
    
    if all_dirs_ok and all_files_ok and not unwanted_found:
        print("🎉 СТРУКТУРА ПРОЕКТА КОРРЕКТНА!")
        print("\n💡 КОМАНДЫ ДЛЯ ЗАПУСКА:")
        print("  python src/lexer.py          # Запуск основного лексера")
        print("  python tests/run_tests.py    # Запуск тестов")
        print("  python check_structure.py    # Проверка структуры")
        return True
    else:
        print("❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ С СТРУКТУРОЙ!")
        if not all_dirs_ok:
            print("  - Отсутствуют некоторые директории")
        if not all_files_ok:
            print("  - Отсутствуют некоторые файлы")
        if unwanted_found:
            print("  - Найдены нежелательные файлы")
        return False

if __name__ == '__main__':
    success = check_structure()
    sys.exit(0 if success else 1)
