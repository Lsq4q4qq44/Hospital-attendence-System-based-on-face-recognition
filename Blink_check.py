from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import imutils
import time
import dlib
import cv2


def eye_aspect_ratio(eye):
    # 计算两组垂直眼点（x，y）坐标之间的欧氏距离
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    # 计算眼睛横纵比
    C = dist.euclidean(eye[0], eye[3])
    # 计算眼睛横纵比
    ear = (A + B) / (2.0 * C)
    return ear

# 定义两个常数，一个用于表示眨眼的眼睛纵横比，然后为连续帧数定义第二个常数眼睛必须低于阈值
EYE_AR_THRESH = 0.23
EYE_AR_CONSEC_FRAMES = 3

# 初始化帧计数器和闪烁总数
blink_counter = 0
frame_counter = 0

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("E:\MyCode\\blink\shape_predictor_68_face_landmarks.dat")

# 分别获取左眼和右眼的面部标志的索引
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# start the video stream thread
print("[INFO] starting video stream thread...")

fileStream = True
vs = VideoStream(src=0).start()

fileStream = False
time.sleep(1.0)

# 从视频流循环检测
while True:
    # if this is a file video stream, then we need to check if
    #  there any more frames left in the buffer to process
    if fileStream and not vs.more():
        break

    frame = vs.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 检测灰框中的人脸
    rects = detector(gray, 0)

    # loop over the face detections
    for rect in rects:
        # 确定面部区域的面部地标，然后将面部地标（x，y）坐标转换为NumPy数组
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

    # 提取左眼和右眼坐标，然后使用坐标计算双眼的眼宽比
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        # 平均双眼的眼宽比
        ear = (leftEAR + rightEAR) / 2.0

        # 计算左眼和右眼的凸包，然后可视化每只眼睛
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        # 检查眼睛纵横比是否低于闪烁阈值，如果低于，则增加闪烁帧计数器
        if ear < EYE_AR_THRESH:
            frame_counter += 1

        # 否则，眼睛纵横比不低于眨眼阈值
        else:
            # 如果眼睛闭了足够的时间，则增加眨眼的总次数
            if frame_counter >= EYE_AR_CONSEC_FRAMES:
                blink_counter += 1
            frame_counter = 0

        # 显示总眨眼次数
        # 为帧计算的眼睛纵横比
        cv2.putText(frame, "Blinks: {}".format(blink_counter), (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "COUNTER: {}".format(frame_counter), (140, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

# 销毁所有窗口
cv2.destroyAllWindows()
vs.stop()
