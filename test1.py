OPENCV_VIDEOIO_PRIORITY_MSMF =0
import cv2

cap = cv2.VideoCapture(0)
        # cap.open(cv2.CAP_ANY, cv2.CAP_FFMPEG)  # Use FFMPEG backend with CAP_ANY
        # cap.set(cv2.CAP_PROP_FPS, 30)  # You may need to adjust the frames per second based on your video's frame rate

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Process the frame as needed
    cv2.imshow("video",frame)

    # # Break the loop if the 'q' key is pressed
    # if cv2.waitKey(30) & 0xFF == ord('q'):
    #     break

# Close the video capture
cap.release()
cv2.destroyAllWindows()
# plt.close()
