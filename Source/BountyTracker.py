from datetime import datetime
from time import sleep, time
from FunMessage import *
import subprocess
import traceback
import threading
import random
import shutil
import sys
import os
import re

try:
    from pypresence import Presence, exceptions
    from WindowsRender import *
    import pytesseract
    import pyautogui
    import requests
except ModuleNotFoundError:
    print('Installing libraries..')
    os.system(r'pip install -r ..\requirements.txt')
    print('Installed successfully!')
    subprocess.call([sys.executable] + sys.argv)
    exit()

if (found_tesseract_path := shutil.which('tesseract')) is None:
    tesseract_name = 'tesseract-ocr-setup-3.02.02.exe'
    tesseract_setup = f'..\\{tesseract_name}'
    if not os.path.exists(tesseract_setup):
        print(f'Downloading {tesseract_name}')

        file_url = 'https://downloads.sourceforge.net/project/tesseract-ocr-alt/tesseract-ocr-setup-3.02.02.exe?ts=gAAAAABlh0rv-caw3tHhQdJ2gIURc8E-fr0Wl-k6t-XMqpkjwNWMdXrhmYg5WtV7JvFwlW9jfgSIIoe_6SxZumFImStJkzGcpw%3D%3D&amp;use_mirror=kumisystems&amp;r=https%3A%2F%2Fwww.google.com%2F'
        response = requests.get(file_url)
        if response.status_code == 200:
            with open(tesseract_setup, 'wb') as file:
                file.write(response.content)
            print('Download complete!')
        else:
            print('Could not download tesseract setup, try again or use link from github')
    print()
    print(f'Install {tesseract_name} with the default install location')
    exit()

pytesseract.pytesseract.tesseract_cmd = found_tesseract_path
LOGS_DIRECTORY = 'logs/'
APPLICATION_ID = 1185231216211918900
SAVE_FILE = 'LastBounty'
MESSAGE_DURATION: float = 45
LAUNCH_TIMESTAMP: int = int(time())
LAST_MESSAGE_UPDATE: float = time()
LAST_VALID_BOUNTY: int = None
CURRENT_BOUNTY: int = None
BOUNTY_TIMESTAMP: float = None
CURRENT_FUN_MESSAGES: list[FunMessage] = []
CURRENT_FUN_MESSAGE: FunMessage = None
RICH_PRESENCE: Presence = None
WINDOWS_RENDER = WindowsRender()
CURRENT_LOG_FILE = f'{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}'


# Options read from Configure.txt file
BOUNTY_LOCATION_ON_SCREEN: tuple = None
DRAW_RECTANGLE_AROUND_CAPTURE: bool = None
LOG_EVERYTHING_TO_FILE: bool = None
SHOW_DISCORD_ACTIVITY: bool = None


def Print(text) -> None:
    out_text = f'[{datetime.now().strftime("%m/%d/%Y %H:%M:%S")}] {text}\n'
    print(out_text, end='')

    if LOG_EVERYTHING_TO_FILE:
        if not os.path.exists(LOGS_DIRECTORY):
            os.mkdir(LOGS_DIRECTORY)
        with open(f'{LOGS_DIRECTORY}{CURRENT_LOG_FILE}', 'a') as log_file:
            log_file.write(out_text)



def ConnectPresence() -> bool:
    try:
        RICH_PRESENCE.connect()
        Print(f'Connected to discord application {APPLICATION_ID}')
        return True
    except exceptions.DiscordNotFound:
        global SHOW_DISCORD_ACTIVITY
        Print('Couldn\'t find discord, switched to offline mode')
        SHOW_DISCORD_ACTIVITY = False
    return False


def FormatTime(seconds: float) -> str:
    seconds = int(seconds)
    return f'{seconds // 3600:>02}:{(seconds // 60) % 60:>02}:{seconds % 60:>02}'


def ShowCaptureRectangle() -> None:
    WINDOWS_RENDER.DrawRectangle(BOUNTY_LOCATION_ON_SCREEN)


def ThreadShowCaptureRectangle() -> None:
    while True:
        ShowCaptureRectangle()


def PickNewMessage() -> None:
    global CURRENT_FUN_MESSAGE, LAST_MESSAGE_UPDATE
    while not (filtered_selection := [fun_message for fun_message in CURRENT_FUN_MESSAGES]):
        CURRENT_FUN_MESSAGES.clear()
        CURRENT_FUN_MESSAGES[:] = [msg for msg in FUN_MESSAGES if random.random() < msg.chance]
    CURRENT_FUN_MESSAGE = random.choice(filtered_selection)
    CURRENT_FUN_MESSAGES.remove(CURRENT_FUN_MESSAGE)
    LAST_MESSAGE_UPDATE = time()


def UpdateBounty(bounty: int, update_just_message: bool) -> None:
    global BOUNTY_TIMESTAMP, SHOW_DISCORD_ACTIVITY

    if not update_just_message:
        with open(SAVE_FILE, 'w') as update_file:
            BOUNTY_TIMESTAMP = int(time())
            update_file.write(f'{bounty}\n{BOUNTY_TIMESTAMP}')

    if not SHOW_DISCORD_ACTIVITY:
        return

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

    while True:
        try:
            RICH_PRESENCE.update(details=details_text, state=state_text, start=LAUNCH_TIMESTAMP, **image_kwargs)
            break
        except exceptions.PipeClosed:
            Print(f'Discord connection was closed, switched to offline mode')
            SHOW_DISCORD_ACTIVITY = False


