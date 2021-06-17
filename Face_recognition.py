import cv2
import sys
import dlib
from Face_train import Model
from imutils import face_utils
from scipy.spatial import distance as dist
from tkinter import messagebox
import datetime
import xlwt

counts = 0

frame_counter = 0
blink_counter = 0

EYE_AR_THRESH = 0.23
EYE_AR_CONSEC_FRAMES = 3

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

def set_style(name,height,bold=False):
    style = xlwt.XFStyle()  # 初始化样式

    font = xlwt.Font()  # 为样式创建字体
    font.name = name # 'Times New Roman'
    font.bold = bold
    font.color_index = 4
    font.height = height

    borders= xlwt.Borders()
    borders.left= 6
    borders.right= 6
    borders.top= 6
    borders.bottom= 6

    style.font = font
    style.borders = borders

    return style

def write_excel():

    # 创建工作簿
    global f
    f = xlwt.Workbook(encoding = "utf-8")

    # 创建sheet
    global sheet1
    sheet1 = f.add_sheet(u'sheet1',cell_overwrite_ok=True)
    row0 = [u'name',u'state',u'audit_dt',u'cre_Dt']



def Record():
    global counts
    sheet1.write(counts,0,'Yizihao')
    sheet1.write(counts,1,'1')
    sheet1.write(counts,2,ow_time)
    sheet1.write(counts,3,ow_time)
    f.save('Attendance.xls') #保存文件
    counts += 1

# 计算眼睛横纵比
def eye_aspect_ratio(eye):

    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # 计算眼睛横纵比
    C = dist.euclidean(eye[0], eye[3])

    # 计算眼睛横纵比
    ear = (A + B) / (2.0 * C)

    # return the eye aspect ratio
    return ear


# 眨眼检测
def Blink_check(gray):
    rects = detector(gray, 0)
    global blink_counter
    global frame_counter

    for rect in rects:

        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)


        ear = (leftEAR + rightEAR) / 2.0

        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        if ear < EYE_AR_THRESH:
            frame_counter += 1

        else:
            if frame_counter >= EYE_AR_CONSEC_FRAMES:
                blink_counter += 1
            frame_counter = 0

        # 显示总眨眼次数
        cv2.putText(frame, "Blinks: {}".format(blink_counter), (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "COUNTER: {}".format(frame_counter), (140, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


model = Model()
model.load_model(file_path='E:\model\Yizihao.face.model.h5')


if __name__ == '__main__':
    ow_time = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    write_excel()
    if len(sys.argv) != 1:
        print("Usage:%s camera_id\r\n" % (sys.argv[0]))
        sys.exit(0)
        Load_model()


    # 框住人脸的矩形边框颜色
    color = (0, 255, 0)

    # 捕获指定摄像头的实时视频流
    cap = cv2.VideoCapture(0)

    # 人脸识别分类器本地存储路径
    cascade_path = "haarcascade_frontalface_default.xml"

    # 循环检测识别人脸
    while True:
        ret, frame = cap.read()  # 读取一帧视频

        if ret is True:

            # 图像灰化，降低计算复杂度
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            continue
        # 使用人脸识别分类器，读入分类器
        cascade = cv2.CascadeClassifier(cascade_path)

        # 利用分类器识别出哪个区域为人脸
        faceRects = cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3, minSize=(32, 32))
        if len(faceRects) > 0:
            for faceRect in faceRects:
                x, y, w, h = faceRect

                # 截取脸部图像提交给模型识别这是谁
                image = frame[y - 10: y + h + 10, x - 10: x + w + 10]

                global faceID
                faceID = model.face_predict(image)

                # 如果是“Yizihao”
                if faceID == 0:
                    cv2.rectangle(frame, (x - 10, y - 10), (x + w + 10, y + h + 10), color, thickness=2)
                    global name
                    name = 'Yizihao'
                    # 文字提示
                    cv2.putText(frame, 'Yizihao',
                                (x + 30, y + 30),  # 坐标
                                cv2.FONT_HERSHEY_SIMPLEX,  # 字体
                                1,  # 字号
                                (255, 0, 255),  # 颜色
                                2)  # 字的线宽
                    # 眨眼检测
                    Blink_check(gray)
                    cv2.putText(frame, "Please blink four times", (300, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (33, 12, 215), 2)


                else:
                    pass
        if blink_counter >= 4:
            messagebox.showinfo("提示","签到成功！")
            Record()
            break

        cv2.imshow("识别", frame)

        # 等待10毫秒看是否有按键输入
        k = cv2.waitKey(10)
        # 如果输入q则退出循环
        if k & 0xFF == ord('q'):
            break

    # 释放摄像头并销毁所有窗口
    cap.release()
    cv2.destroyAllWindows()
