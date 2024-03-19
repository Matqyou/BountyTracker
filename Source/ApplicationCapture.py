from PIL import Image
import win32gui
import win32con
import win32ui


class ApplicationCapture:
    WINDOWED_OFFSET_X: int = 8
    WINDOWED_OFFSET_Y: int = 31

    def __init__(self, hwnd: int, capture_rect: tuple[int, int, int, int]):
        self.application_handle: int = hwnd
        self.capture_x, self.capture_y, self.capture_w, self.capture_h = capture_rect
        self.capture_pos = self.capture_x + ApplicationCapture.WINDOWED_OFFSET_X, \
            self.capture_y + ApplicationCapture.WINDOWED_OFFSET_Y
        self.capture_size = self.capture_w, self.capture_h
        self.released: bool = False

        # Get handles
        self.device_context_handle: int = win32gui.GetWindowDC(self.application_handle)
        self.microsoft_device_context: win32ui.PyCDC = win32ui.CreateDCFromHandle(self.device_context_handle)
        self.save_device_context: win32ui.PyCDC = self.microsoft_device_context.CreateCompatibleDC()

        # Create a bitmap
        self.save_bitmap: win32ui.PyCBitmap = win32ui.CreateBitmap()
        self.save_bitmap.CreateCompatibleBitmap(self.microsoft_device_context, *self.capture_size)
        self.save_device_context.SelectObject(self.save_bitmap)

    def capture(self) -> Image:
        self.save_device_context.BitBlt((0, 0), self.capture_size,
                                        self.microsoft_device_context,
                                        self.capture_pos, win32con.SRCCOPY)

        bitmap_information: dict = self.save_bitmap.GetInfo()
        bitmap_string: str = self.save_bitmap.GetBitmapBits(True)
        image_size: tuple[int, int] = bitmap_information['bmWidth'], bitmap_information['bmHeight']

        return Image.frombuffer('RGB', image_size, bitmap_string, 'raw', 'BGRX', 0, 1)

    def is_open(self) -> bool:
        return win32gui.IsWindow(self.application_handle)

    def release_resources(self, delete_dc_from_handle: bool) -> None:
        if self.released:
            return

        self.released = True
        if self.save_bitmap:
            win32gui.DeleteObject(self.save_bitmap.GetHandle())
        if self.save_device_context:
            self.save_device_context.DeleteDC()
        if delete_dc_from_handle:
            if self.microsoft_device_context:
                self.microsoft_device_context.DeleteDC()
        if self.device_context_handle:
            win32gui.ReleaseDC(self.application_handle, self.device_context_handle)

    def __del__(self) -> None:
        self.release_resources(delete_dc_from_handle=True)

    def window_closed(self) -> None:
        self.release_resources(delete_dc_from_handle=False)
