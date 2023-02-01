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
        self.drone.takeoff()

    def land(self):
        self.drone.land()

    def fly_to_mission_floor(self):
        height = self.drone.get_height()
        if height < self.params['floor']:
            self.drone.move_up(self.params['floor'] - self.drone.get_height())
        else:
            height = self.drone.get_height() - self.params['floor']
            self.drone.move_down(height)
    
    def fly_to_mission_ceiling(self):
        height = self.drone.get_height()
        if height > self.params['ceiling']:
            self.drone.move_down(self.drone.get_height() - self.params['ceiling'])
        else:
            height = self.params['ceiling'] - self.drone.get_height()
            self.drone.move_up(height)

    def fly_up(self, cm):
        self.drone.move_up(int(cm))

    def fly_down(self, cm):
        self.drone.move_down(int(cm))
            

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
                #print('IRS going to floor')
                self.drone.move_up(self.params['floor'] - self.drone.get_height())
            else:
                #print('IRS going to floor')
                self.drone.move_down(self.drone.get_height() - self.params['floor'])
        else: #Barometer
            if (self.drone.get_barometer() - BAR_floor) <= self.params['floor']:
                #print('BAR going up to floor')
                self.drone.move_up(self.params['floor'] - (self.drone.get_barometer() - BAR_floor))
            else:
                #print('BAR going down to floor')
                #print('BAR HEIGHT IS', self.drone.get_barometer())
                #print('BAR FLOOR IS', BAR_floor)
                #print('CURR BAR HEIGHT IS', self.drone.get_barometer() - BAR_floor)
                self.drone.move_down(int((self.drone.get_barometer() - BAR_floor) - self.params['floor']))
                #print('DONE MOVING DOWN')
                #print('CURR BAR HEIGHT AFTER GOING DOWN IS IS', self.drone.get_barometer() - BAR_floor)

    
    def go_to_ceiling(self, BAR_floor):
        if self.params['m_type'] == 'IRS': #m_type = measurement type , IR = Infrared Sensor
            if self.drone.get_height() >= self.params['ceiling']:
                #print('IRS going to ceiling')
                self.drone.move_down(self.drone.get_height() - self.params['ceiling'])
            else:
                #print('IRS going to ceiling')
                self.drone.move_up(self.params['ceiling'] - self.drone.get_height())
        else: #Barometer
            if drone.get_barometer() >= self.params['ceiling']:
                self.drone.move_down((self.drone.get_barometer() - BAR_floor) - self.params['ceiling'])
            else:
                self.drone.move_up(int(self.params['ceiling'] - (self.drone.get_barometer() - BAR_floor)))

#------------------------- END OF HighFlyers CLASS ---------------------------

if __name__ == "__main__":
    logging.config.dictConfig(log_settings)
    log = logging.getLogger(logname)

    print("Please enter your Measurement Type: IRS or BAR")
    m_type = input()

    #Barometer and Infrared Test Code #error between 35 and 40 for floor. greater than 40 good. BAR ERROR AT 35 CM
    params = {'floor': 10, 'ceiling': 200, 'm_type': m_type, 'mission_name': 'mission 5', 'drone_name': 'colt'}
    my_robomaster = Tello()
    drone = HighFlyers(my_robomaster, params)
    BAR_ground = drone.get_barometer()
    log.info("Colt is about to commence takeoff")
    drone.takeoff()
    log.info("Colt has successfully made it in the air")
    time.sleep(5)
    log.info("Colt is about to fly down to the mission floor")
    drone.go_to_floor(BAR_ground)
    log.info("Colt has reached the mission floor")
    time.sleep(5)
    log.info("Colt is about to fly to the ceiling")
    drone.go_to_ceiling(BAR_ground)
    log.info("Colt has reached the ceiling")
    time.sleep(5)
    log.info("Colt is about to fly down to the mission floor")
    drone.go_to_floor(BAR_ground) 
    log.info("Colt has reached the mission floor")
    log.info("Colt is about to commence landing")
    time.sleep(5)
    drone.land()
    log.info("Colt has landed. Mission Success!")

