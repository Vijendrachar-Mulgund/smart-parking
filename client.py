# importing everything we need
import cv2
import csv
import time

# Select the Video source
VIDEO_SOURCE = 1

# start the recording
cap = cv2.VideoCapture(VIDEO_SOURCE)

# Allow the camera to start (To avoid the blank first frame)
time.sleep(3)

ret, image = cap.read()

# If the return value form the VideoCapture is true, then write the image file
if ret:
    # Save the JPG image to send to the server
    cv2.imwrite("data/frame0.jpg", image)
    img = cv2.imread("data/frame0.jpg")

    # Get the regions of interest/parking spots
    r = cv2.selectROIs('ROI Selector', img, showCrosshair=False, fromCenter=False)

    if len(r):
        # Convert the result to a list
        rlist = r.tolist()
        print(rlist)

        # Write the list into a csv file
        with open('data/rois.csv', 'w', newline='') as outf:
            csvw = csv.writer(outf)
            csvw.writerows(rlist)
    else:
        print("Please select the Region of interest")

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
