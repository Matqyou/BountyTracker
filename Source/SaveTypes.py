import os


def cast_to(value_str: str, cast_type):
    if cast_type == bool:
        if value_str.lower() == 'true':
            return True
        elif value_str.lower() == 'false':
            return False
    else:
        try:
            return cast_type(value_str)
        except:
            pass
    raise ValueError(f'Could not cast from `{value_str}` into {cast_type}')


def parse_tuple(value_str: str, expected_types: tuple) -> tuple:
    split_value_str = [param_str.strip() for param_str in value_str.split(',')]
    if (expected_len := len(expected_types)) > (got_len := len(split_value_str)):
        raise ValueError(f'not enough values to unpack (expected {expected_len}, got {got_len})')
    elif expected_len < got_len:
        raise ValueError(f'too many values to unpack (expected {expected_len})')
    return tuple(cast_to(param_str, expected_type) for param_str, expected_type in zip(split_value_str, expected_types))


class SaveTypes:
    @staticmethod
    def save_to_file(file: str, values: dict) -> None:
        save_text = '\n'.join(f'{keyword} = {value_any}' for keyword, value_any in values.items())
        with open(file, 'w') as save_file:
            save_file.write(save_text)

    @staticmethod
    def load_file(file: str, load_types: dict) -> dict:
        if os.path.exists(file):
            with open(file, 'r') as file:
                content_lines = file.read().splitlines()
                value_lines = [line_ for line in content_lines if (line_ := line.strip()) and not line_.startswith('#')]
            load_types_: dict = load_types.copy()
            unparsed_values: list = [tuple(part.strip() for part in line.split('=', 1)) for line in value_lines]
            result: dict = {}
            for keyword, value_str in unparsed_values:
                if keyword in load_types_:
                    expected_type = load_types_[keyword]
                    parse_function = (cast_to, parse_tuple)[type(expected_type) == tuple]
                    result[keyword] = parse_function(value_str, expected_type)
                    load_types_.pop(keyword)
                else:
                    result[keyword] = value_str
            return result
        return {}
