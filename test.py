import cv2
print("Installed")

img = cv2.imread("photos/subash.jpg")
img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
imgGrey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
imgBlur = cv2.GaussianBlur(imgGrey , (7,7), 0)
imgCanny = cv2.Canny(img, 100, 100)
cv2.imshow("Output1", imgCanny)
# cv2.imshow("Output2", imgGrey)
# cv2.imshow("Output3", imgBlur)
cv2.waitKey(0)

# cap = cv2.VideoCapture(0)
# while True:
#     success, img = cap.read()
#     cv2.imshow("Video", img)
#     if(cv2.waitKey(10) & 0xFF ==ord('q')):
#         break