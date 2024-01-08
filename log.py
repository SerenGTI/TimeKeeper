
from terminal import *

def warn(msg: str):
    print(colored("[WARNING] ", "brown", None), end="")
    print(msg)

def error(msg: str):
    print(colored("[ERROR] ", "light red", None), end="")
    print(msg)