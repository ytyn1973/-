import cv2
import numpy as np

#frameWidth = 1920
#frameHeight = 1080
cap = cv2.VideoCapture(0)
#cap.set(3, frameWidth)
#cap.set(4, frameHeight)

def empty(a):
    pass

cv2.namedWindow("Parameters")
cv2.resizeWindow("Parameters",640,240)
cv2.createTrackbar("Threshold1","Parameters",150,255,empty)
cv2.createTrackbar("Threshold2","Parameters",120,255,empty)
cv2.createTrackbar("Area","Parameters",2298,30000,empty)

def getContours(img,imgContour):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:`
        area = cv2.contourArea(cnt)
        areaMin = cv2.getTrackbarPos("Area", "Parameters")
        if area > areaMin:
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 255), 7)
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            print(len(approx))
            x , y , w, h = cv2.boundingRect(approx)
            cv2.rectangle(imgContour, (x , y ), (x + w , y + h ), (0, 255, 0), 5)

            cv2.putText(imgContour, "Points: " + str(len(approx)), (x + w + 20, y + 20), cv2.FONT_HERSHEY_COMPLEX, .7,
                        (0, 255, 0), 2)
            if int(len(approx))==6 or int(len(approx))==5 or int(len(approx))==7:
                img_with_text=cv2.putText(imgContour, "Type: " + "Lock-Lock", (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0, 255, 0), 2)
            if int(len(approx))>=8:
                img_with_text=cv2.putText(imgContour, "Type: " + "Cola", (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0, 255, 0), 2)
            # cv2.putText(imgContour, "Area: " + str(int(area)), (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX, 0.7,
                        #(0, 255, 0), 2)
    cv2.imshow("Result", img_with_text)
while True:
    success, img = cap.read()
    imgContour = img.copy()
    imgBlur = cv2.GaussianBlur(img, (7, 7), 1)#高斯模糊
    imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)
    threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters")
    threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")
    imgCanny = cv2.Canny(imgGray,150,120)#边缘检测
    kernel = np.ones((5, 5))
    imgDil = cv2.dilate(imgCanny, kernel, iterations=1)#膨胀操作
    getContours(imgDil,imgContour)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break