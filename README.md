# Lyric MP3 player V1.0
Поигрыватель MP3 файлов, c возможностью хранения списков воспроизведения
Для полноценной работы программы трубуетс установить tkinter-tooltip

pip install tkinter-tooltip
Остальные библиотеки можно установить прямо из PyCharm
Вот их список:

import os.path
import time
import sqlite3
import pygame
import webbrowser
import requests
import lxml
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilenames
from tktooltip import ToolTip
from tinytag import TinyTag
from bs4 import BeautifulSoup
