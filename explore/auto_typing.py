import pyautogui
import time

def type_text(text, delay=0.05):
    time.sleep(delay)
    for char in text:
        pyautogui.typewrite(char)
        time.sleep(delay)

# Example usage
text = 'This is a sample text to type.'
type_text(text)