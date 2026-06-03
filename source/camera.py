import cv2
import ultralytics
import random
import utils

# Φόρτωση YOLOv8
yolo = ultralytics.YOLO("yolov8s.pt")

def getColours(cls_num):
    """Generate unique colors for each class ID"""
    random.seed(cls_num)
    return tuple(random.randint(0, 255) for _ in range(3))

def start_security():
    videoCap = cv2.VideoCapture(0)
    person_detected = False

    while True:
        ret, frame = videoCap.read()
        if not ret:
            break

        # YOLO tracking
        results = yolo.track(frame, stream=True)

        detected_person_now = False

        for result in results:
            class_names = result.names

            for box in result.boxes:
                if box.conf[0] > 0.4:
                    cls = int(box.cls[0])
                    class_name = class_names[cls]

                    # Αν βρέθηκε άνθρωπος
                    if class_name == "person":
                        detected_person_now = True

                    # Σχεδίαση bounding box
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    colour = getColours(cls)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)
                    cv2.putText(
                        frame,
                        f"{class_name} {float(box.conf[0]):.2f}",
                        (x1, max(y1 - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        colour,
                        2
                    )

        # Στείλε ειδοποίηση ΜΟΝΟ όταν εμφανιστεί άνθρωπος
        if detected_person_now and not person_detected:
            utils.send_security_notification({"person": "yes"})
            person_detected = True

        # Αν δεν υπάρχει άνθρωπος στο frame, reset
        if not detected_person_now:
            person_detected = False

        # Εμφάνιση εικόνας
        cv2.imshow("Camera", frame)

        # Έξοδος με 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    videoCap.release()
    cv2.destroyAllWindows()

def stop_security():
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_security()