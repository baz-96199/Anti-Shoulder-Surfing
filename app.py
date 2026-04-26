from flask import Flask, render_template, redirect
import mysql.connector
import os
import webbrowser

app = Flask(__name__)

# ---------------- DB CONNECTION ----------------
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="root@123",
        database="privacy_system",
        auth_plugin='mysql_native_password'
    )

# ---------------- DASHBOARD ----------------
@app.route("/")
def dashboard():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM intrusion_logs ORDER BY id DESC")
        data = cursor.fetchall()

        cursor.close()
        db.close()

        # -------- SYSTEM STATUS (LIVE) --------
        try:
            with open("system_status.txt", "r") as f:
                system_state = f.read().strip()
        except:
            system_state = "STOPPED"

        status = "ACTIVE" if system_state == "RUNNING" else "SAFE"

        return render_template("dashboard.html", data=data, status=status)

    except Exception as e:
        return f"Database Error: {e}"

# ---------------- DELETE SINGLE ----------------
@app.route("/delete/<int:id>")
def delete_record(id):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Get image path
        cursor.execute("SELECT image_path FROM intrusion_logs WHERE id=%s", (id,))
        result = cursor.fetchone()

        if result:
            image_path = result[0]
            if os.path.exists(image_path):
                os.remove(image_path)

        # Delete record
        cursor.execute("DELETE FROM intrusion_logs WHERE id=%s", (id,))
        db.commit()

        cursor.close()
        db.close()

        return redirect("/")

    except Exception as e:
        return f"Delete Error: {e}"

# ---------------- CLEAR ALL ----------------
@app.route("/clear")
def clear_all():
    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Delete images
        cursor.execute("SELECT image_path FROM intrusion_logs")
        all_images = cursor.fetchall()

        for img in all_images:
            if os.path.exists(img[0]):
                os.remove(img[0])

        # Delete DB records
        cursor.execute("DELETE FROM intrusion_logs")
        db.commit()

        cursor.close()
        db.close()

        return redirect("/")

    except Exception as e:
        return f"Clear Error: {e}"

# ---------------- RUN ----------------
if __name__ == "__main__":
    import threading
    threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(debug=False, use_reloader=False)