#Main controller File
#!/usr/bin/env python3
#High Flyers Mission 4

import dji_matrix as djim
import logging
from djitellopy import Tello
import time
import math
import logging, logging.config
from datetime import datetime

#------------------------- BEGIN HighFlyers CLASS ----------------------------
now = datetime.now().strftime("%Y%m%d.%H")
logfile = f"High Flyers.{now}.log"
logname = 'colt'
log_settings = {
    'version':1,
    'disable_existing_loggers': False,
    'handlers': {
        'error_file_handler': {
            'level': 'DEBUG',
            'formatter': 'drone_errfile_fmt',
            'class': 'logging.FileHandler',
            'filename': logfile,
            'mode': 'a',
        },
        'debug_console_handler': {
            'level': 'DEBUG',
            'formatter': 'drone_stderr_fmt',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },    
    },    
    'formatters': {
        'drone_errfile_fmt': {
            'format': '%(asctime)s|%(levelname)s: %(message)s [%(name)s@%(filename)s.%(funcName)s.%(lineno)d]',
            'datefmt': '%Y-%m-%dT%H:%M:%S'
        },
        'drone_stderr_fmt': {
            'format': '%(levelname)s: %(message)s [%(name)s@%(filename)s.%(funcName)s.%(lineno)d]',
        },
    },
    'loggers': {
        logname: {
            'handlers' :['debug_console_handler', 'error_file_handler'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

class HighFlyers():
    """
    An interface from Team "Heads-Up Flight" to control a DJI Tello RoboMaster 
    Drone. Inherits from the djitellopy.Tello class.
    """

    def __init__(self, drone_baseobject, mission_params, debug_level=logging.INFO):
        """
        Constuctor that establishes a connection with the drone. Pass in a new
        djitellopy Tello object give your HeadsUpTello object its wings.

        Arguments
            drone_baseobject: A new djitellopy.Tello() object
            debug_level:      Set the desired logging level.
                              logging.INFO shows every command and response 
                              logging.WARN will only show problems
                              There are other possibilities, see logging module
        """

        # HighFlyers class uses the design principal of composition (has-a)
        # instead of inheritance (is-a) so that we can choose between the real
        # drone and a simulator. If we had used inheritance, we would be forced
        # to choose one or the other.
        self.drone = drone_baseobject
        self.drone.LOGGER.setLevel(debug_level)
        self.params = mission_params
        self.x_distance = 0
        self.y_distance = 0
        self.curr_degrees = 0

        #logging object
        logging.config.dictConfig(log_settings)
        self.log = logging.getLogger(logname)

        try:
            self.drone.connect()
            self.connected = True
        except Exception as excp:
            print(f"ERROR: could not connect to Trello Drone: {excp}")
            print(f" => Did you pass in a valid drone base object?")
            print(f" => Verify that your firewall allows UDP ports 8889 and 8890")
            print(f"    The Chromebook's firewall reverts to default settings every")
            print(f"    time that you restart the virtual Linux environment.")
            print(f" => You may need to connect to the drone with the Trello App.")
            self.disconnect()
            raise
        return


    def takeoff(self):
        if self.drone.get_battery() <= self.params['min_takeoff_power']:
            print("Error Low Battery")
        else:
            self.drone.takeoff()
            self.log.info("Drone has taken off and passed battery check")
        print(f"Current Battery Level: {self.get_battery()}")

    def land(self):
        self.drone.land()

    def pre_flight_check(self): 
        """checks to see if drone is above min operating power, if not, logs error and lands"""
        if self.drone.get_battery() <= self.params['min_operating_power']:
            self.log.warning("Battery is below Min Operating Power. Drone will now Land.")
            self.drone.land()

    def fly_to_mission_floor(self):
        self.pre_flight_check()
        height = self.drone.get_height()
        if height < self.params['floor']:
            self.drone.move_up(self.params['floor'] - self.drone.get_height())
        else:
            height = self.drone.get_height() - self.params['floor']
            self.drone.move_down(height)
    
    def fly_to_mission_ceiling(self):
        self.pre_flight_check()
        height = self.drone.get_height()
        if height > self.params['ceiling']:
            self.drone.move_down(self.drone.get_height() - self.params['ceiling'])
        else:
            height = self.params['ceiling'] - self.drone.get_height()
            self.drone.move_up(height)

    def fly_up(self, cm):
        self.pre_flight_check()
        self.drone.move_up(int(cm))
        self.log.info(f"Drone succesfully flew up {cm} cm")

    def fly_down(self, cm):
        self.pre_flight_check()
        self.drone.move_down(int(cm))
        self.log.info(f"Drone succesfully flew down {cm} cm")
        
    #Fly forward/Fly Back min distance = 20cm
    def fly_forward(self, cm, home=False):
        self.pre_flight_check()
        self.drone.move_forward(int(cm))
        if 0 <= self.curr_degrees < 90 or 270 < self.curr_degrees < 360: #drone has rotated but still facing forward direction
            self.x_distance += round(abs(math.cos(math.radians(self.curr_degrees)) * cm),0)
        elif 0 < self.curr_degrees < 180: #drone has rotated but is still facing left/positive y direction
            self.x_distance -= round(abs(math.cos(math.radians(self.curr_degrees)) * cm),0)
        elif 180 < self.curr_degrees < 270: #drone has rotated and is facing lower right direction
            self.x_distance -= round(abs(math.cos(math.radians(self.curr_degrees)) * cm),0)
        
        if 0 < self.curr_degrees < 180: #drone is going left. adding to y distance
            self.y_distance += round(abs(math.sin(math.radians(self.curr_degrees)) * cm),0)
        elif 180 < self.curr_degrees < 360: #drone is going right. subtracting from y distance
            self.y_distance -= round(abs(math.sin(math.radians(self.curr_degrees)) * cm),0)
        self.log.info(f"Drone succesfully flew forward {cm} cm")
        
    def fly_back(self,cm):
        self.pre_flight_check()
        self.drone.move_back(int(cm))
        angle = self.curr_degrees + 180
        if 0 <= self.curr_degrees < 90 or 270 < self.curr_degrees < 360: #drone has rotated but still facing forward direction
            self.x_distance += round(abs(math.cos(math.radians(self.curr_degrees)) * cm),0)
        elif 0 < self.curr_degrees < 180: #drone has rotated but is still facing left/positive y direction
            self.x_distance -= round(abs(math.cos(math.radians(self.curr_degrees)) * cm),0)
        
        if 0 < self.curr_degrees < 180:
            self.y_distance += round(abs(math.sin(math.radians(self.curr_degrees)) * cm),0)
        elif 180 < self.curr_degrees < 360:
            self.y_distance -= round(abs(math.sin(math.radians(self.curr_degrees)) * cm),0)
        self.log.info(f"Drone succesfully flew back {cm} cm")
        
    def fly_left(self,cm):
        self.pre_flight_check()
        self.drone.move_left(int(cm))
        angle = self.curr_degrees + 90
        if 0 <= self.curr_degrees < 90 or 270 < self.curr_degrees < 360: #drone has rotated but still facing forward direction
            self.x_distance += round(abs(math.cos(math.radians(angle)) * cm),0)
        elif 0 < self.curr_degrees < 180: #drone has rotated but is still facing left/positive y direction
            self.x_distance -= round(abs(math.cos(math.radians(angle)) * cm),0)
        
        if 0 < self.curr_degrees < 180:
            self.y_distance += round(abs(math.sin(math.radians(angle)) * cm),0)
        elif 180 < self.curr_degrees < 360:
            self.y_distance -= round(abs(math.sin(math.radians(angle)) * cm),0)
        self.log.info(f"Drone succesfully flew left {cm} cm")
        
    def fly_right(self,cm):
        self.pre_flight_check()
        self.drone.move_right(int(cm))
        angle = self.curr_degrees + 270
        if 0 <= self.curr_degrees < 90 or 270 < self.curr_degrees < 360: #drone has rotated but still facing forward direction
            self.x_distance += round(abs(math.cos(math.radians(angle)) * cm),0)
        elif 0 < self.curr_degrees < 180: #drone has rotated but is still facing left/positive y direction
            self.x_distance -= round(abs(math.cos(math.radians(angle)) * cm),0)
        
        if 0 < self.curr_degrees < 180:
            self.y_distance += round(abs(math.sin(math.radians(angle)) * cm),0)
        elif 180 < self.curr_degrees < 360:
            self.y_distance -= round(abs(math.sin(math.radians(angle)) * cm),0)
        self.log.info(f"Drone succesfully flew right {cm} cm")

    def rotate_cw(self, degrees):
        self.drone.rotate_clockwise(int(degrees))
        self.curr_degrees = (self.curr_degrees - degrees) % 360
        self.log.info(f"Drone has rotated {degrees} clockwise")

    def rotate_ccw(self, degrees):
        self.drone.rotate_counter_clockwise(int(degrees))
        self.curr_degrees += degrees
        self.curr_degrees = self.curr_degrees % 360
        self.log.info(f"Drone has rotated {degrees} clockwise")

    def __del__(self):
        """ Destructor that gracefully closes the connection to the drone. """
        if self.connected:
            self.disconnect()
        return


    def disconnect(self):
        """ Gracefully close the connection with the drone. """
        self.drone.end()
        self.connected = False
        print(f"Drone connection closed gracefully")
        return


    def top_led_color(self, red:int, green:int, blue:int):
        """
        Change the top LED to the specified color. The colors don't match the
        normal RGB palette very well.

        Arguments
            red:   0-255
            green: 0-255
            blue:  0-255
        """

        r = djim.capped_color(red)
        g = djim.capped_color(green)
        b = djim.capped_color(blue)
        cmd = f"EXT led {r} {g} {b}"
        self.drone.send_control_command(cmd)
        return
            

    def top_led_off(self):
        """ Turn off the top LED. """

        cmd = f"EXT led 0 0 0"
        self.drone.send_control_command(cmd)
        return


    def matrix_pattern(self, flattened_pattern:str, color:str='b'):
        """
        Show the flattened pattern on the LED matrix. The pattern should be 
        64 letters in a row with values either (r)ed, (b)lue, (p)urple, or (0)
        off. The first 8 characters are the top row, the next 8 are the second
        row, and so on.
        
        Arguments
            flattened_pattern: see examples in dji_matrix.py
            color:             'r', 'b', or 'p'
        """

        if color.lower() not in "rpb":
            color = 'b'
        cmd = f"EXT mled g {flattened_pattern.replace('*', color.lower())}"
        self.drone.send_control_command(cmd)
        return


    def matrix_off(self):
        """ Turn off the 64 LED matrix. """
        
        off_pattern = "0" * 64
        self.matrix_pattern(off_pattern)
        return


    def get_battery(self):
        """ Returns the drone's battery level as a percent. """
        return self.drone.get_battery()


    def get_barometer(self):
        """ Returns the drone's current barometer reading in cm. """
        return self.drone.get_barometer()


    def get_temperature(self):
        """ Returns the drone's internal temperature in °F. """
        return self.drone.get_temperature()
    
        
    def go_to_floor(self, BAR_floor):
        if self.params['m_type'] == 'IRS':
            if self.drone.get_height() <= self.params['floor']:
                print('IRS going to floor')
                self.drone.move_up(self.params['floor'] - self.drone.get_height())
            else:
                print('IRS going to floor')
                curr_height_IRS = (self.drone.get_height())
                print('CURR IRS HEIGHT IS', curr_height_IRS)
                print('IRS - floor is', int((self.drone.get_height()) - self.params['floor']))
                self.drone.move_down(self.drone.get_height() - self.params['floor'])
        else: #Barometer
            if (self.drone.get_barometer() - BAR_floor) <= self.params['floor']:
                print('BAR going up to floor')
                self.drone.move_up(self.params['floor'] - (self.drone.get_barometer() - BAR_floor))
            else:
                print('BAR going down to floor')
                #print('BAR HEIGHT IS', self.drone.get_barometer())
                #print('BAR FLOOR IS', BAR_floor)
                curr_height_BAR = (self.drone.get_barometer() - BAR_floor)
                print('CURR BAR HEIGHT IS', curr_height_BAR)
                print('Bar - floor is', int((self.drone.get_barometer() - BAR_floor) - self.params['floor']))
                self.drone.move_down(int((self.drone.get_barometer() - BAR_floor) - self.params['floor']))
                print('DONE MOVING DOWN')
    
    def go_to_ceiling(self, BAR_floor):
        if self.params['m_type'] == 'IRS': #m_type = measurement type , IR = Infrared Sensor
            if self.drone.get_height() >= self.params['ceiling']:
                print('IRS going to ceiling')
                self.drone.move_down(self.drone.get_height() - self.params['ceiling'])
            else:
                print('IRS going to ceiling')
                self.drone.move_up(self.params['ceiling'] - self.drone.get_height())
        else: #Barometer
            if drone.get_barometer() >= self.params['ceiling']:
                self.drone.move_down((self.drone.get_barometer() - BAR_floor) - self.params['ceiling'])
            else:
                self.drone.move_up(self.params['ceiling'] - (self.drone.get_barometer() - BAR_floor))
    @property
    def degrees(self) -> int:
        try:
            return int(round(self.curr_degrees % 360, 0))
        except Exception as excp:
            self.log.warning("Cannot round degrees to a whole number")

    @property
    def position_x(self) -> int:
        try:
            return int(round(self.x_distance,0))
        except Exception as excp:
            self.log.warning("Cannot round X Distance to Whole Number")

    @property
    def position_y(self) -> int:
        try:
            return int(round(self.y_distance,0))
        except Exception as excp:
            self.log.warning("Cannot round Y Distance to Whole Number")
            

    @property
    def hypotenuse(self) -> int:
        try:
            return int(round(math.sqrt(self.position_x**2 + self.position_y**2),0))
        except Exception as excp:
            self.log.warning("Cannot round Hypotenuse Distance to Whole Number")

    @property
    def radians(self):
        try:
            return math.abs(int(round(math.radians(self.curr_degrees,0))))
        except Exception as excp:
            self.log.warning("Cannot round Radians to Whole Number")

    def fly_home(self, drone, direct_flight = False):
        distance = math.sqrt((self.x_distance ** 2) + (self.y_distance ** 2))
        if direct_flight == True:
            if self.position_x > 0 and self.position_y > 0: #drone is in upper left quadrant 
                angle_to_home = round(abs(math.degrees(math.atan2(self.position_x, self.position_y))), 0) + self.curr_degrees + 90
                self.rotate_cw(angle_to_home)
            elif self.position_x < 0 and self.position_y > 0: #drone is in lower left quadrant
                print('in fly home')
                angle_to_home = round(abs(math.degrees(math.atan2(self.position_x, self.position_y))), 0) + self.curr_degrees
                self.rotate_cw(angle_to_home)
            elif self.position_x < 0 and self.position_y < 0: #drone is in lower right quadrant
                angle_to_home = self.curr_degrees + (180 - round(abs(math.degrees(math.atan2(self.position_x, self.position_y))), 0))
                self.rotate_cw(angle_to_home)
            elif self.position_x > 0 and self.position_y < 0: #drone is in upper right quadrant
                angle_to_home = self.curr_degrees - 90 - round(abs(math.degrees(math.atan2(self.position_y, self.position_x))), 0)
                self.rotate_cw(angle_to_home)
            self.fly_forward(distance)
        else:
            if 0 < self.curr_degrees < 180:
                self.rotate_cw(self.curr_degrees)
            else:
                self.rotate_ccw(360 - self.curr_degrees)
            if self.x_distance > 0: #need to move backward
                self.fly_back(self.x_distance)
            if self.x_distance < 0:
                self.fly_forward(self.x_distance)     
            if self.y_distance > 0: #need to move left
                self.fly_left(self.y_distance)
            if self.y_distance < 0:
                self.fly_right(self.y_distance)
        

#------------------------- END OF HighFlyers CLASS ---------------------------
if __name__ == "__main__":

    print("Please enter your Measurement Type: IRS or BAR")
    #Barometer and Infrared Test Code
    params = {'floor':50, 'ceiling':100, 'min_takeoff_power':25, 'min_operating_power':10}
    to_fly = 20
    my_robomaster = Tello()
    drone = HighFlyers(my_robomaster, params)
    drone.takeoff()
    time.sleep(3)
    drone.fly_forward(20)
    time.sleep(2)
    drone.rotate_ccw(45)
    drone.fly_forward(20)
    time.sleep(2)
    drone.fly_home(drone, True)
    drone.land()
    

    """
    drone.fly_forward(to_fly)
    time.sleep(3)
    drone.fly_right(to_fly)
    time.sleep(3)
    drone.fly_forward(20)
    time.sleep(3)
    drone.fly_right(20)
    time.sleep(3)
    print("Now beginning to fly Home")
    drone.fly_home(drone)
    print("Succesfully ran Fly Home Function, will now land")
    drone.land()"""