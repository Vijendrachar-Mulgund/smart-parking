# importing everything we need
import cv2
import csv
import time
import os
import socket
import pickle
import struct

# Constants
VIDEO_SOURCE = 1
SERVER_IP = '127.0.0.1'
SERVER_PORT = 5050
SERVER_ADDR = (SERVER_IP, SERVER_PORT)
CODEC = 'utf-8'
CLIENT_FILE_PATH = 'client_data'


def captureImageAndRoi():
    # Start the Camera
    cap = cv2.VideoCapture(VIDEO_SOURCE)

    # Allow the camera to start (To avoid the blank first frame) # Time in seconds.
    time.sleep(2)

    ret, image = cap.read()

    # If the return value form the VideoCapture is true, then write the image file
    if ret:
        # Get the regions of interest/parking spots
        r = cv2.selectROIs('ROI Selector', image, showCrosshair=False, fromCenter=False)

        if len(r):
            # Convert the result to a list
            rlist = r.tolist()
            print(rlist)

            # Write the list into a csv file
            with open(f"{CLIENT_FILE_PATH}/rois.csv", 'w', newline='') as outf:
                csvw = csv.writer(outf)
                csvw.writerows(rlist)
        else:
            print("Please select the Region of interest")

    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows()


def sendRoiFileToServer(clientSocket):
    csvFileName = os.path.basename('data/rois.csv')

    with open(f"{CLIENT_FILE_PATH}/rois.csv", 'rb') as csvFile:
        csvFileData = csvFile.read()

    clientSocket.sendall(len(csvFileData).to_bytes(8, byteorder='big'))
    clientSocket.sendall(csvFileData)
    clientSocket.sendall(len(csvFileName).to_bytes(4, byteorder='big'))
    clientSocket.sendall(csvFileName.encode('utf-8'))

    print(f"[CLIENT] Sent CSV file: {csvFileName}")


def videoStreamToAndFromServer(clientSocket):
    # Open the camera
    video_capture = cv2.VideoCapture(VIDEO_SOURCE)
    try:
        while True:
            # Capture a frame from the video source
            _, frame = video_capture.read()

            # Serialize each the frame
            frameData = pickle.dumps(frame)

            # Send the frame to the server
            clientSocket.sendall(struct.pack("Q", len(frameData)) + frameData)

            # Receive the processed frame from the server
            data = b""
            payloadSize = struct.calcsize("Q")

            while len(data) < payloadSize:
                packet = clientSocket.recv(4 * 1024)
                if not packet:
                    break
                data += packet

            packedMsgSize = data[:payloadSize]
            data = data[payloadSize:]
            msg_size = struct.unpack("Q", packedMsgSize)[0]

            while len(data) < msg_size:
                data += clientSocket.recv(4 * 1024)

            processed_frame_data = data[:msg_size]
            data = data[msg_size:]

            processed_frame = pickle.loads(processed_frame_data)

            # Display the processed frame (you can modify this part)
            cv2.imshow('Processed Video', processed_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        clientSocket.close()
        video_capture.release()
        cv2.destroyAllWindows()


def initClient():
    # Initialize the client socket to connect to the server
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect(SERVER_ADDR)

    # Capture the initial image and get the ROI co-ordinates
    captureImageAndRoi()

    # Send the Region of interest file to the server
    sendRoiFileToServer(clientSocket)

    # Start the video stream to the server and receive the processed video parallely and display
    videoStreamToAndFromServer(clientSocket)


# Start of the Client program
if __name__ == "__main__":
    os.makedirs(CLIENT_FILE_PATH, exist_ok=True)

    try:
        initClient()
    except KeyboardInterrupt:
        print('Client Shutdown 🛑')
