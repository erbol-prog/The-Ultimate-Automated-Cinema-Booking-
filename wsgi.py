import sys
import os

# Путь к вашему проекту
path = '/home/erbolsk/cinema_project'
if path not in sys.path:
    sys.path.append(path)




from app import app as application  # Замените `app` на имя вашего основного файла
