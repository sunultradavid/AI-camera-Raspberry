import os
import time
from datetime import datetime
import cv2
from picamera2 import Picamera2
import yagmail

# Set up email (secure: use app password or env vars in real usage)
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASS = "your_password"
EMAIL_TO = "recipient@example.com"

yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASS)

# Load Haar cascade
cascade = cv2.CascadeClassifier("haarcascade_upperbody.xml")
os.makedirs("detections", exist_ok=True)

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()

last_detection_time = 0
cooldown = 10  # seconds between alerts

print("[INFO] Starting upper body detection...")
# Save image to date-based folder
date_str = datetime.now().strftime("%Y-%m-%d")
folder = f"detections/{date_str}"
os.makedirs(folder, exist_ok=True)

timestamp = datetime.now().strftime("%H%M%S")
filename = f"{folder}/detected_{timestamp}.jpg"

# Save image
cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
print(f"[INFO] Saved image: {filename}")

# Log the event
with open("detections/detections.log", "a") as log_file:
    log_file.write(f"{datetime.now()}: Saved {filename}\n")


while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    bodies = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

    if len(bodies) > 0 and time.time() - last_detection_time > cooldown:
        for (x, y, w, h) in bodies:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Upper Body", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Save image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"detections/detected_{timestamp}.jpg"
        cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        print(f"[INFO] Saved image: {filename}")

        # Send email
        yag.send(to=EMAIL_TO, subject="Upper Body Detected", contents="Motion was detected by your Pi!", attachments=filename)
        print(f"[INFO] Email sent to {EMAIL_TO}")

        last_detection_time = time.time()

    # Optional: show preview
    cv2.imshow("Upper Body Detection", frame)
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