def LoadBounty() -> None:
    global BOUNTY_TIMESTAMP, CURRENT_BOUNTY, LAST_VALID_BOUNTY
    if not os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'w') as f:
            CURRENT_BOUNTY = LAST_VALID_BOUNTY = 0
            BOUNTY_TIMESTAMP = int(time())
            f.write(f'0\n{BOUNTY_TIMESTAMP}')
    else:
        with open(SAVE_FILE, 'r') as f:
            CURRENT_BOUNTY, BOUNTY_TIMESTAMP = [int(num) for num in f.read().splitlines(keepends=False)]
            LAST_VALID_BOUNTY = CURRENT_BOUNTY
    Print(f'Loaded bounty ${CURRENT_BOUNTY:,}')
    Print(f'It\'s been {FormatTime(time() - BOUNTY_TIMESTAMP)} since last bounty update')


def main() -> None:
    global BOUNTY_LOCATION_ON_SCREEN, \
        DRAW_RECTANGLE_AROUND_CAPTURE, \
        LOG_EVERYTHING_TO_FILE, \
        SHOW_DISCORD_ACTIVITY, \
        CURRENT_LOG_FILE, \
        RICH_PRESENCE, \
        CURRENT_BOUNTY, \
        LAST_VALID_BOUNTY

    with open('../Configure.txt', 'r') as capture_file:
        capture_options = [line for line in capture_file.read().splitlines(keepends=False)
                           if line and not line.startswith('#')]

    num_capture_options = 4
    if len(capture_options) == num_capture_options:
        BOUNTY_LOCATION_ON_SCREEN = [int(param) for param in capture_options[0].split(',')]
        DRAW_RECTANGLE_AROUND_CAPTURE = capture_options[1].lower() == 'true'
        LOG_EVERYTHING_TO_FILE = capture_options[2].lower() == 'true'
        SHOW_DISCORD_ACTIVITY = capture_options[3].lower() == 'true'
    else:
        raise ValueError(f'Configure.txt options must match {num_capture_options}, found: {capture_options}')

    if LOG_EVERYTHING_TO_FILE:
        instance_number = 1
        suffix = ''
        check_for_file = f'{CURRENT_LOG_FILE}{suffix}.txt'
        while os.path.exists(f'{LOGS_DIRECTORY}{check_for_file}'):
            instance_number += 1
            suffix = f' {instance_number}'
            check_for_file = f'{CURRENT_LOG_FILE}{suffix}.txt'
        CURRENT_LOG_FILE = check_for_file

        Print(f'Current log file {CURRENT_LOG_FILE}')

    x, y, w, h = BOUNTY_LOCATION_ON_SCREEN

    Print(f'Will be reading pixel coordinates: {x}x {y}y {w}w {h}h')
    Print(f'Showing capture rectangle on screen: {DRAW_RECTANGLE_AROUND_CAPTURE}')
    Print(f'Log everything to files: {LOG_EVERYTHING_TO_FILE}')
    Print(f'Show activity on discord: {SHOW_DISCORD_ACTIVITY}')

    if DRAW_RECTANGLE_AROUND_CAPTURE:
        threading.Thread(target=ThreadShowCaptureRectangle).start()

    bounty_regular_expression = re.compile(r'\$\d+\sBounty')
    LoadBounty()

    if SHOW_DISCORD_ACTIVITY:
        RICH_PRESENCE = Presence(str(APPLICATION_ID))
        ConnectPresence()

    while True:
        if CURRENT_FUN_MESSAGE is None or time() - LAST_MESSAGE_UPDATE >= CURRENT_FUN_MESSAGE.exposure_time * MESSAGE_DURATION:
            PickNewMessage()
            UpdateBounty(CURRENT_BOUNTY, True)
        screenshot = pyautogui.screenshot(region=BOUNTY_LOCATION_ON_SCREEN).resize((w * 3, h * 3))
        detected_text = pytesseract.image_to_string(screenshot).strip()

        if detected_text:
            dollar_at = detected_text.find('$')
            bounty_at = detected_text.find('Bounty')
            if -1 < dollar_at < bounty_at and bounty_regular_expression.match(detected_text):  # $d Bounty
                CURRENT_BOUNTY = detected_text[dollar_at + 1:bounty_at - 1]
                CURRENT_BOUNTY = int(CURRENT_BOUNTY)
                if LAST_VALID_BOUNTY != CURRENT_BOUNTY:
                    LAST_VALID_BOUNTY = CURRENT_BOUNTY
                    Print(f'New bounty: ${CURRENT_BOUNTY:,} | `{detected_text}`')
                    UpdateBounty(CURRENT_BOUNTY, update_just_message=False)

        sleep(1)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        error_string = traceback.format_exc()
        Print(f'An error has occurred: {e}\nLog written to {CURRENT_LOG_FILE}\n{error_string}')
