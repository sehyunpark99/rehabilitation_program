import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

video_path = '01.mp4'
cap = cv2.VideoCapture(video_path)

#Save results
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') 
out = cv2.VideoWriter('%s_output.mp4' % (video_path.split('.')[0]), fourcc, cap.get(cv2.CAP_PROP_FPS), (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

#Pose model (33 landmarks extraction)
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=2) #complexity = 0, 1, 2 (2=> more sophisticated results)

is_first = True # 어드레스 시 첫 프레임을 받아오기 위한 플래그
# 어드레스 시 첫 프레임의 좌표를 저장할 변수
#Reference = face coordinates and radius
first_center_x, first_center_y, first_radius = None, None, None

while cap.isOpened():
    ret, img = cap.read() #read frame
    if not ret:
        break

    img_h, img_w, _ = img.shape #image height and width

    img_result = img.copy() #for the results

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #BGR to RGB 
    results = pose.process(img) #pose porcessing for getting results

    mp_drawing.draw_landmarks(  #landmark  drawings as a result
        img_result,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
    
    #When landmarks extracted, we will get the size of face
    if results.pose_landmarks:
        # https://google.github.io/mediapipe/solutions/pose.html#pose-landmark-model-blazepose-ghum-3d
        landmark = results.pose_landmarks.landmark

        left_ear_x = landmark[mp_pose.PoseLandmark.LEFT_EAR].x * img_w #need to multiply as landmark give percentage in 0~255
        left_ear_y = landmark[mp_pose.PoseLandmark.LEFT_EAR].y * img_h #we need to change it to pixel

        right_ear_x = landmark[mp_pose.PoseLandmark.RIGHT_EAR].x * img_w 
        right_ear_y = landmark[mp_pose.PoseLandmark.RIGHT_EAR].y * img_h

        center_x = int((left_ear_x + right_ear_x) / 2)
        center_y = int((left_ear_y + right_ear_y) / 2)

        radius = int((left_ear_x - right_ear_x) / 2)
        radius = max(radius, 20)  #min of radius to 20 pixels

        if is_first: # 어드레스 시 첫 프레임의 머리 좌표 저장
            first_center_x = center_x
            first_center_y = center_y
            first_radius = int(radius * 2) 

            is_first = False
        else:
            cv2.circle(img_result, center=(first_center_x, first_center_y),
                radius=first_radius, color=(0, 255, 255), thickness=2)

            color = (0, 255, 0) # 초록색

            # 머리가 원래 위치보다 많이 벗어난 경우
            if center_x - radius < first_center_x - first_radius \
                or center_x + radius > first_center_x + first_radius:
                color = (0, 0, 255) # 빨간색

            cv2.circle(img_result, center=(center_x, center_y),
                radius=radius, color=color, thickness=2)

    cv2.imshow('Pose Guide', img_result)
    out.write(img_result)

    if cv2.waitKey(1) == ord('q'):
        break

pose.close()
cap.release()
out.release()
