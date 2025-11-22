#!/usr/bin/env python3
import sys
import os
from antlr4 import *

try:
    from FixedPseudocodeLexer import FixedPseudocodeLexer
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Сначала выполните: python fixed_setup.py и выберите вариант 2")
    sys.exit(1)

class FixedLexerAnalyzer:
    def __init__(self):
        self.tokens_info = []
    
    def analyze(self, code):
        self.tokens_info = []
        input_stream = InputStream(code)
        lexer = FixedPseudocodeLexer(input_stream)
        tokens = lexer.getAllTokens()
        
        for token in tokens:
            token_type = lexer.symbolicNames[token.type]
            # Пропускаем пробельные символы
            if token_type == 'WS':
                continue
                
            token_info = {
                'text': token.text,
                'type': token_type,
                'line': token.line,
                'column': token.column
            }
            self.tokens_info.append(token_info)
        
        return self.tokens_info
    
    def print_tokens(self):
        if not self.tokens_info:
            print("Нет токенов для отображения")
            return
            
        print("=" * 80)
        print("ЛЕКСИЧЕСКИЙ АНАЛИЗ (Fixed ANTLR Lexer)")
        print("=" * 80)
        print(f"{'ТОКЕН':<20} {'ТИП':<20} {'СТРОКА':<8} {'ПОЗИЦИЯ':<8}")
        print("-" * 80)
        
        for token in self.tokens_info:
            print(f"{token['text']:<20} {token['type']:<20} {token['line']:<8} {token['column']:<8}")
        
        print("-" * 80)
        print(f"Всего токенов: {len(self.tokens_info)}")

def test_fixed_lexer():
    """Тестируем исправленный ANTLR лексер"""
    print("🧪 Тест исправленного ANTLR лексера")
    print("-" * 40)
    
    test_cases = [
        "x = 10;",
        "if (x >= 5) { y = 1; }",
        'print("Hello");'
    ]
    
    analyzer = FixedLexerAnalyzer()
    
    for i, code in enumerate(test_cases, 1):
        print(f"\nТест {i}: {code}")
        try:
            tokens = analyzer.analyze(code)
            
            for token in tokens:
                print(f"  '{token['text']}' -> {token['type']}")
            
            print(f"  Всего токенов: {len(tokens)}")
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")

def main():
    print("🎯 Лексический анализатор псевдокода (Fixed ANTLR Version)")
    print("=" * 50)
    
    # Тестируем базовый функционал
    test_fixed_lexer()
    
    print("\n" + "=" * 50)
    print("📊 Полный анализ примера кода")
    print("=" * 50)
    
    # Пример псевдокода для анализа
    test_code = """
x = 10;
if (x >= 5) {
    y = x * 2;
    print("Result");
}
"""
    
    analyzer = FixedLexerAnalyzer()
    try:
        tokens = analyzer.analyze(test_code)
        analyzer.print_tokens()
        
        # Статистика по типам токенов
        token_types = {}
        for token in tokens:
            token_type = token['type']
            token_types[token_type] = token_types.get(token_type, 0) + 1
        
        print("\n📈 СТАТИСТИКА ПО ТИПАМ ТОКЕНОВ:")
        for token_type, count in sorted(token_types.items()):
            print(f"  {token_type}: {count}")
            
    except Exception as e:
        print(f"❌ Ошибка при анализе: {e}")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
