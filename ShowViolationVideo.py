# Open the video file
import cv2
from ultralytics import YOLO
import intersect_human_car as IHC
import torch

device: str = "cuda" if torch.cuda.is_available() else "cpu"

video_path = "C:/Users/Venya/OneDrive/Документы/Универ/Хакатон_ПДД/test_yolo/challenge.mp4"

def loadVideo(video_path):
    modelDetect = YOLO('ViolationDetect_with_YOLO/detection.pt')
    modelDetect.to(device)

    modelSegmentLines = YOLO('ViolationDetect_with_YOLO/segmentLines.pt')
    modelSegmentLines.to(device)

    modelSegmentCross = YOLO('ViolationDetect_with_YOLO/segmentCrosswalk.pt')
    modelSegmentCross.to(device)

    cap = cv2.VideoCapture(video_path)

    FindViolationInVideo(cap,modelDetect,modelSegmentLines,modelSegmentCross)

def check_successLightCross(list1, list2):
    # Проверяем, что элементы 1 и 2 из list1 точно присутствуют в list2
    if all(x in list2 for x in [list1[0], list1[1]]):
        # Проверяем, что хотя бы один из крайних элементов list1 есть в list2
        if list1[0] in list2 or list1[-1] in list2:
            return True
    return False

def find_indexes_crossHumans(list2):
    """Находит индексы элементов 'crosswalk' и 'humans' в list2"""
    cross_indexes = [i for i, x in enumerate(list2) if x == "crosswalk"]
    humans_indexes = [i for i, x in enumerate(list2) if x == "humans"]
    return cross_indexes, humans_indexes

def find_indexes_solidCar(list2):
    """Находит индексы элементов 'car' и 'solid_white' в list2"""
    car_indexes = [i for i, x in enumerate(list2) if x == "car"]
    solid_white_indexes = [i for i, x in enumerate(list2) if x == "solid_white"]
    return car_indexes, solid_white_indexes

def get_coordinates(indexes, list3):
    """Получает координаты элементов по их индексам в list3"""
    coordinates = [list3[i] for i in indexes]
    return coordinates

def check_intersection(coord1, coord2):
    """Проверяет пересечение двух прямоугольников по их координатам"""
    x1, y1, x2, y2 = coord1
    x3, y3, x4, y4 = coord2
    return not (x2 < x3 or x1 > x4 or y2 < y3 or y1 > y4)
   
def FindViolationInVideo(cap,modelDetect,modelSegmentLines,modelSegmentCross):
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    out = cv2.VideoWriter('instance-segmentation.avi', cv2.VideoWriter_fourcc(*'MJPG'), fps, (w, h))
    # Loop through the video frames
    while cap.isOpened():
    # Read a frame from the video
        success, frame = cap.read()

        if success:
            # Run YOLOv8 inference on the frame
            resultsDetect = modelDetect(frame)
            resultsSegLine = modelSegmentLines(frame)
            resultsSegCross = modelSegmentCross(frame)

            annotated_frame_detect = resultsDetect[0].plot()

            if annotated_frame_detect is not None:
                resultDetect = resultsDetect[0]
                classes = []
                coordinates = []
                
                for box in resultDetect.boxes:
                    class_id = resultDetect.names[box.cls[0].item()] #получаем имена классов
                    cords = box.xyxy[0].tolist()
                    cords = [round(x) for x in cords] #координаты найденного объекта
                    classes.append(class_id)
                    coordinates.append(cords)

                # Extract bounding boxes, classes, object names, confidence scores, and mask
                boxes = resultsSegLine[0].boxes.xyxy.tolist()
                clasSes = resultsSegLine[0].boxes.cls.tolist()
                
                # Iterate through each detected object's box, class, confidence, and mask
                for box, cls in zip(boxes, clasSes):
                    box = [round(x) for x in box]
                    if(cls == 1):
                        classes.append("solid_white")
                        coordinates.append(box)

                boxes = resultsSegCross[0].boxes.xyxy.tolist()
                clasSes = resultsSegCross[0].boxes.cls.tolist()

                # Iterate through each detected object's box, class, confidence, and mask
                for box, cls in zip(boxes, clasSes):
                    box = [round(x) for x in box]
                    classes.append("crosswalk")
                    coordinates.append(box)

                    print("Box:",coordinates)
                    print("Class:",classes)

                #1) проверка на переход пешеходом на красный свет (без разницы какого светофора)
                selected_classes = ["crosswalk","humans","red_pedestrian_light","red_traffic_light"]
                if(check_successLightCross(selected_classes,classes)):
                    # Находим индексы элементов 'crosswalk' и 'humans' в list2
                    cross_indexes, humans_indexes = find_indexes_crossHumans(classes)

                    # Получаем координаты элементов 'crosswalk' и 'humans' из list3
                    cross_coordinates = get_coordinates(cross_indexes, coordinates)
                    humans_coordinates = get_coordinates(humans_indexes, coordinates)

                    # Проверяем пересечение координат 'crosswalk' и 'humans'
                    if check_intersection(cross_coordinates[0], humans_coordinates[0]):
                        print("Нарушение! Зафиксирован переход пешеходом на красный свет")


                #2) проверка на проезд машины на красный    
                selected_classes = ["car", "red_traffic_light"]
                if (all(ele in classes for ele in selected_classes)) :
                    print ("Нарушение! Машина проехала на красный свет")
                

                #3) машина не пропускает пешехода хотя горит зелёный свет
                selected_classes = ["car","crosswalk","green_pedestrian","humans"]
                if (all(ele in classes for ele in selected_classes)) :
                    # Находим индексы элементов list1 в list2
                    indexes = IHC.find_indexes(selected_classes, classes)

                    # Получаем координаты элементов "car", "crosswalk" и "humans" из list3
                    coordinates = IHC.get_coordinates(indexes, coordinates)

                    # Проверяем пересечение координат всех трех элементов
                    if check_intersection(coordinates["car"], coordinates["crosswalk"], coordinates["humans"]):
                        print("Нарушение! Не пропустил пешехода.")
                
                    
                #4) машина пересекла сплошную
                selected_classes = ["car", "solid_white"]
                if all(ele in classes for ele in selected_classes):
                    car_indexes, solid_white_indexes = find_indexes_solidCar(classes)

                    car_coordinates = get_coordinates(car_indexes, coordinates)
                    solid_white_coordinates = get_coordinates(solid_white_indexes, coordinates)

                    if check_intersection(car_coordinates[0], solid_white_coordinates[0]):
                        print("Нарушение! Пересечение сплошной")


                #5) машина остановилась у знака "парковка запрещена"
                selected_classes = ["car","stop_sign"]
                if (all(ele in classes for ele in selected_classes)) :
                    print("Нарушение! Остановка у знака 'остановка запрещена'!")
                    # Visualize the results on the frame
                
                
                out.write(annotated_frame_detect)
            # Display the annotated frame
            #cv2.imshow("YOLOv8 Inference", annotated_frame_detect)

            # Break the loop if 'q' is pressed
            # if cv2.waitKey(1) & 0xFF == ord("q"):
            #     break
        else:
            # Break the loop if the end of the video is reached
            break

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()

if __name__=="__main__":
    loadVideo(video_path)