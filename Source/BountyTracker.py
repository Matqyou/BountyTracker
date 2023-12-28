from time import sleep, time, perf_counter
from Display import Display, ItemDisplay
from Launcher import Launcher, Logger
from SaveTypes import SaveTypes
import multiprocessing
import subprocess
import random
import shutil
import sys
import os
import re

LAUNCHER: Launcher = Launcher()
LOGGER: Logger = LAUNCHER.logger

try:
    from DiscordPresence import DiscordPresence
    from WindowsRender import WindowsRender
    import pytesseract
    import pyautogui
    import requests
except ModuleNotFoundError:
    LOGGER.log('LIBRARIES', 'Installing libraries..')
    subprocess.call(['pip', 'install', '-r', '..\\requirements.txt'])
    LOGGER.log('LIBRARIES', 'Installed successfully!')
    subprocess.call([sys.executable] + sys.argv)
    exit()

possible_tesseract_path = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
if os.path.exists(possible_tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = possible_tesseract_path
elif (tesseract_path := shutil.which('tesseract')) is None:
    setup_name = 'tesseract-ocr-setup-3.02.02.exe'
    setup_file = f'..\\{setup_name}'
    if not os.path.exists(setup_file):
        LOGGER.log('TESSERACT', f'Downloading {setup_name}')

        file_url = 'https://downloads.sourceforge.net/project/tesseract-ocr-alt/tesseract-ocr-setup-3.02.02.exe?ts=gAAAAABlh0rv-caw3tHhQdJ2gIURc8E-fr0Wl-k6t-XMqpkjwNWMdXrhmYg5WtV7JvFwlW9jfgSIIoe_6SxZumFImStJkzGcpw%3D%3D&amp;use_mirror=kumisystems&amp;r=https%3A%2F%2Fwww.google.com%2F'
        response = requests.get(file_url)
        if response.status_code == 200:
            with open(setup_file, 'wb') as file:
                file.write(response.content)
            LOGGER.log('TESSERACT', 'Download complete!')
        else:
            LOGGER.log('TESSERACT', 'Could not download tesseract setup, try again or use link from github')
    LOGGER.log()
    LOGGER.log('TESSERACT', f'Install {setup_name} with the default install location')
    exit()

WINDOWS_RENDER: WindowsRender = None  # type: ignore


def FormatTime(seconds: float) -> str:
    seconds = int(seconds)
    return f'{seconds // 3600:>02}:{(seconds // 60) % 60:>02}:{seconds % 60:>02}'


def ShowCaptureRectangle(rectangle: tuple) -> None:
    try:
        while True:
            WINDOWS_RENDER.draw_rectangle(rectangle)
    except KeyboardInterrupt:
        pass


class BountyTracker:
    APPLICATION_ID: str = str(1185231216211918900)
    SAVE_FILE = 'LastBounty'
    CONFIGURATION_FILE = '../Configure.txt'
    MESSAGE_UPDATE_DELAY: float = 45
    BOUNTY_REGEX = re.compile(r'\$\d+\sBounty')
    FUN_MESSAGES = [
        ItemDisplay("That's like {} cact{} =_=", 3, 'cactus', 'i/us'),
        ItemDisplay("That's like {} chair{} :>", 40, 'chair', 's/'),
        ItemDisplay("That's like {} dynamite >:O", 50, 'dynamite', None),
        ItemDisplay("That's like {} bear trap{} E-E", 60, 'beartrap', 's/'),
        ItemDisplay("That's like {} campfire{} :L", 200, 'campfire', 's/'),
        ItemDisplay("That's like {} lasso{} ;]", 200, 'lasso', 'es/'),
        ItemDisplay("That's like {} wallet{} :P", 350, 'wallet', 's/'),
        ItemDisplay("That's like {} albino pelt{} wew", 750, 'albinopelt', 's/'),
        ItemDisplay("That's like {} shovel{} ._.", 800, 'shovel', 's/'),
        ItemDisplay("That's like {} legendary bison pelt{} :v", 1050, 'legendarybisonpelt', 's/'),
        ItemDisplay("That's like {} bank robber{} o_o", 1900, 'goldbar', 'ies/y'),
        ItemDisplay("That's like {} thunder log{} xO", 2000, 'thunderstrucklog', 's/'),
        ItemDisplay("That's like {} thunder cact{} xO", 3000, 'thunderstruckcactus', 'i/us'),
        ItemDisplay("That's like {} scorched pelt{} :D", 6000, 'scorchedpelt', 's/'),
        ItemDisplay("That's like {} winchester rifle{} x_x", 7200, 'winchester', 's/'),
        ItemDisplay("That's like {} mustang horse{} ;$", 10000, 'mustang', 's/'),
        ItemDisplay("That's like {} frozen axe{} :O", 30000, 'frozenaxe', 's/'),
        ItemDisplay("That's like {} cursed volcanic pistol{}", 55000, 'cursedvolcanicpistol', 's/'),
        ItemDisplay("That's like {} kukri{}", 90000, 'kukri', 's/'),
        ItemDisplay("That's like {} axegonne{} :I", 230000, 'axegonne', 's/'),
        ItemDisplay("That's like {} lamborghini{} 0_0", 250000, 'lamborghini', 's/', chance=0.5),
        ItemDisplay("That's like {} paterson{} wuah", 450000, 'patersonnavy', 's/'),
        ItemDisplay("That's like {} spitfire{} $-$", 4250000, 'spitfire', 's/'),
        Display("What is he looking at..", 'snowman', exposure_time=0.5, chance=0.75),
        Display("Mmmm tasty..", 'candycane', exposure_time=0.5, chance=0.75),
        Display("Thanks, Santa! :}", 'rednoserifle', exposure_time=0.5, chance=0.75),
        Display("That was a nice event..", 'occultblade', exposure_time=0.5, chance=0.75),
        Display("Lightning! Pew pew..", 'lightningmodel3', exposure_time=0.5, chance=0.75),
        Display("Freddy is watching you D:", 'freddy', exposure_time=0.5, chance=0.75),
        Display("???", 'mjolnir', exposure_time=0.25, chance=0.2),
        Display("???", 'heavyguitar', exposure_time=0.25, chance=0.2),
        Display("???", 'm16', exposure_time=0.25, chance=0.2),
        Display("???", 'headsman', exposure_time=0.25, chance=0.2),
        Display("???", 'sled', exposure_time=0.25, chance=0.2),
    ]

    def __init__(self, logger: Logger):
        self.logger: Logger = logger

        self.discord_presence: DiscordPresence = DiscordPresence(logger, BountyTracker.APPLICATION_ID)
        self.message_update_timestamp: float = time()
        self.fun_messages: list[Display] = []
        self.display: Display = None  # type: ignore
        self.bounty: int = None  # type: ignore
        self.last_bounty: int = None  # type: ignore
        self.bounty_update_timestamp: float = None  # type: ignore

        self.capture_rectangle: bool = None  # type: ignore
        self.capture_x: int = None  # type: ignore
        self.capture_y: int = None  # type: ignore
        self.capture_w: int = None  # type: ignore
        self.capture_h: int = None  # type: ignore
        self.show_capture_rectangle: bool = None  # type: ignore
        self.log_to_files: bool = None  # type: ignore
        self.show_discord_activity: bool = None  # type: ignore
        self.capture_refresh_rate: float = None  # type: ignore

    def pick_new_fun_message(self) -> None:
        while not (filtered_selection := [fun_message for fun_message in self.fun_messages]):
            self.fun_messages[:] = [msg for msg in BountyTracker.FUN_MESSAGES if random.random() < msg.chance]
        self.display = random.choice(filtered_selection)
        self.fun_messages.remove(self.display)
        self.message_update_timestamp = time()

    def initialize(self, log_information: bool = False) -> None:
        self.load_configuration(log_information)
        self.load_bounty(log_information)

        if self.show_discord_activity:
            self.set_configuration('show_discord_activity', self.discord_presence.connect(), log_information)

        if self.show_capture_rectangle:
            global WINDOWS_RENDER
            WINDOWS_RENDER = WindowsRender()
            multiprocessing.Process(target=ShowCaptureRectangle, args=(self.capture_rectangle,)).start()

    def load_configuration(self, log_information: bool) -> None:
        load_types = {
            'capture_rectangle': (int, int, int, int),
            'show_capture_rectangle': bool,
            'log_to_files': bool,
            'show_discord_activity': bool,
            'capture_refresh_rate': float
        }
        load_values = SaveTypes.load_file(self.CONFIGURATION_FILE, load_types)
        for keyword, value in load_values.items():
            self.set_configuration(keyword, value, log_information)
        if 'capture_rectangle' in load_values:
            self.capture_x, self.capture_y, self.capture_w, self.capture_h = self.capture_rectangle

    def set_configuration(self, keyword: str, value, log_information: bool) -> None:
        if hasattr(self, keyword) and getattr(self, keyword) != value:
            setattr(self, keyword, value)
            if log_information:
                self.logger.log('CONFIGURE', f'{keyword} = {value}')

    def load_bounty(self, log_information: bool) -> None:
        if not os.path.exists(BountyTracker.SAVE_FILE):
            self.last_bounty = self.bounty = 0
            self.bounty_update_timestamp = int(time())
            save_values = {
                'bounty': self.bounty,
                'bounty_timestamp': self.bounty_update_timestamp
            }
            SaveTypes.save_to_file(BountyTracker.SAVE_FILE, save_values)
        else:
            load_types = {
                'bounty': int,
                'bounty_timestamp': float
            }
            load_values = SaveTypes.load_file(BountyTracker.SAVE_FILE, load_types)
            self.last_bounty = self.bounty = load_values['bounty']
            self.bounty_update_timestamp = load_values['bounty_timestamp']

        if log_information:
            LOGGER.log('LOADBOUNTY', f'Loaded bounty ${self.bounty:,}')
            LOGGER.log('LOADBOUNTY', f'It\'s been {FormatTime(time() - self.bounty_update_timestamp)} since last bounty update')

    def update_bounty(self, bounty: int):
        self.bounty = bounty
        self.bounty_update_timestamp = time()
        save_values = {
            'bounty': self.bounty,
            'bounty_timestamp': self.bounty_update_timestamp
        }
        SaveTypes.save_to_file(BountyTracker.SAVE_FILE, save_values)

    def update_presence(self) -> None:
        if not self.show_discord_activity:
            return

        state_text = None
        if self.display.display_type == 0:
            state_text = self.display.message_format
        elif self.display.display_type == 1:
            item_display: ItemDisplay = self.display  # type: ignore
            state_text = item_display.generate_text(self.bounty)

        details_text = f'Current bounty: ${self.bounty:,}'
        image_text = f'Dead bounty: ${round(self.bounty * 0.4):,} and it\'s been {FormatTime(time() - self.bounty_update_timestamp)} since last bounty update'

        image_kwargs = (
            {'small_image': self.display.icon_key, 'small_text': image_text},
            {'large_image': self.display.icon_key, 'large_text': image_text}
        )[self.display.image_size]

        self.discord_presence.update(state=state_text,
                                     details=details_text,
                                     start=LAUNCHER.startup_timestamp_int,
                                     **image_kwargs)

    def run(self) -> None:
        cycle_start = perf_counter()
        while True:
            if self.display is None or time() - self.message_update_timestamp >= self.display.exposure_time * BountyTracker.MESSAGE_UPDATE_DELAY:
                self.pick_new_fun_message()
                self.update_presence()
            screenshot = pyautogui.screenshot(region=self.capture_rectangle).resize((self.capture_w * 3, self.capture_h * 3))
            detected_text = pytesseract.image_to_string(screenshot).strip()

            if detected_text:
                dollar_at = detected_text.find('$')
                bounty_at = detected_text.find('Bounty')
                if -1 < dollar_at < bounty_at and BountyTracker.BOUNTY_REGEX.match(detected_text):  # $d Bounty
                    bounty_str = detected_text[dollar_at + 1:bounty_at - 1]
                    detected_bounty = int(bounty_str)
                    if self.last_bounty != detected_bounty:
                        self.last_bounty = detected_bounty
                        LOGGER.log('MAIN', f'New bounty: ${detected_bounty:,} | `{detected_text}`')
                        self.update_bounty(detected_bounty)
                        self.update_presence()

            if (elapsed := (perf_counter() - cycle_start)) < self.capture_refresh_rate:
                sleep(self.capture_refresh_rate - elapsed)
                cycle_start = perf_counter()


def main() -> None:
    bounty_tracker = BountyTracker(LOGGER)
    bounty_tracker.initialize(log_information=True)
    bounty_tracker.run()


if __name__ == '__main__':
    LAUNCHER.launch(main)
