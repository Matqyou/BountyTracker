from time import sleep, time, perf_counter
from Display import Display, ItemDisplay
from Launcher import Launcher, Logger
from SaveTypes import SaveTypes
import multiprocessing
import numpy as np
import subprocess
import random
import shutil
import sys
import os
import re

LAUNCHER: Launcher = Launcher()
LOGGER: Logger = LAUNCHER.logger

try:
    from PIL import ImageOps, Image, ImageEnhance, ImageFilter, ImageMath
    from DiscordPresence import DiscordPresence
    from WindowsRender import WindowsRender
    import pytesseract
    import pyautogui
    import requests
    import cv2
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
    LOGGER.log('TESSERACT', f'Install {setup_name} with the default install location')
    exit()


def format_time_elapsed(seconds: float) -> str:
    combine_parts = [f'{int(seconds % 60)}s']
    if seconds >= 60:
        combine_parts.insert(0, f'{int(seconds // 60) % 60}min')
    if seconds >= 3600:
        combine_parts.insert(0, f'{int(seconds // 3600) % 24}hrs')
    if seconds >= 84000:
        combine_parts.insert(0, f'{int(seconds // 84000)}days')
    return ' '.join(combine_parts)


def format_time(seconds: float) -> str:
    seconds = int(seconds)
    return f'{seconds // 3600:>02}:{(seconds // 60) % 60:>02}:{seconds % 60:>02}'


def ShowCaptureRectangle(rectangle: tuple) -> None:
    windows_render: WindowsRender = WindowsRender()
    try:
        while True:
            windows_render.draw_rectangle(rectangle)
    except KeyboardInterrupt:
        pass


