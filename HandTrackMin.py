import cv2 as cv2
import mediapipe as mp
import time
import pyautogui

pyautogui.FAILSAFE = False

cap = cv2.VideoCapture(1)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

pinching = False

average_points = []

def average_point():
    final_x = 0
    final_y = 0
    for point in average_points:
        final_x += point[0]
        final_y += point[1]
    final_x = final_x / len(average_points)
    final_y = final_y / len(average_points)
    return (final_x, final_y)

def pinch_event(x, y):
    print("person pinched their fingers")
    print("x: ", x)
    print("y: ", y)
    pyautogui.click(x, y)

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    # print(results.multi_hand_landmarks)

    # if escape key is pressed, break out of loop
    if cv2.waitKey(1) & 0xFF == 27:
        break

    # get 4th point in results.multi_hand_landmarks
    if results.multi_hand_landmarks:
        handLms = results.multi_hand_landmarks[0]

        mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
        thumb_tip = handLms.landmark[4]
        pointer_tip = handLms.landmark[8]

        # find point that averages the x and y coordinates of the thumb and pointer finger
        x = (thumb_tip.x + pointer_tip.x) / 2
        y = (thumb_tip.y + pointer_tip.y) / 2

        # remove first element of average_points if it has more than 10 elements
        if len(average_points) > 5:
            average_points.pop(0)

        # add new point to average_points
        average_points.append((x, y))
        avg_pt = average_point()

        pad_edges_x = avg_pt[0] * 1.2 - 0.1
        pad_edges_y = avg_pt[1] * 1.2 - 0.1

        # move mouse to thumb tip
        pyautogui.moveTo(1920 - pad_edges_x * 1920, pad_edges_y * 1080,)

        # check if the points are within a certain range
        range = 0.07

        color = (255, 0, 0)

        if thumb_tip.x > pointer_tip.x - range and thumb_tip.x < pointer_tip.x + range:
            if thumb_tip.y > pointer_tip.y - range and thumb_tip.y < pointer_tip.y + range:
                pinch_event(1920 - pad_edges_x * 1920, pad_edges_y * 1080)
                pinching = True
            else:
                pinching = False
        else:
            pinching = False

        if pinching == True:
            color = (0, 255, 0)

        # draw a large dot at the 4th point
        cv2.circle(img, (int(thumb_tip.x * 640), int(thumb_tip.y * 480)), 10, color, cv2.FILLED)
        # draw a small dot at the 8th point
        cv2.circle(img, (int(pointer_tip.x * 640), int(pointer_tip.y * 480)), 10, color, cv2.FILLED)
        # draw a small dot at the 8th point
        cv2.circle(img, (int(x * 640), int(y * 480)), 5, (255, 255, 255), cv2.FILLED)

        # draw a small dot at the avg_pt point
        cv2.circle(img, (int(avg_pt[0] * 640), int(avg_pt[1] * 480)), 5, (100, 100, 100), cv2.FILLED)



    cv2.imshow("Image", img)
    cv2.waitKey(1)

# close the program
cap.release()