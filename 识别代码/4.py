# -- coding: utf-8 --
 
import sys
import threading
import os
import termios
import time
import cv2
import numpy as np
from ctypes import *
import serial
import struct

 
sys.path.append("/opt/MVS/Samples/aarch64/Python/MvImport")
from MvCameraControl_class import *
ser = serial.Serial('/dev/ttyTHS2', 115200)#创造一个串口对象，指定端口号和波特率
g_bExit = False#用于控制和退出
def empty(a):
    pass
img_w=1280#宽度
img_h=1024#高度
img_c=3#通道数

def getContours(img,imgContour):#获取轮廓，并在另一图像上绘制
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)#找出所有轮廓和层次（只检测最外层，保留所有点）
    for cnt in contours:#遍历
        area = cv2.contourArea(cnt)
        if area > 4000:
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 255), 7)
            peri = cv2.arcLength(cnt, True)#周长
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)#多边形拟合
            if int(len(approx))==6 or int(len(approx))==5 or int(len(approx))==7:
                print('recentage')
                date = struct.pack('1s', b'\x11')
                ser.write(date)
       #         img_with_text=cv2.putText(imgContour, "Type: " + "Lock-Lock", (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0, 255, 0), 2)
            if int(len(approx))>=8:
                print('cicle')
                date = struct.pack('1s', b'\x01')#通讯
                ser.write(date)
     #           img_with_text=cv2.putText(imgContour, "Type: " + "Cola", (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0, 255, 0), 2)
            # cv2.putText(imgContour, "Area: " + str(int(area)), (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX, 0.7,
                        #(0, 255, 0), 2)
    cv2.imshow("Result",imgContour)

# 源程序-为线程定义一个函数
def work_thread(cam=0, pData=0, nDataSize=0):
    stFrameInfo = MV_FRAME_OUT_INFO_EX()
    memset(byref(stFrameInfo), 0, sizeof(stFrameInfo))
    while True:
        ret = cam.MV_CC_GetOneFrameTimeout(pData, nDataSize, stFrameInfo, 1000)
        if ret == 0:
            pass
            #print ("get one frame: Width[%d], Height[%d], PixelType[0x%x], nFrameNum[%d]"  % (stFrameInfo.nWidth, stFrameInfo.nHeight, stFrameInfo.enPixelType,stFrameInfo.nFrameNum))
        else:
            print ("no data[0x%x]" % ret)
        if g_bExit == True:
                break
 
#opencv转换显示
def work_thread_rgb82bgr(cam=0, pData=0, nDataSize=0):
    stFrameInfo = MV_FRAME_OUT_INFO_EX()
    memset(byref(stFrameInfo), 0, sizeof(stFrameInfo))
    while True:
        ret = cam.MV_CC_GetOneFrameTimeout(pData, nDataSize, stFrameInfo, 1000)
        if ret == 0:
            print ("get one frame: Width[%d], Height[%d], PixelType[0x%x], nFrameNum[%d]"  % (stFrameInfo.nWidth, stFrameInfo.nHeight, stFrameInfo.enPixelType,stFrameInfo.nFrameNum))
            print('----', stFrameInfo.enPixelType)
            #if stFrameInfo.enPixelType=='PixelType_Gvsp_RGB8_Packed':
            temp = np.asarray(pData)#将pdate指向的数组转换为nump数组
            temp = temp.reshape((img_h, img_w, img_c))#转换成三维numpy数组
            temp = cv2.cvtColor(temp, cv2.COLOR_BGR2RGB)#转化为RGB形式
            temp = cv2.convertScaleAbs(temp, alpha=7, beta=100)#亮度对比度调节
            imgContour = temp.copy()
            cv2.namedWindow("temp", cv2.WINDOW_NORMAL)
            imgBlur = cv2.GaussianBlur(temp, (7, 7), 1)  # 高斯模糊
            imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)
            #threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters")
            #threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")
            imgCanny = cv2.Canny(imgGray, 150, 120)  # 边缘检测
            kernel = np.ones((5, 5))
            imgDil = cv2.dilate(imgCanny, kernel, iterations=1)  # 膨胀操作
            getContours(imgDil, imgContour)
            cv2.waitKey(1)
            #else:
                #print("图像输出格式不是BGR8,请先使用MVS软件设置相机默认输出图像格式为BGR8....")
        else:
            print ("no data[0x%x]" % ret)
        if g_bExit == True:
            break

 
 
 
 
 
 
def press_any_key_exit():
    fd = sys.stdin.fileno()
    old_ttyinfo = termios.tcgetattr(fd)
    new_ttyinfo = old_ttyinfo[:]
    new_ttyinfo[3] &= ~termios.ICANON
    new_ttyinfo[3] &= ~termios.ECHO
    # sys.stdout.write(msg)
    # sys.stdout.flush()
    termios.tcsetattr(fd, termios.TCSANOW, new_ttyinfo)
    try:
        os.read(fd, 7)
    except:
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, old_ttyinfo)
     
