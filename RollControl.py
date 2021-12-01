import board
import time
import RPi.GPIO as GPIO
import adafruit_lsm9ds1
from simple_pid import PID

##pin setup for GPIO
pwmpin = 18
cw = 17
ccw = 27

##setup PID Controller
pid = PID(0.3, 0.09, 0.01, setpoint=0)
pid.output_limits = (0, 1)
pid.sample_time = 0.01

##Board setup/GPIO setup
i2c = board.I2C()
sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)
GPIO.setmode(GPIO.BCM)
GPIO.setup(pwmpin, GPIO.OUT)
GPIO.setup(cw, GPIO.OUT)
GPIO.setup(ccw, GPIO.OUT)

##PWM setup for enable pin on L298D motor Driver
ena = GPIO.PWM(pwmpin, 100)
ena.start(0)

##LSM9DS1 Gyro Error detection and correction to 0
##Side note: added a .25 second delay timer to allow chip to get through initial reading
##First reading was always an outlier.
average = []
for x in range(3):
    time.sleep(.25)
    gyro_x, gyro_y, gyro_z = sensor.gyro
    average.append(gyro_z)
avg = sum(average) / len(average)

##Working loop simulating "coast phase" axial rotation minimization
while True:

    ##Initially set motor to not spin
    GPIO.output(cw, False)
    GPIO.output(ccw, False)

    ##read gyro data and take the z-axis info and subtract the error
    gyro_x, gyro_y, gyro_z = sensor.gyro
    gyro_real = gyro_z - abs(avg)
    print("Gyroscope: {2:5.2f}".format(gyro_x, gyro_y, gyro_real))

    ##Real gyro reading greater than 0.001 rad/sec angular velocity setpoint
    if gyro_real > 0.25:
        GPIO.output(cw, False)
        GPIO.output(ccw, True)
        dty = pid(gyro_real)
        ena.ChangeDutyCycle(dty)

    ##Real gyro reading less than -0.001 rad/sec angular velocity setpoint
    elif gyro_real < -0.25:
        GPIO.output(cw, True)
        GPIO.output(ccw, False)
        dty = pid(gyro_real)
        ena.ChangeDutyCycle(dty)

    time.sleep(.01)
