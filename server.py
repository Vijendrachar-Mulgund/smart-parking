# Importing everything we need
import cv2
import csv
import numpy
import socket
import os
# from PIL import Image

SERVER_IP_ADDRESS = '127.0.0.1'
SERVER_PORT = 5050


# Declaring a static variable
class Spots:
    loc = 0


# Function to determine if a spot is free/occupied
# Params include: image source, individual spot coordinates
def drawRectangle(img, a, b, c, d, lowThreshold, highThreshold, minValue, maxValue):
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


def imageProcessor(serverAddress, savePath):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(serverAddress)
    serverSocket.listen(1)

    print(f"[SERVER] Waiting for a connection on {serverAddress}...")

    connection, clientAddress = serverSocket.accept()
    print(f"[SERVER] Connected to {clientAddress}")

    try:
        while True:
            # Receive image from the client
            imageSize = connection.recv(8)

            # If there is no image size, then break
            if not imageSize:
                break

            imageSize = int.from_bytes(imageSize, byteorder='big')

            imageData = connection.recv(imageSize)
            imageNameSize = connection.recv(4)
            image_name_size = int.from_bytes(imageNameSize, byteorder='big')

            imageName = connection.recv(image_name_size).decode('utf-8')
            imagePath = os.path.join(savePath, imageName)

            with open(imagePath, 'wb') as imageFile:
                imageFile.write(imageData)

            print(f"[SERVER] Received: {imageName}")

            # Process the image here # Find the parking spots and write the processed image into the file
            findParkingSpots(imageFile)

            # Send the received image back to the same client
            with open(imagePath, 'rb') as imgFile:
                image_data = imgFile.read()

            connection.sendall(len(image_data).to_bytes(8, byteorder='big'))
            connection.sendall(image_data)

            print(f"[SERVER] Sent back: {imageName}")

    finally:
        connection.close()
        serverSocket.close()


def findParkingSpots(imageFile):
    # set the number of spots to 0
    Spots.loc = 0

    # Convert the Image to a Numpy array
    frame = numpy.array(imageFile)

    # Define the range of pixels and the thresholds for Canny function
    minValue = cv2.getTrackbarPos('Min pixels', 'parameters')
    maxValue = cv2.getTrackbarPos('Max pixels', 'parameters')
    lowThreshold = cv2.getTrackbarPos('Threshold1', 'parameters')
    highThreshold = cv2.getTrackbarPos('Threshold2', 'parameters')

    # Apply the function for every list of coordinates
    for i in range(len(rois)):
        drawRectangle(frame, rois[i][0], rois[i][1], rois[i][2], rois[i][3], lowThreshold, highThreshold, minValue,
                      maxValue)

    # Adding the number of available spots on the shown image
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, 'Available spots: ' + str(Spots.loc), (10, 30), font, 1, (0, 255, 0), 3)
    # cv2.imshow('Parking Space', frame)

    # Displaying the image with Canny function applied for reference
    # canny = cv2.Canny(frame, lowThreshold, highThreshold)
    # cv2.imshow('Canny Image', canny)


# The start of the program #
if __name__ == "__main__":
    server = (SERVER_IP_ADDRESS, SERVER_PORT)  # Change to your desired address and port
    filePath = 'images'  # Change to your desired directory
    os.makedirs(filePath, exist_ok=True)

    try:
        imageProcessor(server, filePath)
    except KeyboardInterrupt:
        print('Server')