if __name__ == "__main__":
 
    SDKVersion = MvCamera.MV_CC_GetSDKVersion()
    print ("SDKVersion[0x%x]" % SDKVersion)
 
    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
     
    # ch:枚举设备 | en:Enum device
    ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
    if ret != 0:
        print ("enum devices fail! ret[0x%x]" % ret)
        sys.exit()
 
    if deviceList.nDeviceNum == 0:
        print ("find no device!")
        sys.exit()
 
    print ("Find %d devices!" % deviceList.nDeviceNum)
 
    for i in range(0, deviceList.nDeviceNum):
        mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
            print ("\ngige device: [%d]" % i)
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                strModeName = strModeName + chr(per)
            print ("device model name: %s" % strModeName)
 
            nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
            nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
            nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
            nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
            print ("current ip: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
        elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
            print ("\nu3v device: [%d]" % i)
            strModeName = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                if per == 0:
                    break
                strModeName = strModeName + chr(per)
            print ("device model name: %s" % strModeName)
 
            strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                if per == 0:
                    break
                strSerialNumber = strSerialNumber + chr(per)
            print ("user serial number: %s" % strSerialNumber)
 
    if sys.version >= '3':
        nConnectionNum = input("please input the number of the device to connect:")
    else:
        nConnectionNum = raw_input("please input the number of the device to connect:")
 
    if int(nConnectionNum) >= deviceList.nDeviceNum:
        print ("intput error!")
        sys.exit()
 
    # ch:创建相机实例 | en:Creat Camera Object
    cam = MvCamera()
     
    # ch:选择设备并创建句柄| en:Select device and create handle
    stDeviceList = cast(deviceList.pDeviceInfo[int(nConnectionNum)], POINTER(MV_CC_DEVICE_INFO)).contents
 
    ret = cam.MV_CC_CreateHandle(stDeviceList)
    if ret != 0:
        print ("create handle fail! ret[0x%x]" % ret)
        sys.exit()
 
    # ch:打开设备 | en:Open device
    ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    if ret != 0:
        print ("open device fail! ret[0x%x]" % ret)
        sys.exit()
     
    # ch:探测网络最佳包大小(只对GigE相机有效) | en:Detection network optimal package size(It only works for the GigE camera)
    if stDeviceList.nTLayerType == MV_GIGE_DEVICE:
        nPacketSize = cam.MV_CC_GetOptimalPacketSize()
        if int(nPacketSize) > 0:
            ret = cam.MV_CC_SetIntValue("GevSCPSPacketSize",nPacketSize)
            if ret != 0:
                print ("Warning: Set Packet Size fail! ret[0x%x]" % ret)
        else:
            print ("Warning: Get Packet Size fail! ret[0x%x]" % nPacketSize)
 
    # ch:设置触发模式为off | en:Set trigger mode as off
    ret = cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
    if ret != 0:
        print ("set trigger mode fail! ret[0x%x]" % ret)
        sys.exit()
 
    # ch:获取数据包大小 | en:Get payload size
    stParam =  MVCC_INTVALUE()
    memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))
     
    ret = cam.MV_CC_GetIntValue("PayloadSize", stParam)
    if ret != 0:
        print ("get payload size fail! ret[0x%x]" % ret)
        sys.exit()
    nPayloadSize = stParam.nCurValue
 
    # ch:开始取流 | en:Start grab image
    ret = cam.MV_CC_StartGrabbing()
    if ret != 0:
        print ("start grabbing fail! ret[0x%x]" % ret)
        sys.exit()
    #将PayloadSize的uint数据转为可供numpy处理的数据，后面就可以用numpy将其转化为numpy数组格式。
    data_buf = (c_ubyte * nPayloadSize)()
 
    try:
        #有些代码可能会在data_buf前面加上byteref，如果这样做的话，就会将数据转为浮点型，
        # 而opencv需要的是整型，会报错，所以这里就不需要转化了
        #hThreadHandle = threading.Thread(target=work_thread_rgb82bgr, args=(cam, byref(data_buf), nPayloadSize))
        hThreadHandle = threading.Thread(target=work_thread_rgb82bgr, args=(cam, data_buf, nPayloadSize))
        hThreadHandle.start()
        #hThreadHandle.start()
    except:
        print ("error: unable to start thread")
         
    print ("press a key to stop grabbing.")
    press_any_key_exit()
 
    g_bExit = True
    hThreadHandle.join()
 
    # ch:停止取流 | en:Stop grab image
    ret = cam.MV_CC_StopGrabbing()
    if ret != 0:
        print ("stop grabbing fail! ret[0x%x]" % ret)
        del data_buf
        sys.exit()
 
    # ch:关闭设备 | Close device
    ret = cam.MV_CC_CloseDevice()
    if ret != 0:
        print ("close deivce fail! ret[0x%x]" % ret)
        del data_buf
        sys.exit()
 
    # ch:销毁句柄 | Destroy handle
    ret = cam.MV_CC_DestroyHandle()
    if ret != 0:
        print ("destroy handle fail! ret[0x%x]" % ret)
        del data_buf
        sys.exit()
 
    del data_buf

