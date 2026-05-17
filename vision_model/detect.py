import cv2
# from environment.state_parser import parse_state

def live_agent_vision_loop(camera_index=1):
    cap = cv2.VideoCapture(camera_index)
    
    # Force MJPEG to prevent capture card bandwidth lag
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Crop out HDMI letterboxing here if necessary
        # pixel_7_screen = frame[:, start_x:end_x] 

        # 2. Run inference (YOLO / MobileNet / etc.)
        # results = my_vision_model(pixel_7_screen)

        # 3. Parse state and trigger CZN action
        # current_state = parse_state(results)
        
        cv2.imshow("CZN Eye - Live Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Start the loop
    live_agent_vision_loop(camera_index=1)