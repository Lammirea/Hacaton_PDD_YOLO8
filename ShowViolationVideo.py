# Open the video file
import cv2
from ultralytics import YOLO

video_path = "C:/Users/Venya/OneDrive/Документы/Универ/Хакатон_ПДД/test_yolo/000002.mp4"
def loadVideo(video_path):

    cap = cv2.VideoCapture(video_path)
   
    frame_width = int(cap.get(3)) 
    frame_height = int(cap.get(4)) 
   
    size = (frame_width, frame_height) 
   
    result = cv2.VideoWriter("output.avi",  
                         cv2.VideoWriter_fourcc(*'MJPG'), 
                         10, size) 
    
    FindViolationInVideo(cap,result)
    
def FindViolationInVideo(cap,result):

    model = YOLO('ViolationDetect_with_YOLO/models/detection/train4/weights/best.pt')

    # Loop through the video frames
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()

        if success:
            # Run YOLOv8 inference on the frame
            results = model(frame)

            # Visualize the results on the frame
            annotated_frame = results[0].plot()
            result.write(annotated_frame) 
                       
        else:
            # Break the loop if the end of the video is reached
            break

    # Release the video capture object and close the display window
    cap.release()
    result.release()

if __name__=="__main__":
    loadVideo(video_path)