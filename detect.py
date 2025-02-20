#Code adapted from van Gent, P. (2016).
# Emotion Recognition Using Facial Landmarks, Python, DLib and OpenCV. A tech blog about fun things with Python and embedded electronics.
# Retrieved from: http://www.paulvangent.com/2016/08/05/emotion-recognition-using-facial-landmarks/
#Import required modules
import cv2
import dlib
import math
import numpy as np

#Dlib positions
#  ("mouth", (48, 68)),
#	("right_eyebrow", (17, 22)),
#	("left_eyebrow", (22, 27)),
#	("right_eye", (36, 42)),
#	("left_eye", (42, 48)),
#	("nose", (27, 35)),
#	("jaw", (0, 17))

#Set up some required objects
video_capture = cv2.VideoCapture(0) #Webcam object
#Change Frame Rate
video_capture.set(cv2.CAP_PROP_FPS, 30)
#Change Resolution
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320);
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 130);
detector = dlib.get_frontal_face_detector() #Face detector
#Landmark identifier. Set the filename to whatever you named the downloaded file
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

def get_top_lip_height(lip_first_id, face_landmarks):
    sum=0
    for i in range(3):
        # distance between two near points up and down
        distance = math.sqrt( (face_landmarks.part(lip_first_id + i).x - face_landmarks.part(lip_first_id + i + 11).x)**2 +
                              (face_landmarks.part(lip_first_id + i).y - face_landmarks.part(lip_first_id + i + 11).y)**2   )
        sum += distance
    return sum / 3

def get_bottom_lip_height(lip_first_id, face_landmarks):
    sum=0
    for i in range(3):
        # distance between two near points up and down
        distance = math.sqrt( (face_landmarks.part(lip_first_id + i).x - face_landmarks.part(lip_first_id + i + 9).x)**2 +
                              (face_landmarks.part(lip_first_id + i).y - face_landmarks.part(lip_first_id + i + 9).y)**2   )
        sum += distance
    return sum / 3

def get_mouth_height(mouth_first_id, face_landmarks):
    sum=0
    for i in range(3):
        # distance between two near points up and down
        distance = math.sqrt( (face_landmarks.part(mouth_first_id + i).x - face_landmarks.part(mouth_first_id + 6 - i).x)**2 +
                              (face_landmarks.part(mouth_first_id + i).y - face_landmarks.part(mouth_first_id + 6 - i).y)**2   )
        sum += distance
    return sum / 3


def is_mouth_open(face_landmarks):
    top_lip_height =  get_top_lip_height(50, face_landmarks)
    bottom_lip_height = get_bottom_lip_height(56, face_landmarks)
    mouth_height = get_mouth_height(61, face_landmarks)

    # if mouth is open more than lip height * ratio, return true.
    ratio = 1.0
    #print('top_lip_height: %.2f, bottom_lip_height: %.2f, mouth_height: %.2f, min*ratio: %.2f'
         # % (top_lip_height,bottom_lip_height,mouth_height, min(top_lip_height, bottom_lip_height) * ratio))

    if mouth_height > min(top_lip_height, bottom_lip_height) * ratio:
        return True
    else:
        return False

count_detected_frames = 0

while True:
    ret, frame = video_capture.read()
    frame = cv2.flip(frame,180)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    clahe_image = clahe.apply(gray)

    mask = np.zeros(frame.shape[:2], dtype='uint8')
    (center_x, center_y) = (frame.shape[1] // 2, frame.shape[0] // 2)
    cv2.circle(mask, (center_x, center_y), 100, 255, -1)
    masked = cv2.bitwise_and(frame, frame, mask=mask)
    clahe_image = masked

    detections = detector(clahe_image, 1) #Detect the faces in the image

    for k,d in enumerate(detections): #For each detected face
        shape = predictor(clahe_image, d) #Get coordinates
        for i in range(48,68): #There are 68 landmark points on each face
            cv2.circle(frame, (shape.part(i).x, shape.part(i).y), 1, (0,255,0), thickness=-1) #For each point, draw a red circle with thickness2 on the original frame
            #cv2.putText(frame, str(i), (shape.part(i).x,shape.part(i).y),
            #        fontFace=cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
            #        fontScale=0.3,
            #        color=(0, 0, 255))
        # Display text for mouth open / close
        ret_mouth_open = is_mouth_open(shape)
        if ret_mouth_open is True:
            count_detected_frames = count_detected_frames + 1
        else:
            count_detected_frames = 0

        if count_detected_frames > 10:
            text = 'Boca aberta'
        else:
            text = 'Abra a boca'
        cv2.putText(frame, text, (200, 420), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 255), 1)

    cv2.circle(frame,(320, 300), 70, (0,0,255), 2)
    #cv2.imshow("masked", masked)
    cv2.imshow("image", frame) #Display the frame

    if cv2.waitKey(1) & 0xFF == ord('q'): #Exit program when the user presses 'q'
        break

cv2.destroyAllWindows()
