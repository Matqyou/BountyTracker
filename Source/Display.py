IMAGE_SIZES = ['small', 'large']

class Display:
    def __init__(self, message_format: str,
                 icon_key: str = None,
                 image_size: str = 'small',
                 exposure_time: float = 1.0,
                 chance: float = 1.0):
        self.message_format: str = message_format
        self.icon_key: str = icon_key
        self.image_size: int = IMAGE_SIZES.index(image_size.lower())
        self.exposure_time: float = exposure_time
        self.chance: float = chance
        self.display_type = 0


class ItemDisplay(Display):
    def __init__(self, message_format: str,
                 item_price: int,
                 icon_key: str = None,
                 suffix_info: str = None,
                 image_size: str = 'small',
                 exposure_time: float = 1.0,
                 chance: float = 1.0):
        super().__init__(message_format, icon_key, image_size, exposure_time, chance)
        self.item_price: int = item_price
        self.display_type = 1

        if suffix_info is not None:
            suffix_info = tuple(suffix_info.split('/'))
        self.suffix_info: tuple = suffix_info

    def generate_text(self, money: int) -> str:
        if self.item_price > money:
            fraction = money / self.item_price * 100
            percision_places = int(fraction < 10)
            amount = f'{fraction:.{percision_places}f}% of a'
            first_letter_index = self.message_format.find('{}') + 3
            first_letter = self.message_format[first_letter_index:first_letter_index + 1]
            if first_letter.lower() in 'aeiou':
                amount += 'n'
        else:
            amount = money // self.item_price

        suffix = None
        if (suffix_info := self.suffix_info) is not None:
            index = type(amount) == str or amount == 1
            suffix = suffix_info[index]

        return self.message_format.format(amount, suffix)
