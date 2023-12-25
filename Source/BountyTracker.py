from SaveTypes import SaveTypes
from time import sleep, time
from FunMessage import *
from Launcher import *
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
    from WindowsRender import *
    import pytesseract
    import pyautogui
    import requests
except ModuleNotFoundError:
    LOGGER.log('LIBRARIES', 'Installing libraries..')
    os.system(r'pip install -r ..\requirements.txt')
    LOGGER.log('LIBRARIES', 'Installed successfully!')
    subprocess.call([sys.executable] + sys.argv)
    exit()

if (found_tesseract_path := shutil.which('tesseract')) is None:
    tesseract_name = 'tesseract-ocr-setup-3.02.02.exe'
    tesseract_setup = f'..\\{tesseract_name}'
    if not os.path.exists(tesseract_setup):
        LOGGER.log('TESSERACT', f'Downloading {tesseract_name}')

        file_url = 'https://downloads.sourceforge.net/project/tesseract-ocr-alt/tesseract-ocr-setup-3.02.02.exe?ts=gAAAAABlh0rv-caw3tHhQdJ2gIURc8E-fr0Wl-k6t-XMqpkjwNWMdXrhmYg5WtV7JvFwlW9jfgSIIoe_6SxZumFImStJkzGcpw%3D%3D&amp;use_mirror=kumisystems&amp;r=https%3A%2F%2Fwww.google.com%2F'
        response = requests.get(file_url)
        if response.status_code == 200:
            with open(tesseract_setup, 'wb') as file:
                file.write(response.content)
            LOGGER.log('TESSERACT', 'Download complete!')
        else:
            LOGGER.log('TESSERACT', 'Could not download tesseract setup, try again or use link from github')
    LOGGER.log()
    LOGGER.log('TESSERACT', f'Install {tesseract_name} with the default install location')
    exit()

pytesseract.pytesseract.tesseract_cmd = found_tesseract_path
APPLICATION_ID = 1185231216211918900
DISCORD_PRESENCE: DiscordPresence = DiscordPresence(LOGGER, str(APPLICATION_ID))
SAVE_FILE = 'LastBounty'
CONFIGURATION_FILE = '../Configure.txt'
MESSAGE_DURATION: float = 45
LAUNCH_TIMESTAMP: int = int(time())
LAST_MESSAGE_UPDATE: float = time()
LAST_VALID_BOUNTY: int = None
CURRENT_BOUNTY: int = None
BOUNTY_TIMESTAMP: float = None
CURRENT_FUN_MESSAGES: list[FunMessage] = []
CURRENT_FUN_MESSAGE: FunMessage = None
WINDOWS_RENDER = WindowsRender()


# Options read from Configure.txt file
CAPTURE_RECTANGLE: tuple = None
SHOW_CAPTURE_RECTANGLE: bool = None
CAPTURE_REFRESH_RATE: float = None


def FormatTime(seconds: float) -> str:
    seconds = int(seconds)
    return f'{seconds // 3600:>02}:{(seconds // 60) % 60:>02}:{seconds % 60:>02}'


def ShowCaptureRectangle(rectangle: tuple) -> None:
    try:
        while True:
            WINDOWS_RENDER.DrawRectangle(rectangle)
    except KeyboardInterrupt:
        pass


def PickNewMessage() -> None:
    global CURRENT_FUN_MESSAGE, LAST_MESSAGE_UPDATE
    while not (filtered_selection := [fun_message for fun_message in CURRENT_FUN_MESSAGES]):
        CURRENT_FUN_MESSAGES.clear()
        CURRENT_FUN_MESSAGES[:] = [msg for msg in FUN_MESSAGES if random.random() < msg.chance]
    CURRENT_FUN_MESSAGE = random.choice(filtered_selection)
    CURRENT_FUN_MESSAGES.remove(CURRENT_FUN_MESSAGE)
    LAST_MESSAGE_UPDATE = time()


def UpdateBounty(bounty: int, update_just_message: bool) -> None:
    global BOUNTY_TIMESTAMP

    if not update_just_message:
        with open(SAVE_FILE, 'w') as update_file:
            BOUNTY_TIMESTAMP = int(time())
            update_file.write(f'{bounty}\n{BOUNTY_TIMESTAMP}')

    if DISCORD_PRESENCE.show_discord_activity:
        amount = None
        if CURRENT_FUN_MESSAGE.item_price > 0:
            if CURRENT_FUN_MESSAGE.item_price > CURRENT_BOUNTY:
                fraction = bounty / CURRENT_FUN_MESSAGE.item_price * 100
                percision_places = int(fraction < 10)
                amount = f'{fraction:.{percision_places}f}% of a'
                first_letter_index = CURRENT_FUN_MESSAGE.message_format.find('{}') + 3
                first_letter = CURRENT_FUN_MESSAGE.message_format[first_letter_index:first_letter_index + 1]
                if first_letter.lower() in 'aeiou':
                    amount += 'n'
            else:
                amount = bounty // CURRENT_FUN_MESSAGE.item_price

        suffix = None
        if (suffix_info := CURRENT_FUN_MESSAGE.suffix_info) is not None:
            index = type(amount) == str or amount == 1
            suffix = suffix_info[index]

        state_text = CURRENT_FUN_MESSAGE.message_format.format(amount, suffix)
        details_text = f'Current bounty: ${bounty:,}'
        image_text = f'Dead bounty: ${round(bounty * 0.4):,} and it\'s been {FormatTime(time() - BOUNTY_TIMESTAMP)} since last bounty update'

        image_kwargs = (
            {'small_image': CURRENT_FUN_MESSAGE.icon_key, 'small_text': image_text},
            {'large_image': CURRENT_FUN_MESSAGE.icon_key, 'large_text': image_text}
        )[CURRENT_FUN_MESSAGE.image_size]

        DISCORD_PRESENCE.update(state=state_text,
                                details=details_text,
                                start=LAUNCHER.startup_timestamp_int,
                                **image_kwargs)


