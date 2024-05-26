import cv2
import pymongo
from scipy.spatial import distance as dist
from bson.json_util import dumps
from datetime import datetime
from math import dist

point1 = None
point2 = None
data_sent = False

def mouse_callback(event, x, y, flags, param):
    global point1, point2, data_sent
    if event == cv2.EVENT_LBUTTONDOWN:
        if point1 is None:
            point1 = (x, y)
        elif point2 is None:
            point2 = (x, y)
        else:
            point1 = (x, y)
            point2 = None
        data_sent = False

def main():
    global point1, point2, data_sent
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Frame")

    cv2.setMouseCallback("Frame", mouse_callback)


    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["points_database"]
    collection = db["points_collection"]

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.putText(frame, "Press space to reset", (14, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        if point1:
            cv2.circle(frame, point1, 5, (0, 0, 255), -1)
            cv2.putText(frame, str(point1), point1, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        if point2:
            cv2.circle(frame, point2, 5, (0, 0, 255), -1)
            cv2.putText(frame, str(point2), point2, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        if point1 and point2:
            cv2.line(frame, point1, point2, (0, 255, 0), 2)

        if point1 and point2:
            distance = dist(point1,point2)
            cv2.putText(frame, f"Distance: {distance:.2f}", (14, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


            data = {
                "point1": point1,
                "point2": point2,
                "distance": distance,
                "timestamp": datetime.now().isoformat()
            }


            if not data_sent:
                collection.insert_one(data)
                print(f"Data saved to MongoDB: {dumps(data)}")
                data_sent = True

        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            point1 = None
            point2 = None
            data_sent = False

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()