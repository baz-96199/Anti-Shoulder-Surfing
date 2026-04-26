import cv2
import datetime
import os
import requests
import ctypes
import mysql.connector
import sys
import mediapipe as mp
import face_recognition
import time

# ---------------- SETTINGS ----------------
RISK_THRESHOLD = 60
COOLDOWN_SECONDS = 10   # prevent spam alerts
FRAME_SKIP = 2          # performance boost

# ---------------- RESOURCE PATH ----------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.getcwd()
    return os.path.join(base_path, relative_path)

# ---------------- LOAD OWNER FACES ----------------
owner_encodings = []
owner_folder = resource_path("owners")

for file in os.listdir(owner_folder):
    path = os.path.join(owner_folder, file)
    img = face_recognition.load_image_file(path)
    encodings = face_recognition.face_encodings(img)

    if encodings:
        owner_encodings.append(encodings[0])

if len(owner_encodings) == 0:
    print("No owner faces found!")
    sys.exit()

# ---------------- TELEGRAM ----------------
BOT_TOKEN = "8769002086:AAEbvObYm_Gpx9UWejTPd1sCMHJ4IKXIhC8"
CHAT_ID = "6071561703"

def send_telegram_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print("Telegram Error:", e)

def send_telegram_photo(photo_path):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        with open(photo_path, "rb") as photo:
            requests.post(url, data={"chat_id": CHAT_ID}, files={"photo": photo})
    except Exception as e:
        print("Telegram Photo Error:", e)

# ---------------- DB ----------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root@123"
    )

# ---------------- MEDIAPIPE ----------------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# ---------------- CREATE FOLDER ----------------
if not os.path.exists("static/images"):
    os.makedirs("static/images")

# ---------------- CAMERA ----------------
cap = cv2.VideoCapture(0)

alert_active = False
last_alert_time = 0
frame_count = 0

print("System Running...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % FRAME_SKIP != 0:
        continue

    face_count = 0
    unknown_detected = False
    close_person = False
    unknown_intruder_looking = False

    # ---------------- PREPROCESS FRAME ----------------
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # ---------------- FACE RECOGNITION ----------------
    face_locations = face_recognition.face_locations(rgb_frame)
    face_count = len(face_locations)

    # ---------------- ADVANCED HEAD + EYE TRACKING ----------------
    results = face_mesh.process(rgb_frame)
    h, w, _ = frame.shape

    for (top, right, bottom, left) in face_locations:

        # Distance check
        width = right - left
        if width > 120:
            close_person = True

        # Check if known
        is_unknown = False
        # Calculate encoding on full image using precise box
        encodings = face_recognition.face_encodings(rgb_frame, [(top, right, bottom, left)])
        if encodings:
            face_encoding = encodings[0]
            distances = face_recognition.face_distance(owner_encodings, face_encoding)
            if len(distances) > 0:
                best_match = min(distances)
                if best_match >= 0.6:  # Default tolerance (0.6), reduces false positives for owner
                    is_unknown = True
            else:
                is_unknown = True
        else:
            is_unknown = True

        if is_unknown:
            unknown_detected = True

            # Check if this specific unknown person is looking at the screen
            this_face_looking = False
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    nose = face_landmarks.landmark[1]
                    nx, ny = int(nose.x * w), int(nose.y * h)
                    
                    # Match mediapipe face to this face_recognition bounding box (with wider margins)
                    margin_x = (right - left) * 0.3
                    margin_y = (bottom - top) * 0.3
                    if (left - margin_x) <= nx <= (right + margin_x) and (top - margin_y) <= ny <= (bottom + margin_y):
                        # Head Orientation
                        left_outer = face_landmarks.landmark[33]
                        left_inner = face_landmarks.landmark[133]
                        right_outer = face_landmarks.landmark[263]
                        right_inner = face_landmarks.landmark[362]
                        
                        left_eye_center = (left_inner.x + left_outer.x) / 2
                        right_eye_center = (right_inner.x + right_outer.x) / 2
                        face_center_x = (left_eye_center + right_eye_center) / 2
                        
                        eye_dist = abs(left_eye_center - right_eye_center)
                        yaw_ratio = abs(nose.x - face_center_x) / (eye_dist + 1e-6)
                        looking_forward = yaw_ratio < 0.45  # Relaxed from 0.25 to catch side-glances
                        
                        # Eye Gaze using Iris landmarks (468, 473)
                        left_iris = face_landmarks.landmark[468]
                        right_iris = face_landmarks.landmark[473]
                        
                        def get_gaze_ratio(iris, inner, outer):
                            eye_width = abs(outer.x - inner.x)
                            dist = abs(iris.x - inner.x)
                            return dist / (eye_width + 1e-6)
                            
                        left_gaze = get_gaze_ratio(left_iris, left_inner, left_outer)
                        right_gaze = get_gaze_ratio(right_iris, right_inner, right_outer)
                        
                        eye_forward = (0.20 < left_gaze < 0.80) and (0.20 < right_gaze < 0.80) # Relaxed to 60% of eye width
                        
                        print(f"[DEBUG] Unknown face -> Yaw: {yaw_ratio:.2f}, L_Gaze: {left_gaze:.2f}, R_Gaze: {right_gaze:.2f}")
                        
                        if looking_forward and eye_forward:
                            this_face_looking = True
                            print("[ALERT] Intruder is looking at screen!")
                            break

            if this_face_looking:
                unknown_intruder_looking = True

    # ---------------- RISK SCORE ----------------
    risk_score = 0

    if face_count > 1:
        risk_score += 20

    if unknown_detected:
        risk_score += 30

    if unknown_intruder_looking:
        risk_score += 50

    if close_person:
        risk_score += 10

    print("Risk Score:", risk_score)

    # ---------------- INTRUSION ----------------
    current_time = time.time()

    if risk_score >= RISK_THRESHOLD and (current_time - last_alert_time > COOLDOWN_SECONDS):

        last_alert_time = current_time

        now = datetime.datetime.now()
        filename = f"static/images/intruder_{now.strftime('%H%M%S')}.jpg"
        cv2.imwrite(filename, frame)

        try:
            db = get_db_connection()
            cursor = db.cursor()

            query = "INSERT INTO privacy_system.intrusion_logs (timestamp, face_count, image_path) VALUES (%s, %s, %s)"
            values = (now, face_count, filename)

            cursor.execute(query, values)
            db.commit()

            cursor.close()
            db.close()

        except Exception as e:
            print("DB Error:", e)

        send_telegram_message("⚠️ Privacy Breach Detected!")
        send_telegram_photo(filename)

        print("Intrusion Detected!")

        ctypes.windll.user32.LockWorkStation()

cap.release()
cv2.destroyAllWindows()