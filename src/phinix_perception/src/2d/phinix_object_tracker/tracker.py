#!/usr/bin/env python
# coding: utf-8
!pip install ultralytics
!pip install supervision
# !pip install opencv-python


import cv2
from ultralytics import YOLO
import supervision as sv
import argparse



# take model parameter as command line argument 
model = YOLO("yolov8s.pt")


parser = argparse.ArgumentParser(description="Object Detection and Tracking using YOLO or Supervision")
parser.add_argument("--video", type=str, default="a.mp4", help="Path to input video file")
parser.add_argument("--model", type=str, default="yolov8s.pt", help="Path to YOLO model file")
parser.add_argument("--tracker", type=str, default="bytetrack.yaml", help="Path to tracker config file (YOLO mode)")
parser.add_argument("--use-yolo-track", action="store_true", help="Use YOLO's built-in tracking instead of Supervision ByteTrack")
args = parser.parse_args()




def detect_objects(frame):
    detection_results = model(frame)
    return detection_results


# def track_objects(frame, detection_results):
#     results = model.track(frame, persist=True, tracker="bytetrack.yaml")
#     return results


# USING SUPERVISION ----
def track_objects(frame, detection_results):
    tracker = sv.ByteTrack()
    results = tracker.update(detection_results)

    if args.use_yolo_track:
        # Integrated
        results = model.track(source=frame, tracker=args.tracker, persist=True)
    else:
        # SV
        results = tracker.update(detection_results)
    
    return results


def video_scan(video_path, output_path="tracked_output.mp4"):
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    output_video = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 2 FUNCTION CALLS
        # first line detection - gives bounding boxes and labels
        # second function does the tracking

        detection_results = detect_objects(frame)
        results = track_objects(frame,detection_results)

        # Draw tracking boxes
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
                track_id = int(box.id[0]) if box.id is not None else -1  # Object tracking ID
                label = f"ID {track_id}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        output_video.write(frame)

    cap.release()
    output_video.release()
    cv2.destroyAllWindows()


video_scan(args.video)
