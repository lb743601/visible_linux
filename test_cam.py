import cv2

cap = cv2.VideoCapture("/dev/video0")

# 设置摄像头分辨率
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)

if not cap.isOpened():
    print("无法打开摄像头")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("无法读取帧")
        break

    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray=frame
    # print(gray.shape)
    # 显示灰度图像
    cv2.imshow("Gray Image", gray)

    # 按下'q'键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
