import win32gui, win32api, win32con


class WindowsRender:
    def __init__(self, color: tuple = (255, 0, 0)):
        self.device_context = win32gui.GetDC(0)
        self.pen_color = win32api.RGB(*color)
        self.pen = None

    def draw_rectangle(self, rect: tuple):
        x, y, w, h = rect
        x2, y2 = x + w, y + h

        self.pen = win32gui.CreatePen(win32con.PS_SOLID, 1, self.pen_color)
        old_pen = win32gui.SelectObject(self.device_context, self.pen)

        win32gui.MoveToEx(self.device_context, x, y)
        win32gui.LineTo(self.device_context, x2, y)
        win32gui.LineTo(self.device_context, x2, y2)
        win32gui.LineTo(self.device_context, x, y2)
        win32gui.LineTo(self.device_context, x, y)

        win32gui.SelectObject(self.device_context, old_pen)
        win32gui.DeleteObject(self.pen)