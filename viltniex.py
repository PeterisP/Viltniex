import pyautogui
# im = pyautogui.screenshot('test.png')
corner_x, corner_y, _, _ = pyautogui.locateOnScreen('images/bluestacks.png')
print(corner_x, corner_y)
pyautogui.click(corner_x + 50, corner_y + 50)
print('haa')