import sys
import os
from antlr4 import *
from PseudocodeLexer import PseudocodeLexer

class LexerAnalyzer:
    def __init__(self):
        self.tokens_info = []
    
    def analyze(self, code):
        input_stream = InputStream(code)
        lexer = PseudocodeLexer(input_stream)
        tokens = lexer.getAllTokens()
        
        for token in tokens:
            token_type = lexer.symbolicNames[token.type]
            # Пропускаем WS токены
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
        print("=" * 80)
        print("ЛЕКСИЧЕСКИЙ АНАЛИЗ")
        print("=" * 80)
        print(f"{'ТОКЕН':<20} {'ТИП':<25} {'СТРОКА':<8} {'ПОЗИЦИЯ':<8}")
        print("-" * 80)
        
        for token in self.tokens_info:
            print(f"{token['text']:<20} {token['type']:<25} {token['line']:<8} {token['column']:<8}")
        
        print("-" * 80)
        print(f"Всего токенов: {len(self.tokens_info)}")

def test_basic_lexer():
    """Простой тест лексера"""
    test_code = "x = 10;"
    print("Базовый тест лексера:")
    print(f"Код: {test_code}")
    
    input_stream = InputStream(test_code)
    lexer = PseudocodeLexer(input_stream)
    
    token = lexer.nextToken()
    while token.type != Token.EOF:
        if lexer.symbolicNames[token.type] != 'WS':
            print(f"Токен: '{token.text}' -> {lexer.symbolicNames[token.type]}")
        token = lexer.nextToken()

def main():
    # Сначала протестируем базовый функционал
    test_basic_lexer()
    print("\n" + "="*50 + "\n")
    
    # Пример псевдокода для анализа
    test_code = """
x = 10;
if (x > 5) {
    y = x * 2;
    print("Result");
} else {
    y = 0;
}

for i in range(1, 5) {
    print(i);
}

while (x > 0 && y < 100) {
    x = x - 1;
    y = y + 10;
}
"""
    
    print("Полный анализ кода:")
    analyzer = LexerAnalyzer()
    tokens = analyzer.analyze(test_code)
    analyzer.print_tokens()
    
    # Статистика
    token_types = {}
    for token in tokens:
        token_type = token['type']
        token_types[token_type] = token_types.get(token_type, 0) + 1
    
    print("\nСТАТИСТИКА ПО ТИПАМ ТОКЕНОВ:")
    for token_type, count in sorted(token_types.items()):
        print(f"  {token_type}: {count}")

class LexerTester:
    def __init__(self):
        self.test_cases = [
            {
                'name': 'Простое присваивание',
                'code': 'x = 42;',
                'expected_tokens': ['ID', 'ASSIGN', 'NUMBER', 'SEMI']
            },
            {
                'name': 'Арифметические операции',
                'code': 'result = (a + b) * c;',
                'expected_tokens': ['ID', 'ASSIGN', 'LPAREN', 'ID', 'PLUS', 'ID', 'RPAREN', 'MUL', 'ID', 'SEMI']
            }
        ]
    
    def run_tests(self):
        analyzer = LexerAnalyzer()
        
        print("\n" + "="*50)
        print("ТЕСТИРОВАНИЕ ЛЕКСЕРА")
        print("="*50)
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\nТест {i}: {test_case['name']}")
            print(f"Код: {test_case['code']}")
            
            tokens = analyzer.analyze(test_case['code'])
            actual_types = [token['type'] for token in tokens]
            
            if actual_types == test_case['expected_tokens']:
                print("✅ ТЕСТ ПРОЙДЕН")
            else:
                print("❌ ТЕСТ НЕ ПРОЙДЕН")
                print(f"Ожидалось: {test_case['expected_tokens']}")
                print(f"Получено:  {actual_types}")

if __name__ == '__main__':
    try:
        main()
        tester = LexerTester()
        tester.run_tests()
    except Exception as e:
        print(f"Ошибка: {e}")
        print("\nУбедитесь, что файлы лексера сгенерированы правильно:")
        print("1. antlr4 -Dlanguage=Python3 Pseudocode.g4")
        print("2. Проверьте наличие файлов: PseudocodeLexer.py, PseudocodeParser.py")
