import threading
import os

def run_main():
    os.system("python main.py")

def run_dashboard():
    os.system("python app.py")

t1 = threading.Thread(target=run_main)
t2 = threading.Thread(target=run_dashboard)

t1.start()
t2.start()

t1.join()
t2.join()