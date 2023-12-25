class FunMessage:
    IMAGE_SIZES = ['small', 'large']
    SUFFIXES = {
        'none': None,
        's': ('s', ''),
        'ies/y': ('ies', 'y')
    }

    def __init__(self, message_format: str,
                 item_price: int,
                 icon_key: str = None,
                 suffix_info: str = 'none',
                 image_size: str = 'small',
                 exposure_time: float = 1.0,
                 chance: float = 1.0):
        self.message_format: str = message_format
        self.item_price: int = item_price
        self.icon_key: str = icon_key
        self.suffix_info: tuple = FunMessage.SUFFIXES[suffix_info.lower()]
        self.image_size: int = FunMessage.IMAGE_SIZES.index(image_size.lower())
        self.exposure_time: float = exposure_time
        self.chance: float = chance

# suffix_info
# 0 - no change of suffix
# 1 - add an `s` depending on the number
# 2 - add an `y` or `ies` depending on the number
