# Importing everything we need
import cv2
import csv
import numpy
import socket
import os
import pickle
import struct

# from PIL import Image

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5050
SERVER_ADDR = (SERVER_IP, SERVER_PORT)
CODEC = 'utf-8'
SERVER_FILE_PATH = 'server_data'


# Declaring a static variable
class Spots:
    loc = 0


# Empty callback function for creating tracker
def callback(foo):
    pass


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


def receiveRoiFile(connection):
    # Receive the CSV file from the client
    csvFileSize = int.from_bytes(connection.recv(8), byteorder='big')
    csvFileData = connection.recv(csvFileSize)
    csvFileNameSize = int.from_bytes(connection.recv(4), byteorder='big')
    csvFileName = connection.recv(csvFileNameSize).decode(CODEC)
    csvFilePath = os.path.join(SERVER_FILE_PATH, csvFileName)

    print("[SERVER] The CSV file ", csvFileData)

    with open(csvFilePath, 'wb') as csv_file:
        csv_file.write(csvFileData)

    # getting the spots coordinates into a list
    with open(f"{SERVER_FILE_PATH}/rois.csv", 'r', newline='') as inf:
        csvRead = csv.reader(inf)
        rois = list(csvRead)
    # converting the values to integer
    rois = [[int(float(j)) for j in i] for i in rois]

    print(f"[SERVER] Received CSV file: {csvFileName}")

    return rois


# Process each image frame
def processFrame(iframe, rois):
    # Creating the parameters window with trackbars
    cv2.namedWindow('parameters')
    cv2.createTrackbar('Threshold1', 'parameters', 186, 700, callback)
    cv2.createTrackbar('Threshold2', 'parameters', 122, 700, callback)
    cv2.createTrackbar('Min pixels', 'parameters', 100, 1500, callback)
    cv2.createTrackbar('Max pixels', 'parameters', 500, 1500, callback)

    # set the number of spots to 0
    Spots.loc = 0

    # Convert the Image to a Numpy array
    frame = numpy.array(iframe)

    # Define the range of pixels and the thresholds for Canny function
    minValue = cv2.getTrackbarPos('Min pixels', 'parameters')
    maxValue = cv2.getTrackbarPos('Max pixels', 'parameters')
    lowThreshold = cv2.getTrackbarPos('Threshold1', 'parameters')
    highThreshold = cv2.getTrackbarPos('Threshold2', 'parameters')

    # Apply the function for every list of coordinates
    for i in range(len(rois)):
        drawRectangle(frame, rois[i][0], rois[i][1], rois[i][2], rois[i][3], lowThreshold, highThreshold, minValue, maxValue)

    # Adding the number of available spots on the shown image
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, 'Available spots: ' + str(Spots.loc), (10, 30), font, 1, (0, 255, 0), 3)
    # cv2.imshow('Parking Space', frame)

    # Displaying the image with Canny function applied for reference
    # canny = cv2.Canny(frame, lowThreshold, highThreshold)
    # cv2.imshow('Canny Image', canny)

    # # Listen for 'Q' key to stop the stream
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
    return frame


def videoStreamFormAndToClient(connection, rois):
    try:
        while True:
            # Receive the video frame from the client
            data = b""
            payloadSize = struct.calcsize("Q")

            while len(data) < payloadSize:
                packet = connection.recv(4 * 1024)
                if not packet:
                    break
                data += packet

            packedMsgSize = data[:payloadSize]
            data = data[payloadSize:]
            msgSize = struct.unpack("Q", packedMsgSize)[0]

            while len(data) < msgSize:
                data += connection.recv(4 * 1024)

            frameData = data[:msgSize]
            data = data[msgSize:]

            frame = pickle.loads(frameData)

            # Process the video frame
            processedFrame = processFrame(frame, rois)

            # Send the processed frame back to the client
            processedFrameData = pickle.dumps(processedFrame)
            connection.sendall(struct.pack("Q", len(processedFrameData)) + processedFrameData)

    finally:
        connection.close()


# The initialize function
def initServer():
    # Create and bind the socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(SERVER_ADDR)
    serverSocket.listen(1)

    print(f"[SERVER] Waiting for a connection on {SERVER_ADDR}...")

    connection, clientAddress = serverSocket.accept()
    print(f"[SERVER] Connected to {clientAddress}")

    try:
        # Receive the CSF with the region of interest co-ordinates and store the file in the server
        rois = receiveRoiFile(connection)

        # Receive the feed from the client to process, send the processed feed back to the client
        videoStreamFormAndToClient(connection, rois)

    finally:
        # At the end, close the socket connection
        connection.close()
        serverSocket.close()


# The start of the Server program
if __name__ == "__main__":
    os.makedirs(SERVER_FILE_PATH, exist_ok=True)

    try:
        initServer()
    except (KeyboardInterrupt, ConnectionResetError):
        print('Server shutdown 🛑')
