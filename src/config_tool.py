import argparse
import json
import re
import sys

TOKEN_NAME = re.compile(r'^[_a-zA-Z]+$')
TOKEN_NUMBER = re.compile(r'^[1-9][0-9]*$')

class ConfigError(Exception):
    pass


class Parser:
    def __init__(self):
        self.constants = {}

    def parse_value(self, text):
        text = text.strip()

        if TOKEN_NUMBER.match(text):
            return int(text)

        if text.startswith('@(') and text.endswith(')'):
            name = text[2:-1]
            if name not in self.constants:
                raise ConfigError(f"Неизвестная константа: {name}")
            return self.constants[name]

        if text.startswith('{') and text.endswith('}'):
            inner = text[1:-1].strip()
            if not inner:
                return []
            parts = [p.strip() for p in inner.split('.')]
            return [self.parse_value(p) for p in parts]

        raise ConfigError(f"Некорректное значение: {text}")

    def parse_line(self, line, lineno):
        if not line.endswith(';'):
            raise ConfigError(f"Строка {lineno}: отсутствует ';'")

        line = line[:-1].strip()
        if '<-' not in line:
            raise ConfigError(f"Строка {lineno}: отсутствует '<-'")

        name, value = map(str.strip, line.split('<-', 1))

        if not TOKEN_NAME.match(name):
            raise ConfigError(f"Строка {lineno}: некорректное имя '{name}'")

        if name in self.constants:
            raise ConfigError(f"Строка {lineno}: повторное объявление '{name}'")

        self.constants[name] = self.parse_value(value)

    def parse(self, text):
        for lineno, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            self.parse_line(line, lineno)
        return self.constants


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()

        p = Parser()
        result = p.parse(text)

        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)

    except ConfigError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()