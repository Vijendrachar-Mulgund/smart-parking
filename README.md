# Smart Parking

As urbanisation and car ownership continue to rise, the challenge of finding convenient parking becomes increasingly significant. Globally a substantial portion of time is spent searching for parking spots, our project seeks to address this issue through an innovative Internet of Things (IoT) solution.

In this project, we configure the Raspberry Pi as a monitoring device, set up a cloud server using OpenStack, and establish a resilient socket connection between the client and server. The system's capabilities are showcased through the initiation of a live video feed, the real-time processing of each frame to identify available parking spaces, and the transmission of processed frames back to the client for display.

#### The project operates on a client-server model, and the visual representation of its functionality is depicted in the image below.

![Smart Paring Architecture](/assets/smart_systems.jpg)

## Project set up

To execute the project, it is essential to install an operating system on both the Raspberry Pi and the VPS server. Additionally, Python3 must be installed on both systems.

### Client side setup

To enable the camera module on the Raspberry Pi using raspi-config, you can install the required package using the following commands:

```
sudo apt update
sudo apt install raspi-config
```

Once the package is installed, you can run raspi-config to access the Raspberry Pi Software Configuration Tool. Navigate to the "Interfacing Options" and enable the camera module from there.

```
sudo raspi-config
```

After enabling the camera module, you may need to reboot your Raspberry Pi for the changes to take effect.

### Server side setup

We chose OpenStack for the server because it helps us create a virtual private server in the cloud. But if you prefer, you can use any other server that does the same job and has a public IP address. The public IP address is important because it allows the Raspberry Pi to connect to the server.

### Project Execution

The project has some specific requirements, or dependencies. These are like tools or packages that the project needs to work correctly. To organize these dependencies and prevent them from affecting other projects or your system, we create a Python virtual environment.

To create the python virtual environment, create a project folder and inside the project folder, execute the following command to create a Virtual environment.

```
python3 -m venv .
```

Activate the virtual environment using the following command.

```
source bin/activate
```

Once the virtual environment is active, clone the project and install the dependencies with the following command.

```
pip install -r requirements.txt
```

This command will install all the dependencies mentioned in the `retirements.txt` file

This procedure applies to both the client and the server.

Once everything is configured, initiate the server and then launch the client using the following commands.

Start server

```
python3 server.py
```

Start Client

```
python3 client.py
```
