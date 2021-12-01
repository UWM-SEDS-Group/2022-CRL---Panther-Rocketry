from picamera import PiCamera
import board
import busio
import adafruit_lsm9ds1
from time import sleep
from os import fsync

def safeWrite(file, text):
    file.write(text)
    file.flush()
    fsync(file)


class LSM9DS1(Sensor):
    def __init__(self, i2c):
        self.name = "LSM9DS1"

        try:
            self.sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)
            self.status = "Online"
            self.functional = True
        except:
            self.status = "Error"
            self.functional = False

    def getData(self):
        rtr = {"accel_x": "Error", "accel_y": "Error", "accel_z": "Error", "mag_x": "Error", "mag_y": "Error",
               "mag_z": "Error", "gyro_x": "Error", "gyro_y": "Error", "gyro_z": "Error", "LSM Temp": "Error"}

        try:
            rtr['accel_x'], rtr['accel_y'], rtr['accel_z'] = self.sensor.acceleration
            rtr['mag_x'], rtr['mag_y'], rtr['mag_z'] = self.sensor.magnetic
            rtr['gyro_x'], rtr['gyro_y'], rtr['gyro_z'] = self.sensor.gyro

        except:
            pass

        return rtr


def main():
    ##Setup/log data
    datalogname = input("Please enter the name for the data log: ")
    videoname = input("Please enter the name for the video: ")

    if "." not in datalogname:
        datalogname = "%s.csv" % datalogname

    if "." not in videoname:
        videoname = "%s.h264" % videoname

    i2c = busio.I2C(board.SCL, board.SDA)

    sensors = [LSM9DS1(i2c)]

    print("Sensor Status:")
    for sensor in sensors:
        print("%s: %s" % (sensor.getName(), sensor.getStatus()))


    try:
        camera = PiCamera()
        camera.resolution = (1920, 1080)
        camera.framerate = 30
        print("Camera: Online")
    except:
        print("Camera: Error")

    input("!!!!Press Enter to start recording and logging!!!!")

    camera.start_recording('/home/pi/%s' % videoname)

    with open(datalogname, 'w') as f:
        for sensor in sensors:
            for key in sensor.getData():
                safeWrite(f, "%s," % key)

        safeWrite(f, '\n')

        while (True):
            for sensor in sensors:
                data = sensor.getData()

                for key in data:
                    if type(data[key]) == type(0.1):
                        safeWrite(f, "%.3f," % data[key])

                    else:
                        safeWrite(f, "%s," % data[key])
            safeWrite(f, '\n')
            
main()
