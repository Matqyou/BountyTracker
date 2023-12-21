import win32gui, win32api, win32con


class WindowsRender:
    def __init__(self):
        self.device_context = win32gui.GetDC(0)
        self.pen_color = win32api.RGB(255, 0, 0)
        self.pen = None

    def DrawRectangle(self, rect: tuple):
        X, Y, W, H = rect
        X2, Y2 = X + W, Y + H

        self.pen = win32gui.CreatePen(win32con.PS_SOLID, 1, self.pen_color)
        old_pen = win32gui.SelectObject(self.device_context, self.pen)

        win32gui.MoveToEx(self.device_context, X, Y)
        win32gui.LineTo(self.device_context, X2, Y)
        win32gui.LineTo(self.device_context, X2, Y2)
        win32gui.LineTo(self.device_context, X, Y2)
        win32gui.LineTo(self.device_context, X, Y)

        win32gui.SelectObject(self.device_context, old_pen)
        win32gui.DeleteObject(self.pen)