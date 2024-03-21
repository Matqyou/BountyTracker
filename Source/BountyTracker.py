from Display import Display, ItemDisplay, RateDisplay
from time import sleep, time, perf_counter
from Launcher import Launcher, Logger
from SaveTypes import SaveTypes
from typing import Any, Optional
import multiprocessing
import subprocess
import threading
import random
import shutil
# import atexit
import sys
import os
import re

LAUNCHER: Launcher = Launcher()
LOGGER: Logger = LAUNCHER.logger

try:
    from PIL import ImageOps, Image, ImageEnhance, ImageFilter, ImageMath, ImageGrab
    from CheapWindowsRendering import CheapWindowsRendering
    from ApplicationCapture import ApplicationCapture
    from DiscordPresence import DiscordPresence
    import pygetwindow
    import pytesseract
    import numpy as np
    import pyautogui
    import win32gui
    import win32con
    import win32api
    import requests
    import win32ui
    import pygame
    import cv2
except ModuleNotFoundError:
    LOGGER.log('LIBRARIES', 'Installing libraries..')
    subprocess.call(['pip', 'install', '-r', '..\\requirements.txt'])
    LOGGER.log('LIBRARIES', 'Installed successfully!')
    subprocess.call([sys.executable] + sys.argv)
    exit()

pytesseract.pytesseract.tesseract_cmd = os.path.abspath(os.path.join(os.getcwd(), './dependencies/tesseract/tesseract.exe'))
os.environ["TESSDATA_PREFIX"] = "./dependencies/tesseract/"


def format_time_elapsed(seconds: float) -> str:
    combine_parts: list[str] = [f'{int(seconds % 60)}s']
    if seconds >= 60:
        combine_parts.insert(0, f'{int(seconds // 60) % 60}min')
    if seconds >= 3600:
        combine_parts.insert(0, f'{int(seconds // 3600) % 24}hrs')
    if seconds >= 84000:
        combine_parts.insert(0, f'{int(seconds // 84000)}days')
    return ' '.join(combine_parts)


def format_time(seconds: float) -> str:
    seconds: int = int(seconds)
    return f'{seconds // 3600:>02}:{(seconds // 60) % 60:>02}:{seconds % 60:>02}'


def ShowCaptureRectangle(rectangle: tuple) -> None:  # TODO: make this better
    windows_render: CheapWindowsRendering = CheapWindowsRendering()
    try:
        while True:
            windows_render.draw_rectangle(rectangle)
    except KeyboardInterrupt:
        pass