def LoadBounty() -> None:
    global BOUNTY_TIMESTAMP, CURRENT_BOUNTY, LAST_VALID_BOUNTY
    if not os.path.exists(SAVE_FILE):
        BOUNTY_TIMESTAMP = int(time())
        save_values = {
            'bounty': 0,
            'bounty_timestamp': BOUNTY_TIMESTAMP
        }
        SaveTypes.save_to_file(SAVE_FILE, save_values)
    else:
        load_types = {
            'bounty': int,
            'bounty_timestamp': int
        }
        load_values = SaveTypes.load_file(SAVE_FILE, load_types)
        LAST_VALID_BOUNTY = CURRENT_BOUNTY = load_values['bounty']
        BOUNTY_TIMESTAMP = load_values['bounty_timestamp']
    LOGGER.log('LOAD', f'Loaded bounty ${CURRENT_BOUNTY:,}')
    LOGGER.log('LOAD', f'It\'s been {FormatTime(time() - BOUNTY_TIMESTAMP)} since last bounty update')


def main() -> None:
    global CAPTURE_RECTANGLE, \
        SHOW_CAPTURE_RECTANGLE, \
        SHOW_DISCORD_ACTIVITY, \
        CAPTURE_REFRESH_RATE, \
        RICH_PRESENCE, \
        CURRENT_BOUNTY, \
        LAST_VALID_BOUNTY

    load_types = {
        'capture_rectangle': (int, int, int, int),
        'show_capture_rectangle': bool,
        'log_to_files': bool,
        'show_discord_activity': bool,
        'capture_refresh_rate': float
    }
    load_values = SaveTypes.load_file(CONFIGURATION_FILE, load_types)

    try:
        CAPTURE_RECTANGLE = load_values['capture_rectangle']
        SHOW_CAPTURE_RECTANGLE = load_values['show_capture_rectangle']
        LOGGER.set_log_to_file(load_values['log_to_files'])
        DISCORD_PRESENCE.set_show_discord_activity(load_values['show_discord_activity'])
        CAPTURE_REFRESH_RATE = load_values['capture_refresh_rate']
    except KeyError:
        raise KeyError('Some value was missing from the configuration file')

    x, y, w, h = CAPTURE_RECTANGLE
    LOGGER.log('CONFIGURE', f'Will be reading pixel coordinates: {x}x {y}y {w}w {h}h')
    LOGGER.log('CONFIGURE', f'Showing capture rectangle on screen: {SHOW_CAPTURE_RECTANGLE}')
    LOGGER.log('CONFIGURE', f'Log everything to files: {LOGGER.log_to_file}')
    LOGGER.log('CONFIGURE', f'Show activity on discord: {DISCORD_PRESENCE.show_discord_activity}')
    LOGGER.log('CONFIGURE', f'Capture refresh rate delay: {CAPTURE_REFRESH_RATE}s')

    if SHOW_CAPTURE_RECTANGLE:
        multiprocessing.Process(target=ShowCaptureRectangle, args=(CAPTURE_RECTANGLE,)).start()

    bounty_regular_expression = re.compile(r'\$\d+\sBounty')
    LoadBounty()
    DISCORD_PRESENCE.connect()

    while True:
        if CURRENT_FUN_MESSAGE is None or time() - LAST_MESSAGE_UPDATE >= CURRENT_FUN_MESSAGE.exposure_time * MESSAGE_DURATION:
            PickNewMessage()
            UpdateBounty(CURRENT_BOUNTY, True)
        screenshot = pyautogui.screenshot(region=CAPTURE_RECTANGLE).resize((w * 3, h * 3))
        detected_text = pytesseract.image_to_string(screenshot).strip()

        if detected_text:
            dollar_at = detected_text.find('$')
            bounty_at = detected_text.find('Bounty')
            if -1 < dollar_at < bounty_at and bounty_regular_expression.match(detected_text):  # $d Bounty
                CURRENT_BOUNTY = detected_text[dollar_at + 1:bounty_at - 1]
                CURRENT_BOUNTY = int(CURRENT_BOUNTY)
                if LAST_VALID_BOUNTY != CURRENT_BOUNTY:
                    LAST_VALID_BOUNTY = CURRENT_BOUNTY
                    LOGGER.log('MAIN', f'New bounty: ${CURRENT_BOUNTY:,} | `{detected_text}`')
                    UpdateBounty(CURRENT_BOUNTY, update_just_message=False)

        sleep(CAPTURE_REFRESH_RATE)


if __name__ == '__main__':
    LAUNCHER.launch(main)
