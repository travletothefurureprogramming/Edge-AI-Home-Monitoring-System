import cv2
import ultralytics
import random
import utils
import time

yolo = ultralytics.YOLO("yolov8s.pt")

is_running = False

def getColours(cls_num):
    """Generate unique colors for each class ID"""
    random.seed(cls_num)
    return tuple(random.randint(0, 255) for _ in range(3))

def start_security():
    global is_running
    
    if is_running:
        print("Η ασφάλεια τρέχει ήδη!")
        return
        
    videoCap = cv2.VideoCapture(0)
    if not videoCap.isOpened():
        print("Σφάλμα: Δεν είναι δυνατή η πρόσβαση στην κάμερα.")
        return

    is_running = True
    person_detected = False
    print("Το σύστημα Edge-AI Monitoring ξεκίνησε...")

    while is_running:
        ret, frame = videoCap.read()
        if not ret:
            print("Αποτυχία λήψης frame από την κάμερα.")
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

                    if class_name == "person":
                        detected_person_now = True

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

        if detected_person_now and not person_detected:
            utils.send_security_notification({"person": "yes"})
            person_detected = True

        if not detected_person_now:
            person_detected = False

        cv2.imshow("Edge-AI Camera Monitoring", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("Τερματισμός κάμερας και αποδέσμευση πόρων...")
    is_running = False
    videoCap.release()
    cv2.destroyAllWindows()
    
    cv2.waitKey(1) 

def stop_security():
    global is_running
    print("Λήψη εντολής για κλείσιμο της ασφάλειας...")
    is_running = False 

if __name__ == "__main__":
    start_security()