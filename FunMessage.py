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
        self.message_format = message_format
        self.item_price = item_price
        self.icon_key = icon_key
        self.suffix_info = FunMessage.SUFFIXES[suffix_info.lower()]
        self.image_size = FunMessage.IMAGE_SIZES.index(image_size.lower())
        self.exposure_time = exposure_time
        self.chance = chance


FUN_MESSAGES = [
    FunMessage("That's like {} dynamite >:O", 50, 'dynamite', 'none'),
    FunMessage("That's like {} frozen axe{} :O", 30000, 'frozenaxe', 's'),
    FunMessage("That's like {} bank robber{} o_o", 1900, 'goldbar', 'ies/y'),
    FunMessage("That's like {} wallet{} :P", 350, 'wallet', 's'),
    FunMessage("That's like {} albino pelt{} wew", 750, 'albinopelt', 's'),
    FunMessage("That's like {} legendary bison pelt{} :v", 1050, 'legendarybisonpelt', 's'),
    FunMessage("That's like {} scorched pelt{} :D", 6000, 'scorchedpelt', 's'),
    FunMessage("That's like {} winchester rifle{} x_x", 7200, 'winchester', 's'),
    FunMessage("That's like {} mustang horse{} ;$", 10000, 'mustang', 's'),
    FunMessage("That's like {} cursed volcanic pistol{}", 55000, 'cursedvolcanicpistol', 's'),
    FunMessage("That's like {} axegonne{} :I", 230000, 'axegonne', 's'),
    FunMessage("That's like {} lamborghini{} 0_0", 250000, 'lamborghini', 's', chance=0.5),
    FunMessage("That's like {} paterson{} wuah", 450000, 'patersonnavy', 's'),
    FunMessage("That's like {} spitfire{} $-$", 4250000, 'spitfire', 's'),
    FunMessage("Freddy is watching you D:", 0, 'freddy', 'none', exposure_time=0.5, chance=0.75),
    FunMessage("???", 0, 'mjolnir', 'none', exposure_time=0.25, chance=0.1),
    FunMessage("???", 0, 'heavyguitar', 'none', exposure_time=0.25, chance=0.1),
    FunMessage("???", 0, 'm16', 'none', exposure_time=0.25, chance=0.1),
    FunMessage("???", 0, 'headsman', 'none', exposure_time=0.25, chance=0.1),
    FunMessage("???", 0, 'sled', 'none', exposure_time=0.25, chance=0.1),
]

# suffix_info
# 0 - no change of suffix
# 1 - add an `s` depending on the number
# 2 - add an `y` or `ies` depending on the number
