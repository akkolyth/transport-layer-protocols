"""
python-template
"""

from pathlib import Path
from typing import Union

HEADER = '"""\npython-template\n"""\n\n'
TARGET_DIRECTORY = '.'


def header_py_files(directory: Union[str, Path]) -> None:
    directory = Path(directory)

    for file_path in directory.rglob('*.py'):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        if not (content.startswith(HEADER) or content.startswith('#') or content.startswith('"""')):
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(HEADER + content)


if __name__ == '__main__':
    header_py_files(TARGET_DIRECTORY)