class BountyTracker:
    APPLICATION_ID: str = str(1185231216211918900)
    HISTORY_FILE: str = '../BountyHistory'
    CAPTURES_DIRECTORY: str = '../Captures/'
    CONFIGURATION_FILE: str = '../Configure.txt'
    MESSAGE_UPDATE_DELAY: float = 45
    SCREENIE_PRESCALE: float = 4
    SCREENIE_POSTSCALE: float = 0.8
    SCREENIE_FINALSCALE: float = SCREENIE_PRESCALE * SCREENIE_POSTSCALE
    BOUNTY_REGEX = re.compile(r'\$\d+\sBounty')
    FUN_MESSAGES: list[Display] = [
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
        ItemDisplay("That's like {} scorched pelt{} :D", 3500, 'scorchedpelt', 's/'),
        ItemDisplay("That's like {} winchester rifle{} x_x", 7200, 'winchester', 's/'),
        ItemDisplay("That's like {} mustang horse{} ;$", 10000, 'mustang', 's/'),
        ItemDisplay("That's like {} frozen axe{} :O", 30000, 'frozenaxe', 's/'),
        ItemDisplay("That's like {} cursed volcanic pistol{}", 55000, 'cursedvolcanicpistol', 's/'),
        ItemDisplay("That's like {} kukri{}", 90000, 'kukri', 's/'),
        ItemDisplay("That's like {} axegonne{} :I", 230000, 'axegonne', 's/'),
        ItemDisplay("That's like {} lamborghini{} 0_0", 250000, 'lamborghini', 's/', chance=0.5),
        ItemDisplay("That's like {} paterson{} wuah", 475000, 'patersonnavy', 's/'),
        ItemDisplay("That's like {} spitfire{} $-$", 4250000, 'spitfire', 's/'),
        RateDisplay("Just {} of deer hunting ;L", 30000, 'deer', exposure_time=0.25, chance=0.2),
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
        Display("Uhhh", 'waa', exposure_time=0.25, chance=0.2),
    ]
    configuration_types: dict[str, Any] = {
        'capture_rectangle': (int, int, int, int),
        'show_capture_rectangle': bool,
        'capture_refresh_delay': float,
        'log_to_files': bool,
        'show_discord_activity': bool,
        'capture_preview': bool,
        'save_captures': bool,
        'ram_disk_letter': str
    }

    def __init__(self, logger: Logger):
        self.logger: Logger = logger

        self.discord_presence: DiscordPresence = DiscordPresence(logger, BountyTracker.APPLICATION_ID)
        self.message_update_timestamp: float = time()
        self.fun_messages: list[Display] = []
        self.history: list[tuple[float, int]] = []
        self.detected_queue: list[int] = []
        self.roblox_capture: ApplicationCapture = None  # type: ignore
        self.last_roblox_capture_search_timestamp: float = None  # type: ignore
        self.display: Display = None  # type: ignore
        self.bounty: int = None  # type: ignore
        self.last_bounty: int = None  # type: ignore
        self.bounty_update_timestamp: float = None  # type: ignore
        self.raw_screenshot: Image = None  # type: ignore
        self.screenshot: Image = None  # type: ignore
        self.capture_window: pygame.Surface = None  # type: ignore

        self.capture_rectangle: tuple = None  # type: ignore
        self.capture_size: tuple = None  # type: ignore
        self.capture_x: int = None  # type: ignore
        self.capture_y: int = None  # type: ignore
        self.capture_w: int = None  # type: ignore
        self.capture_h: int = None  # type: ignore
        self.show_capture_rectangle: bool = None  # type: ignore
        self.log_to_files: bool = None  # type: ignore
        self.show_discord_activity: bool = None  # type: ignore
        self.capture_preview: bool = None  # type: ignore
        self.capture_refresh_delay: float = None  # type: ignore
        self.save_captures: bool = None  # type: ignore
        self.ram_disk_letter: str = None  # type: ignore
        self.ram_disk_directory: str = None  # type: ignore

    def find_roblox_window(self) -> bool:
        self.last_roblox_capture_search_timestamp = perf_counter()

        if (roblox_handle := win32gui.FindWindow(None, 'Roblox')) != 0:
            self.roblox_capture = ApplicationCapture(roblox_handle, self.capture_rectangle)

            self.logger.log('CAPTURE', f'Registered Roblox with the handle {roblox_handle}')
            return True
        return False

    def pick_new_fun_message(self) -> None:
        while not (filtered_selection := [fun_message for fun_message in self.fun_messages]):
            self.fun_messages[:] = [msg for msg in BountyTracker.FUN_MESSAGES if random.random() < msg.chance]
        self.display = random.choice(filtered_selection)
        self.fun_messages.remove(self.display)
        self.message_update_timestamp = time()

    @staticmethod
    def begin_capture_window(self) -> None:
        pygame.init()
        icon: pygame.Surface = pygame.image.load('Icon.png')
        window_width: float = self.capture_w * BountyTracker.SCREENIE_FINALSCALE
        window_height: float = self.capture_h + self.capture_h * BountyTracker.SCREENIE_FINALSCALE
        self.capture_window = pygame.display.set_mode((window_width, window_height))

        pygame.display.set_icon(icon)
        pygame.display.set_caption(f'BountyTracker: Capture')
        clock = pygame.time.Clock()
        beginning: float = perf_counter()

        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.logger.log('CAPTURE', 'Capture window has been closed')
                    self.set_configuration('capture_preview', False)
                    return

            if (currently := perf_counter()) - beginning > 0.75:
                beginning = currently
                caption = f'b/hr ${int(self.bounty_hourly(3600)):,}'
                pygame.display.set_caption(caption)
            if self.raw_screenshot:
                screenshot_surface: pygame.Surface = pygame.image.fromstring(self.raw_screenshot.tobytes(),
                                                                             self.raw_screenshot.size, "RGB")
                self.capture_window.blit(screenshot_surface, (0, 0))
            if self.screenshot:
                screenshot_surface: pygame.Surface = pygame.image.fromstring(self.screenshot.tobytes(),
                                                                             self.screenshot.size, "RGB")
                self.capture_window.blit(screenshot_surface, (0, self.capture_h))
            pygame.display.update()

    def initialize(self) -> None:
        self.load_configuration()
        self.load_history()

        self.find_roblox_window()

        if self.show_capture_rectangle:
            multiprocessing.Process(target=ShowCaptureRectangle, args=(self.capture_rectangle,)).start()

        if self.show_discord_activity:
            self.set_configuration('show_discord_activity', self.discord_presence.connect())

        if self.capture_preview:
            thread = threading.Thread(target=self.begin_capture_window, args=(self,))
            thread.start()

        if self.ram_disk_letter:
            self.ram_disk_letter = self.ram_disk_letter[0].upper()
            if not os.path.exists(f'{self.ram_disk_letter}:\\'):
                self.logger.log('RAMDISK', f'No disk with the letter {self.ram_disk_letter} has been found')
                self.set_configuration('ram_disk_letter', None)
            else:
                self.ram_disk_directory = f'{self.ram_disk_letter}:\\BountyTracker\\'

    def bounty_hourly(self, check_how_long_ago: float) -> float:
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
            tracking_file.write(f'{self.bounty_update_timestamp}, {self.bounty}\n')

    def load_history(self) -> None:
        if not os.path.exists(BountyTracker.HISTORY_FILE):
            self.init_history()
        else:
            self.history: list[tuple[float, int]] = SaveTypes.load_records(BountyTracker.HISTORY_FILE, (float, int))

        if not len(self.history):
            self.init_history()
        else:  # If the file is empty for some reason
            self.bounty_update_timestamp, self.bounty = self.history[0]
            self.last_bounty = self.bounty
        num_records = len(self.history)

        self.logger.log('HISTORY', f'Loaded {num_records} record{("s", "")[num_records == 1]}')
        self.logger.log('HISTORY', f'Loaded bounty ${self.bounty:,}')

        num_intro_records: int = 5
        self.logger.log('HISTORY', f'[Last {num_intro_records} bounty updates]')
        intro_records = self.history[num_intro_records::-1] if num_records >= num_intro_records else self.history[::-1]
        last_timestamp: Optional[float] = None
        last_bounty: Optional[int] = None
        for timestamp, bounty in intro_records:
            if last_timestamp is not None:
                timetext = format_time_elapsed(timestamp - last_timestamp)
                bountytext = f'+${bounty - last_bounty:,}'
                self.logger.log('HISTORY', f'Bounty updated to ${bounty:,} / {bountytext} over {timetext}')
            last_timestamp = timestamp
            last_bounty = bounty

        timetext = format_time(time() - self.bounty_update_timestamp)
        self.logger.log('HISTORY', f'It\'s been {timetext} since last bounty update')
        self.logger.log('HISTORY', f'Current hourly bounty rate ${int(self.bounty_hourly(3600)):,}')

    def load_configuration(self) -> None:
        load_values = SaveTypes.load_file(BountyTracker.CONFIGURATION_FILE, BountyTracker.configuration_types)
        for keyword, value in load_values.items():
            self.set_configuration(keyword, value)
        if 'capture_rectangle' in load_values:
            self.capture_x, self.capture_y, self.capture_w, self.capture_h = self.capture_rectangle
        self.logger.set_log_to_file(self.log_to_files)

    def set_configuration(self, keyword: str, value) -> None:
        if hasattr(self, keyword) and getattr(self, keyword) != value:
            setattr(self, keyword, value)
            self.logger.log('CONFIGURE', f'{keyword} = {value}')

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
        elif self.display.display_type == 2:
            rate_display: RateDisplay = self.display  # type: ignore
            state_text = rate_display.generate_text(self.bounty)

        hourly = int(self.bounty_hourly(3600))
        details_text = f'Current bounty: ${self.bounty:,}'
        image_text = f'Dead bounty: ${round(self.bounty * 0.4):,} ' \
                     f'last updated {format_time(time() - self.bounty_update_timestamp)} ago. ' \
                     f'Hourly bounty rate ${hourly:,}'

        image_kwargs = (
            {'small_image': self.display.icon_key, 'small_text': image_text},
            {'large_image': self.display.icon_key, 'large_text': image_text}
        )[self.display.image_size]

        self.discord_presence.update(state=state_text,
                                     details=details_text,
                                     start=LAUNCHER.startup_timestamp_int,
                                     **image_kwargs)

    def process_screenshot(self) -> None:
        capture_pil = self.raw_screenshot.copy()
        upscaled_pil = capture_pil.resize((int(capture_pil.width * BountyTracker.SCREENIE_PRESCALE),
                                           int(capture_pil.height * BountyTracker.SCREENIE_PRESCALE)),
                                          Image.Resampling.LANCZOS)
        upscaled_image = np.array(upscaled_pil)
        hsv_image = cv2.cvtColor(upscaled_image, cv2.COLOR_RGB2HSV)

        white_mask = cv2.inRange(hsv_image, (0, 0, 242), (180, 10, 255))
        processed_image = cv2.bitwise_and(hsv_image, hsv_image, mask=white_mask)
        dilate_kernel = np.ones((2, 2), np.uint8)
        dilated_image = cv2.dilate(processed_image, dilate_kernel, iterations=3)
        rgb_image = cv2.cvtColor(dilated_image, cv2.COLOR_HSV2RGB)

        processed = Image.fromarray(rgb_image)
        self.screenshot = processed.resize((int(processed.width * BountyTracker.SCREENIE_POSTSCALE),
                                            int(processed.height * BountyTracker.SCREENIE_POSTSCALE)),
                                           Image.Resampling.LANCZOS)

    def capture_screenshot(self) -> bool:
        if not self.roblox_capture.is_open():
            self.roblox_capture.window_closed()
            self.roblox_capture = None
            return False

        self.raw_screenshot = self.roblox_capture.capture()
        self.process_screenshot()
        return True

    def process_detected_text(self) -> None:
        if self.ram_disk_letter:
            if not os.path.exists(self.ram_disk_directory):
                os.mkdir(self.ram_disk_directory)
            screenshot_path: str = f'{self.ram_disk_directory}capture.png'
            tesseract_result_path: str = f'{self.ram_disk_directory}result'
            self.screenshot.save(screenshot_path)

            tesseract_kwargs: dict = {
                'input_filename': screenshot_path,
                'output_filename_base': tesseract_result_path,
                'extension': 'txt',
                'lang': None,
                'config': '',
                'nice': 0,
                'timeout': 0,
            }
            pytesseract.pytesseract.run_tesseract(**tesseract_kwargs)

            with open(tesseract_result_path + '.txt', 'rb') as output_file:
                detected_text: str = output_file.read().decode('utf-8')
        else:  # TODO: don't use image_to_string
            detected_text: str = pytesseract.image_to_string(self.screenshot).strip()

        # If we didn't find anything, leave
        if not detected_text:
            return

        # Check if the bounty corresponds to the regular expression `$d Bounty`
        dollar_index: int = detected_text.find('$')
        bounty_index: int = detected_text.find('Bounty')
        if not -1 < dollar_index < bounty_index or not BountyTracker.BOUNTY_REGEX.match(detected_text):
            return

        # If the previous detected bounty is the same, leave
        bounty_string: str = detected_text[dollar_index + 1:bounty_index - 1]
        detected_bounty: int = int(bounty_string)
        if self.detected_queue and detected_bounty == self.detected_queue[0]:
            return

        # If the previous bounty is the most probable current bounty, leave
        self.detected_queue.append(detected_bounty)
        num_detected: int = len(self.detected_queue)
        if len(self.detected_queue) > 10:
            self.detected_queue.pop(0)
            num_detected -= 1
        average_n_past_bounties: float = sum(self.detected_queue) / num_detected
        sorted_probably_bounties = sorted(self.detected_queue, key=lambda x: abs(x - average_n_past_bounties - 300))
        most_probable_bounty = sorted_probably_bounties[0]
        if self.last_bounty == most_probable_bounty:
            return

        # Update the bounty presence and history
        if self.last_bounty is not None:
            raw_difference = most_probable_bounty - self.last_bounty
            bounty_difference = abs(raw_difference)
            sign = ('-', '+')[raw_difference >= 0]
        else:
            bounty_difference = most_probable_bounty
            sign = '+'

        time_elapsed: str = format_time_elapsed(time() - self.bounty_update_timestamp) \
            if self.bounty_update_timestamp is not None \
            else '???'  # TODO: check if the program even gets to this point

        self.last_bounty = most_probable_bounty
        self.update_bounty(most_probable_bounty)
        self.logger.log('MAIN', f'Updated bounty ${self.bounty:,} / {sign}${bounty_difference:,} over {time_elapsed}')
        self.update_presence()

        if self.save_captures:
            capture_sample: Image = Image.new('RGB', (max(self.raw_screenshot.width, self.screenshot.width),
                                                      self.raw_screenshot.height + self.screenshot.height),
                                              color=(0, 0, 0))
            capture_sample.paste(self.raw_screenshot, (0, 0))
            capture_sample.paste(self.screenshot, (0, self.raw_screenshot.height))

            if not os.path.exists(BountyTracker.CAPTURES_DIRECTORY):
                os.mkdir(BountyTracker.CAPTURES_DIRECTORY)
            capture_sample.save(f'{BountyTracker.CAPTURES_DIRECTORY}{self.bounty_update_timestamp}.png')

    def run(self) -> None:
        cycle_start: float = perf_counter()
        while True:
            if self.display is None or \
                    time() - self.message_update_timestamp >= \
                    self.display.exposure_time * BountyTracker.MESSAGE_UPDATE_DELAY:
                self.pick_new_fun_message()
                self.update_presence()

            if self.roblox_capture:
                if self.capture_screenshot():
                    self.process_detected_text()
            else:
                if perf_counter() - self.last_roblox_capture_search_timestamp > 1:
                    self.find_roblox_window()

            if (elapsed := (perf_counter() - cycle_start)) < self.capture_refresh_delay:
                sleep(self.capture_refresh_delay - elapsed)
                cycle_start = perf_counter()


def main() -> None:
    os.system('cls')
    program: BountyTracker = BountyTracker(LOGGER)
    program.initialize()
    program.run()


# def deinitialize() -> None:  # TODO: make sure to cleanup
#     pass


if __name__ == '__main__':
    # atexit.register(deinitialize)
    LAUNCHER.launch(main)
