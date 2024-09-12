import cv2
import numpy as np
def empty(a):
    pass
cv2.namedWindow("Parameters")
cv2.resizeWindow("Parameters",640,240)
cv2.createTrackbar("Threshold","Parameters",0,40,empty)
#导入两个函数库
def cnt_area(cnt):
    area=cv2.contourArea(cnt)
    return area
#构造一个计算轮廓面积的函数
def GetGontours():
#实现图形识别功能的主函数
    #1、根据二值图找到轮廓
    #tryexcept语言可以保证在识别不到轮廓的情况下不中止程序，而是等待直到能识别到轮廓
    try:
        contours, hierarchy = cv2.findContours(dst1,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # 轮廓      层级      # #轮廓检索模式(推荐此)  轮廓逼近方法
        contours = list(contours)
    #因为contours是元组没有sort属性，将其转换为list
        contours.sort(key=cnt_area, reverse=True)

        #对轮廓进行排序以找到最大轮廓，第一个参数是比较依据，Ture表示从大到小
        # 2、画出轮廓
        dst=cv2.drawContours(img, contours, 1, (11, 210, 255), 5)
        #                           轮廓     第几个(默认-1：所有)   颜色       线条厚度
        cnt=contours[0]
    #cnt为提取的第一个轮廓
        peri=cv2.arcLength(cnt,True)
        x = cv2.getTrackbarPos("Threshold", "Parameters")
        approx=cv2.approxPolyDP(cnt,x*peri*0.01,True)
        #第二项为阈值，通过调节它来控制精度
        print(len(approx))
        if len(approx)==4:
            print("juxing")
        else :
            print("cicle")
        cv2.imshow("dst", dst)
    except:
        print("No contours found.")

if __name__ == "__main__":


    #down_width = 750
    #down_height = 500
    #down_points = (down_width, down_height)#调控图片的大小
    #img2 = cv2.resize(img1, down_points, interpolation=cv2.INTER_LINEAR)#缩放图像
    cap = cv2.VideoCapture(0)
    while True:
        ret, img2 = cap.read()
        img = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)#变灰
        t,dst1 = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)#二值化
        GetGontours()

        # 按'q'键退出摄像头捕捉
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
# 释放摄像头资源
cap.release()
cv2.waitKey(0)
cv2.destroyAllWindows()