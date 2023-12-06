# Importing everything we need
import cv2
import csv
import numpy
from PIL import Image


# Declaring a static variable
class Spots:
    loc = 0


# Function to determine if a spot is free/occupied
# Params include: image source, individual spot coordinates
def drawRectangle(img, a, b, c, d):
    # cutting the image based on the coordinates
    sub_img = img[b:b + d, a:a + c]

    # extracting the edges
    edges = cv2.Canny(sub_img, lowThreshold, highThreshold)

    # Count the number of pixels
    pix = cv2.countNonZero(edges)

    # Testing if the pixels number is in the given range
    if pix in range(minValue, maxValue):
        # Drawing a green rectangle on the source image using the given coordinates
        # Increasing the number of available spots
        cv2.rectangle(img, (a, b), (a + c, b + d), (0, 255, 0), 3)
        Spots.loc += 1
    else:
        # Drawing a red rectangle on the source image if the pixels number is not in the range
        cv2.rectangle(img, (a, b), (a + c, b + d), (0, 0, 255), 3)


# empty callback function for creating tracker
def callback(foo):
    pass


# getting the spots coordinates into a list
with open('data/rois.csv', 'r', newline='') as inf:
    csvRead = csv.reader(inf)
    rois = list(csvRead)
# converting the values to integer
rois = [[int(float(j)) for j in i] for i in rois]

# creating the parameters window with trackbars
cv2.namedWindow('parameters')
cv2.createTrackbar('Threshold1', 'parameters', 186, 700, callback)
cv2.createTrackbar('Threshold2', 'parameters', 122, 700, callback)
cv2.createTrackbar('Min pixels', 'parameters', 100, 1500, callback)
cv2.createTrackbar('Max pixels', 'parameters', 500, 1500, callback)


# Start the feed
while True:
    # set the number of spots to 0
    Spots.loc = 0

    # Read the image from the folder
    imgRead = Image.open('data/frame0.jpg')

    # Convert the Image to a Numpy array
    frame = numpy.array(imgRead)

    # Define the range of pixels and the thresholds for Canny function
    minValue = cv2.getTrackbarPos('Min pixels', 'parameters')
    maxValue = cv2.getTrackbarPos('Max pixels', 'parameters')
    lowThreshold = cv2.getTrackbarPos('Threshold1', 'parameters')
    highThreshold = cv2.getTrackbarPos('Threshold2', 'parameters')

    # Apply the function for every list of coordinates
    for i in range(len(rois)):
        drawRectangle(frame, rois[i][0], rois[i][1], rois[i][2], rois[i][3])

    # Adding the number of available spots on the shown image
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, 'Available spots: ' + str(Spots.loc), (10, 30), font, 1, (0, 255, 0), 3)
    cv2.imshow('Parking Space', frame)

    # Displaying the image with Canny function applied for reference
    canny = cv2.Canny(frame, lowThreshold, highThreshold)
    cv2.imshow('Canny Image', canny)

    # Listen for 'Q' key to stop the stream
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
