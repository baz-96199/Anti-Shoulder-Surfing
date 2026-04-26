# Anti-Shoulder-Surfing
It is a project on Anti Shoulder Surfing in which you will get to know if anyone is looking from behind at you screen.
If any unknownn person is looking at your screen then your device will automatically detect that person take screenshot and will lock your screen.

**Features:-**
✔ Real-time webcam monitoring
✔ Owner vs Unknown face recognition
✔ Eye gaze / head direction detection
✔ Privacy risk score engine
✔ Screenshot evidence capture
✔ Telegram instant alerts
✔ Automatic system lock
✔ MySQL intrusion logs
✔ Flask live dashboard
✔ Delete / Clear records from dashboard

**Technologies Used:-**
Python
OpenCV
face_recognition
MediaPipe
Flask
MySQL
HTML / CSS
Telegram Bot API

**Required things to install:-**
pip install opencv-python
pip install face_recognition
pip install mediapipe==0.10.9
pip install flask
pip install mysql-connector-python
pip install requests

**MySQL Setup:-**
Create database:

CREATE DATABASE privacy_system;
Create table:
USE privacy_system;
CREATE TABLE intrusion_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME,
    face_count INT,
    image_path VARCHAR(255)
);

**Structure of folders**
Anti_Shoulder_Surfing_Project/
│── main.py
│── app.py
│── requirements.txt
│── system_status.txt
│── README.md
│
├── owners/
│   ├── owner1.jpg
│   ├── owner2.jpg
│   └── owner3.jpg
│
├── static/
│   └── images/
│
├── templates/
│   └── dashboard.html
│
└── haarcascade_frontalface_default.xml

**Change your telegram bot credentials**
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

**Change MySQL password**
password="your_password"

**Working**
Webcam detects faces
↓
Checks owner vs unknown
↓
Analyzes gaze direction
↓
Calculates risk score
↓
If risk high:
- Save screenshot
- Send Telegram alert
- Store in MySQL
- Lock Windows
- Haar Cascade File

**This project uses:**

haarcascade_frontalface_default.xml

Included in repository.
If missing, OpenCV built-in version can also be used automatically.
you need to find this in your pc at this location
C:\Users\YourName\AppData\Local\Programs\Python\Python310\Lib\site-packages\cv2\data\