class BountyTracker:
    APPLICATION_ID: str = str(1185231216211918900)
    HISTORY_FILE = 'BountyHistory'
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
        ItemDisplay("That's like {} scorched pelt{} :D", 4000, 'scorchedpelt', 's/'),
        ItemDisplay("That's like {} winchester rifle{} x_x", 7200, 'winchester', 's/'),
        ItemDisplay("That's like {} mustang horse{} ;$", 10000, 'mustang', 's/'),
        ItemDisplay("That's like {} frozen axe{} :O", 30000, 'frozenaxe', 's/'),
        ItemDisplay("That's like {} cursed volcanic pistol{}", 55000, 'cursedvolcanicpistol', 's/'),
        ItemDisplay("That's like {} kukri{}", 90000, 'kukri', 's/'),
        ItemDisplay("That's like {} axegonne{} :I", 230000, 'axegonne', 's/'),
        ItemDisplay("That's like {} lamborghini{} 0_0", 250000, 'lamborghini', 's/', chance=0.5),
        ItemDisplay("That's like {} paterson{} wuah", 475000, 'patersonnavy', 's/'),
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
        self.history: list[tuple] = []
        self.detected_queue: list[int] = []
        self.display: Display = None  # type: ignore
        self.bounty: int = None  # type: ignore
        self.last_bounty: int = None  # type: ignore
        self.bounty_update_timestamp: float = None  # type: ignore
        self.raw_screenshot: Image = None  # type: ignore
        self.screenshot: Image = None  # type: ignore

        self.capture_rectangle: bool = None  # type: ignore
        self.capture_x: int = None  # type: ignore
        self.capture_y: int = None  # type: ignore
        self.capture_w: int = None  # type: ignore
        self.capture_h: int = None  # type: ignore
        self.show_capture_rectangle: bool = None  # type: ignore
        self.log_to_files: bool = None  # type: ignore
        self.show_discord_activity: bool = None  # type: ignore
        self.capture_refresh_delay: float = 1.5  # 1.5

    def pick_new_fun_message(self) -> None:
        while not (filtered_selection := [fun_message for fun_message in self.fun_messages]):
            self.fun_messages[:] = [msg for msg in BountyTracker.FUN_MESSAGES if random.random() < msg.chance]
        self.display = random.choice(filtered_selection)
        self.fun_messages.remove(self.display)
        self.message_update_timestamp = time()

    def initialize(self, log_information: bool = False) -> None:
        self.load_configuration(log_information)
        self.load_history(log_information)

        if log_information:
            self.logger.log('HISTORY', f'Current hourly bounty rate ${int(self.bounty_hourly(3600)):,}')

        if self.show_capture_rectangle:
            multiprocessing.Process(target=ShowCaptureRectangle, args=(self.capture_rectangle,)).start()

        if self.show_discord_activity:
            self.set_configuration('show_discord_activity', self.discord_presence.connect(), log_information)

    # def bounty_gained_in_past_hour(self):
    #     past_hour = time() - 3600
    #     amount = 0
    #     last_record = None
    #     for record in self.history:
    #         bounty_timestamp, bounty = record
    #         if last_record is not None:
    #             l_bounty_timestamp, l_bounty = last_record
    #             bounty_difference = l_bounty - bounty
    #             if l_bounty_timestamp < past_hour:
    #                 break
    #             amount += bounty_difference
    #         last_record = record
    #     return amount

    def bounty_hourly(self, check_how_long_ago: float):
        right_now = time()
        past_hour = right_now - check_how_long_ago
        amount = 0
        time_spent = 0
        last_record = None
        for record in self.history:
            bounty_timestamp, bounty = record
            if last_record is not None:
                l_bounty_timestamp, l_bounty = last_record
                if l_bounty_timestamp < past_hour:
                    break
                bounty_difference = l_bounty - bounty
                amount += bounty_difference
                time_spent = right_now - l_bounty_timestamp
            last_record = record
        if time_spent > 0.0:
            return amount / time_spent * 3600
        return 0.0

    def init_history(self) -> None:
        self.last_bounty = self.bounty = 0
        self.bounty_update_timestamp = int(time())
        self.history = [(self.bounty_update_timestamp, self.bounty)]
        with open(BountyTracker.HISTORY_FILE, 'w') as tracking_file:
            tracking_file.write(f'{self.bounty_update_timestamp}, {self.bounty}')

    def load_history(self, log_information: bool) -> None:
        if not os.path.exists(BountyTracker.HISTORY_FILE):
            self.init_history()
        else:
            self.history = SaveTypes.load_records(BountyTracker.HISTORY_FILE, (float, int))

        if log_information:
            if not len(self.history):
                self.init_history()
            else:
                self.bounty_update_timestamp, self.bounty = self.history[0]
                self.last_bounty = self.bounty
            num_records = len(self.history)
            time_elapsed = format_time(time() - self.bounty_update_timestamp)
            self.logger.log('HISTORY', f'Loaded {num_records} record{("s", "")[num_records == 1]}')
            self.logger.log('HISTORY', f'Loaded bounty ${self.bounty:,}')
            self.logger.log('HISTORY', f'It\'s been {time_elapsed} since last bounty update')

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
        LAUNCHER.logger.set_log_to_file(self.log_to_files)

    def set_configuration(self, keyword: str, value, log_information: bool) -> None:
        if hasattr(self, keyword) and getattr(self, keyword) != value:
            setattr(self, keyword, value)
            if log_information:
                self.logger.log('CONFIGURE', f'{keyword} = {value}')

    # def load_bounty(self, log_information: bool) -> None:  # CHANGE IT TO WORK WITH HISTORY
    #     if not os.path.exists(BountyTracker.SAVE_FILE):
    #         self.last_bounty = self.bounty = 0
    #         self.bounty_update_timestamp = int(time())
    #         save_values = {
    #             'bounty': self.bounty,
    #             'bounty_timestamp': self.bounty_update_timestamp
    #         }
    #         SaveTypes.save_to_file(BountyTracker.SAVE_FILE, save_values)
    #     else:
    #         load_types = {
    #             'bounty': int,
    #             'bounty_timestamp': float
    #         }
    #         load_values = SaveTypes.load_file(BountyTracker.SAVE_FILE, load_types)
    #         self.last_bounty = self.bounty = load_values['bounty']
    #         self.bounty_update_timestamp = load_values['bounty_timestamp']
    #
    #     if log_information:
    #         time_elapsed = format_time(time() - self.bounty_update_timestamp)
    #         self.logger.log('LOADBOUNTY', f'Loaded bounty ${self.bounty:,}')
    #         self.logger.log('LOADBOUNTY', f'It\'s been {time_elapsed} since last bounty update')

    def update_bounty(self, bounty: int):
        self.bounty = bounty
        self.bounty_update_timestamp = time()
        SaveTypes.append_record(BountyTracker.HISTORY_FILE, f'{self.bounty_update_timestamp}, {self.bounty}')
        self.history.insert(0, (self.bounty_update_timestamp, self.bounty))

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
        image_text = f'Dead bounty: ${round(self.bounty * 0.4):,} ' \
                     f'last updated {format_time(time() - self.bounty_update_timestamp)} ago. ' \
                     f'Hourly bounty rate ${int(self.bounty_hourly(3600)):,}'

        image_kwargs = (
            {'small_image': self.display.icon_key, 'small_text': image_text},
            {'large_image': self.display.icon_key, 'large_text': image_text}
        )[self.display.image_size]

        self.discord_presence.update(state=state_text,
                                     details=details_text,
                                     start=LAUNCHER.startup_timestamp_int,
                                     **image_kwargs)

    # def process_screenshot(self) -> None:
    #     self.raw_screenshot = pyautogui.screenshot(region=self.capture_rectangle)
    #     grayscale_image = ImageOps.grayscale(self.raw_screenshot)
    #     scaled_image = grayscale_image.resize((self.raw_screenshot.width * 6, self.raw_screenshot.height * 6), 5)
    #     contrast_image = ImageEnhance.Contrast(scaled_image).enhance(1.2)
    #
    #     threshold = 225
    #     binary_mask = contrast_image.point(lambda p: p > threshold and 255)
    #     alpha_channel = Image.new("L", contrast_image.size, 255)
    #     alpha_channel.paste(binary_mask, (0, 0))
    #     threshold_image = contrast_image.convert("RGBA")
    #     threshold_image.putalpha(alpha_channel)
    #     black_background = Image.new("RGBA", threshold_image.size, (0, 0, 0, 255))
    #     self.screenshot = Image.alpha_composite(black_background, threshold_image)

    def process_screenshot(self) -> None:
        self.raw_screenshot = pyautogui.screenshot(region=self.capture_rectangle)

        screenshot_copy = self.raw_screenshot.copy()
        upscaled = screenshot_copy.resize((int(screenshot_copy.width * 3),
                                           int(screenshot_copy.height * 3)),
                                          Image.LANCZOS)
        cv_screenshot = np.array(upscaled)
        hsv_image = cv2.cvtColor(cv_screenshot, cv2.COLOR_RGB2HSV)
        white_mask = cv2.inRange(hsv_image, (0, 0, 180), (180, 10, 255))
        filtered_screenshot = cv2.bitwise_and(hsv_image, hsv_image, mask=white_mask)
        rgb_image = cv2.cvtColor(filtered_screenshot, cv2.COLOR_HSV2RGB)

        self.screenshot = Image.fromarray(rgb_image)

    def process_detected_text(self) -> None:
        detected_text = pytesseract.image_to_string(self.screenshot).strip()
        if detected_text:
            dollar_at = detected_text.find('$')
            bounty_at = detected_text.find('Bounty')
            if -1 < dollar_at < bounty_at and BountyTracker.BOUNTY_REGEX.match(detected_text):  # $d Bounty
                bounty_str = detected_text[dollar_at + 1:bounty_at - 1]
                detected_bounty = int(bounty_str)
                if not self.detected_queue or detected_bounty != self.detected_queue[0]:
                    self.detected_queue.append(detected_bounty)
                    num_detected = len(self.detected_queue)
                    if len(self.detected_queue) > 10:
                        self.detected_queue.pop(0)
                        num_detected -= 1
                    average_detected = sum(self.detected_queue) / num_detected
                    sorted_probable = sorted(self.detected_queue, key=lambda x: abs(x - average_detected - 300))
                    most_probable = sorted_probable[0]
                    if self.last_bounty != most_probable:
                        if self.last_bounty is not None:
                            raw_difference = most_probable - self.last_bounty
                            bounty_difference = abs(raw_difference)
                            sign = ('-', '+')[raw_difference >= 0]
                        else:
                            bounty_difference = most_probable
                            sign = '+'
                        if self.bounty_update_timestamp is not None:
                            time_elapsed = format_time_elapsed(time() - self.bounty_update_timestamp)
                        else:
                            time_elapsed = '???'
                        self.logger.log('MAIN', f'Updated bounty ${most_probable:,} / '
                                                f'{sign}${bounty_difference:,} over {time_elapsed}')
                        self.last_bounty = most_probable
                        self.update_bounty(most_probable)
                        self.update_presence()

                        capture_sample = Image.new('RGB', (max(self.raw_screenshot.width, self.screenshot.width),
                                                           self.raw_screenshot.height + self.screenshot.height),
                                                   color=(0, 0, 0))
                        capture_sample.paste(self.raw_screenshot, (0, 0))
                        capture_sample.paste(self.screenshot, (0, self.raw_screenshot.height))
                        capture_sample.save(f'captures/{self.bounty_update_timestamp}.png')

    def run(self) -> None:
        cycle_start = perf_counter()
        while True:
            if self.display is None or \
                    time() - self.message_update_timestamp >= \
                    self.display.exposure_time * BountyTracker.MESSAGE_UPDATE_DELAY:
                self.pick_new_fun_message()
                self.update_presence()

            self.process_screenshot()
            self.process_detected_text()

            if (elapsed := (perf_counter() - cycle_start)) < self.capture_refresh_delay:
                sleep(self.capture_refresh_delay - elapsed)
                cycle_start = perf_counter()


def main() -> None:
    bounty_tracker = BountyTracker(LOGGER)
    bounty_tracker.initialize(log_information=True)
    bounty_tracker.run()


if __name__ == '__main__':
    LAUNCHER.launch(main)
