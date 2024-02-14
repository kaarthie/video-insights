from webcolors import rgb_to_name
from ultralytics import YOLO
import cv2
import face_recognition
import math
import time
import os


from webcolors import CSS3_NAMES_TO_HEX, hex_to_rgb

# Calculate color difference
def color_difference(color1, color2):
    return sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2))

def find_closest_color_name(rgb_value):
    closest_color = min(CSS3_NAMES_TO_HEX.items(), key=lambda x: color_difference(hex_to_rgb(x[1]), rgb_value))
    return closest_color[0]

# rgb_value = (129, 149, 145)  # Example RGB value
# closest_color_name = find_closest_color_name(rgb_value)
# print(f"Closest color name: {closest_color_name}")


classNames = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat", "traffic light", 
    "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", 
    "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", 
    "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", 
    "tennis racket", "bottle-non bio-degradable", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", 
    "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", 
    "chair", "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse", 
    "remote", "keyboard", "cell phone - non", "microwave", "oven", "toaster", "sink", "refrigerator", "book", 
    "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush", "hair brush", "banner", "blanket", 
    "branch", "bridge", "building-other", "bush", "cabinet", "cage", "cardboard", "carpet", "ceiling-other", 
    "ceiling-tile", "cloth", "clothes", "clouds", "counter", "cupboard", "curtain", "desk-stuff", "dirt", 
    "door-stuff", "fence", "floor-marble", "floor-other", "floor-stone", "floor-tile", "floor-wood", "flower", "fog", 
    "food-other", "fruit", "furniture-other", "grass", "gravel", "ground-other", "hill", "house", "leaves", 
    "light", "mat", "metal", "mirror-stuff", "moss", "mountain", "mud", "napkin", "net", "paper", 
    "pavement", "pillow", "plant-other", "plastic", "platform", "playingfield", "railing", "railroad", "river", 
    "road", "rock", "roof", "rug", "salad", "sand", "sea", "shelf", "sky-other", "skyscraper", 
    "snow", "solid-other", "stairs", "stone", "straw", "structural-other", "table", "tent", "textile-other", 
    "towel", "tree", "vegetable", "wall-brick", "wall-concrete", "wall-other", "wall-panel", "wall-stone", "wall-tile", 
    "wall-wood", "water-other", "waterdrops", "window-blind", "window-other", "wood"]

def load_known_faces(directory):
    known_faces = {}
    for filename in os.listdir(directory):
        if filename.endswith(".jpg"):
            name = os.path.splitext(filename)[0]
            image_path = os.path.join(directory, filename)
            image = face_recognition.load_image_file(image_path)
            face_encoding = face_recognition.face_encodings(image,num_jitters=10)[0]
            known_faces[name] = face_encoding
    return known_faces

def detect_persons_with_faces(img, model, known_faces, confidence_threshold=0.8):
    results = model(img, stream=True)

    for r in results:
        boxes = r.boxes

        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])

            if confidence > confidence_threshold and classNames[cls] == "person":
                frame = img[y1:y2, x1:x2]
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame, number_of_times_to_upsample=2)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, num_jitters=10)

                for face_encoding, face_location in zip(face_encodings, face_locations):
                    matches = face_recognition.compare_faces(list(known_faces.values()), face_encoding, tolerance=0.4)
                    name = "Unknown" if not any(matches) else list(known_faces.keys())[matches.index(True)]

                    top, right, bottom, left = face_location
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    print("Frame:",(left,top),(right,bottom))
                    try:
                        (b,g,r)=frame[(right+left)//2,bottom+50]
                        color_name = find_closest_color_name((b,g,r))
                        cv2.rectangle(frame, ((right+left)//2, bottom+50), ((right+left)//2, bottom+50), (128, 128, 128), 2)
                        print(color_name)
                    except:
                        print("color not found")
    return img

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    known_faces_directory = "images"
    known_faces = load_known_faces(known_faces_directory)

    model = YOLO("yolov8n.pt")
    prev =0 

    while True:
       
        success, img = cap.read()
      

        img_with_faces = detect_persons_with_faces(img, model, known_faces)

        cv2.imshow('Webcam', img_with_faces)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
