# importing everything we need
import cv2
import csv
import time
import os
import socket

# Constants
VIDEO_SOURCE = 1
SERVER_IP_ADDRESS = '127.0.0.1'
SERVER_PORT = 5050


def captureInitialImageAndRoi():
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
            with open('data/rois.csv', 'w', newline='') as outf:
                csvw = csv.writer(outf)
                csvw.writerows(rlist)
        else:
            print("Please select the Region of interest")

    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows()


def sendCSVFileToServer(clientSocket):
    csvFileName = os.path.basename('data/rois.csv')

    with open('data/rois.csv', 'rb') as csvFile:
        csvFileData = csvFile.read()

    clientSocket.sendall(len(csvFileData).to_bytes(8, byteorder='big'))
    clientSocket.sendall(csvFileData)
    clientSocket.sendall(len(csvFileName).to_bytes(4, byteorder='big'))
    clientSocket.sendall(csvFileName.encode('utf-8'))

    print(f"[CLIENT] Sent CSV file: {csvFileName}")


def imageCaptureSendToServer(serverAddress):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect(serverAddress)

    # Send the CSV file to the server
    sendCSVFileToServer(clientSocket)

    # Start capturing the image for processing
    camera = cv2.VideoCapture(VIDEO_SOURCE)  # Use 0 for the default camera

    try:
        time.sleep(2)  # Allow the camera to warm up

        while True:
            # Capture an image
            ret, frame = camera.read()
            if not ret:
                print("[CLIENT] Failed to capture image.")
                break

            # Encode the image as JPEG
            _, imageData = cv2.imencode('.jpg', frame)
            image_data = imageData.tobytes()

            # Send the image to the server
            imageSize = len(image_data).to_bytes(8, byteorder='big')
            imageName = f"parking_image.jpg".encode('utf-8')
            imageNameSize = len(imageName).to_bytes(4, byteorder='big')

            clientSocket.sendall(imageSize)
            clientSocket.sendall(image_data)
            clientSocket.sendall(imageNameSize)
            clientSocket.sendall(imageName)

            print(f"[CLIENT] Sent: {imageName.decode('utf-8')}")

            # Wait for 5 seconds before capturing the next image
            time.sleep(5)

    except KeyboardInterrupt:
        print("[CLIENT] Client terminated by user.")

    finally:
        camera.release()
        clientSocket.close()


if __name__ == "__main__":
    # First capture the image and select Region of interest
    captureInitialImageAndRoi()

    # Establish a connection with the server
    server_address = (SERVER_IP_ADDRESS, SERVER_PORT)  # Change to the server address and port

    # Capture images every 5 seconds to send it to the server
    imageCaptureSendToServer(server_address)
