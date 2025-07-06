import socket
import cv2
import math
import mediapipe as mp

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = '' # Replace with your server's IP address
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    #print(client.recv(2048).decode(FORMAT))







cap = cv2.VideoCapture(0)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 
height  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) 
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5)

tipIds = [4, 8, 12, 16, 20]

gesture = ""

# Define a function to count fingers
def countFingers(image, hand_landmarks, hand_label):
    global gesture
    cv2.putText(image,"Your Current Gesture" + gesture,(75,90),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)
    if hand_landmarks:

		# Get all Landmarks of the FIRST Hand VISIBLE
        landmarks = hand_landmarks[0].landmark
        
        # Count Fingers        
        fingers = []

        for lm_index in tipIds:
            # Get Finger Tip and Bottom y Position Value
            finger_tip_y = landmarks[lm_index].y 
            finger_bottom_y = landmarks[lm_index - 2].y

            # Check if ANY FINGER is OPEN or CLOSED
            if lm_index !=4:
                if finger_tip_y < finger_bottom_y:
                    fingers.append(1)


                if finger_tip_y > finger_bottom_y:
                    fingers.append(0)

        totalFingers = fingers.count(1)

        # shoot
        finger_tip_x = int((landmarks[8].x)*width)
        finger_tip_y = int((landmarks[8].y)*height)

        thumb_tip_x = int((landmarks[4].x)*width)
        thumb_tip_y = int((landmarks[4].y)*height)
        
        # Draw a LINE between FINGER TIP and THUMB TIP
        cv2.line(image, (finger_tip_x, finger_tip_y), (thumb_tip_x, thumb_tip_y), (255, 0 , 0), 2)


        # Calculate DISTANCE between FINGER TIP and THUMB TIP
        distance = math.sqrt(((finger_tip_x - thumb_tip_x)**2)+((finger_tip_y - thumb_tip_y)**2))
        
        
       

        fingers_folded = 0

         # Tip and pip landmark indices (thumb, index, middle, ring, pinky)
       

       
                
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]

        if hand_label == "Left":
            if thumb_tip.x > thumb_ip.x:  # Thumb folded inward
                fingers_folded += 1
        elif hand_label == "Right":
            if thumb_tip.x < thumb_ip.x:  # Thumb folded inward
                fingers_folded += 1

        
        if(fingers_folded==0 and totalFingers==0):
            if(gesture!="block"):
                gesture="block"
                print("Your Current Gesture " + gesture)
        if(distance>=150 and totalFingers <=2): #shoot open
            if(gesture!="shoot"):
                gesture="shoot"
                print("Your Current Gesture" + gesture)
                
        if(totalFingers==0 and fingers_folded==1): #reload
            if(gesture!="reload"):
                gesture="reload"
                print("Your Current Gesture " + gesture)
        
    
        
       
            

        


# Define a function to 
def drawHandLanmarks(image, hand_landmarks):
    
    # Darw connections between landmark points
    if hand_landmarks:

      for landmarks in hand_landmarks:
               
        mp_drawing.draw_landmarks(image, landmarks, mp_hands.HAND_CONNECTIONS)


def record():
    cap = cv2.VideoCapture(0)
    while True:
        success, image = cap.read()
        
        image = cv2.flip(image, 1)

        # Detect the Hands Landmarks 
        results = hands.process(image)
        
        
        # Get landmark position from the processed result
        hand_landmarks = results.multi_hand_landmarks
        if results.multi_hand_landmarks and results.multi_handedness:
            hand_landmarks = results.multi_hand_landmarks
            hand_label = results.multi_handedness[0].classification[0].label  # 'Left' or 'Right'
            countFingers(image, hand_landmarks, hand_label)
            drawHandLanmarks(image, hand_landmarks)

        cv2.imshow("Media Controller", image)
        
        # Quit the window on pressing Spacebar key
        key = cv2.waitKey(1)
        if key == 27:
            break
def get_gesture():
    global gesture
    gesture = ""
    record()
    cap.release()
    cv2.destroyAllWindows()
    return gesture
def recv_msg():
    msg_length = client.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length.strip())
        return client.recv(msg_length).decode(FORMAT)
    return ""
def main():
    global gesture
    while True:
        msg = recv_msg()
        if(msg == "round"):
            gesture = get_gesture()
            if gesture:
                send(gesture)
        elif(msg == str(socket.gethostbyname(socket.gethostname()))):
            print("You have Won")
            break
        else:
            print("You Lost")
            break

    client.close()
main()
