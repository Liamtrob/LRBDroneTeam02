import logging
import random
import time
import math
import numpy

def _approximate(value):
    rand_10pct = value // 10
    return value + random.randint(-rand_10pct, +rand_10pct)


class DroneSim:

    def __init__(self):
        self._height = 0
        self._grounded = True
        self._connected = False
        self._start_time = 0
        self._stop_time = 0
        self._battery_level = 65
        self.x_distance = 0
        self.y_distance = 0
        self.curr_degrees = 0
        self.last_move = 0
        self.curr_move = 0

        # Set up logger, straight from DJI
        HANDLER = logging.StreamHandler()
        FORMATTER = logging.Formatter('[%(levelname)s] %(filename)s - %(lineno)d - %(message)s')
        HANDLER.setFormatter(FORMATTER)

        self.LOGGER = logging.getLogger('djitellopy')
        self.LOGGER.addHandler(HANDLER)
        self.LOGGER.setLevel(logging.INFO)


    def connect(self):
        print(">> CONNECTION ESTABLISHED <<")
        self._connected = True


    def end(self):
        print(f">> CONNECTION TERMINATED <<")
        self._connected = False

    def turn_motor_on(self):
        print(f">> MOTORS SPINNING <<")
        return

    def turn_motor_off(self):
        print(f">> MOTORS HAVE STOPPED <<")
        return

    def takeoff(self):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot takeoff b/c drone is not connected")
        if self._grounded == False:
            raise RuntimeError(f"Cannot takeoff b/c drone is already flying")

        # Start new mission flight time
        self._start_time = int(time.time())
        self._stop_time = self._start_time  # stop_time set by land() function

        # Simulate time delay
        delay = 2 * random.random()
        time.sleep(delay)

        # Perform requested operation
        self._height = _approximate(60)
        self._grounded = False
        self._battery_level -= 1

        # Log message
        print(f">> DRONE AIRBORN <<")


    def land(self):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot land b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot land b/c drone is already grounded")

        # Simulate time delay
        delay = 2 * random.random()
        time.sleep(delay)

        # Perform requested operation
        self._stop_time = int(time.time())
        self._height = 0
        self._grounded = True
        self._battery_level -= 1

        # Log message
        print(f">> DRONE LANDED <<")


    def get_flight_time(self):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot get flight time b/c drone is not connected")
        if self._grounded == True:
            return self._stop_time - self._start_time

        # Perform requested operation
        return int(time.time()) - self._start_time


    def move_up(self, value_cm):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot move UP b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot move UP b/c drone is grounded")

        # Simulate time delay
        delay = (value_cm // 100) + 2 * random.random()
        time.sleep(delay)

        # Perform requested operation
        self._height += _approximate(value_cm)
        self._battery_level -= 1

        # Log message
        print(f">> MOVED UP {value_cm}cm <<")
        return self._height


    def move_down(self, value_cm):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot move DOWN b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot move DOWN b/c drone is grounded")

        # Simulate time delay
        delay = (value_cm // 100) + 2 * random.random()
        time.sleep(delay)

        # Perform requested operation
        self._height -= _approximate(value_cm)
        self._battery_level -= 1

        # Log message
        print(f">> MOVED DOWN {value_cm}cm <<")
        return self._height


    def move_forward(self, value_cm, home=False):
        print("IN MOVE FORWARD. CURR DEGREES IS", self.curr_degrees)
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot move FWD b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot move FWD b/c drone is grounded")
        # Simulate time delay
        delay = (value_cm // 100) + 2 * random.random()
        time.sleep(delay)
        self._battery_level -= 1
        if 0 < self.curr_degrees < 90: #drone has rotated facing upper left quadrant
            self.x_distance += (math.cos(math.radians(self.curr_degrees)) * value_cm)
            self.y_distance += (math.sin(math.radians(self.curr_degrees)) * value_cm)
            print('ADDING TO X_DISTANCE', math.cos(math.radians(self.curr_degrees)) * value_cm)
        elif 90 < self.curr_degrees < 180: #drone has rotated and is facing lower left quadrant
            self.x_distance -= (math.cos(math.radians(self.curr_degrees)) * value_cm)
            self.y_distance += (math.sin(math.radians(self.curr_degrees)) * value_cm)
        elif 180 < self.curr_degrees < 270: #drone has rotated and is facing lower right quadrant
            self.x_distance -= (math.cos(math.radians(self.curr_degrees)) * value_cm)
            self.y_distance -= (math.sin(math.radians(self.curr_degrees)) * value_cm)
        elif 270 < self.curr_degrees < 360: #drone has rotated and is facing upper right quadrant
            self.x_distance += (math.cos(math.radians(self.curr_degrees)) * value_cm)
            self.y_distance += (math.sin(math.radians(self.curr_degrees)) * value_cm)
        elif self.curr_degrees == 0: #drone is not rotated facing forward 
            self.x_distance += value_cm
            self.y_distance += 0
        elif self.curr_degrees == 180: #drone is facing backwards
            self.x_distance -= value_cm
            self.y_distance += 0
        elif self.curr_degrees == 90: #drone is facing exactly left. x position won't change when moving forward
            self.x_distance += 0
            self.y_distance += value_cm
        else: #drone is facing exactly right. x position won't change when moving forward
            self.y_distance -= value_cm
        # Log message
        print(f">> MOVED FORWARD {value_cm}cm <<")
        return


    def move_back(self, value_cm):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot move BACK b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot move BACK b/c drone is grounded")
        self.x_distance -= value_cm
        # Simulate time delay
        delay = abs(value_cm // 100) + 2 * random.random()
        time.sleep(delay)
        self._battery_level -= 1
        if 0 < self.curr_degrees < 90: #drone has rotated facing upper left quadrant
            self.x_distance -= (math.cos(math.radians(self.curr_degrees)) * value_cm)
            self.y_distance -= (math.sin(math.radians(self.curr_degrees)) * value_cm)
            print('ADDING TO X_DISTANCE', math.cos(math.radians(self.curr_degrees)) * value_cm)
        elif 90 < self.curr_degrees < 180: #drone has rotated and is facing lower left quadrant
            self.x_distance += (math.cos(math.radians(self.curr_degrees)) * value_cm)
            self.y_distance -= (math.sin(math.radians(self.curr_degrees)) * value_cm)
        elif 180 < self.curr_degrees < 270: #drone has rotated and is facing lower right quadrant
            self.x_distance += (math.cos(math.radians(self.curr_degrees)) * value_cm)
            self.y_distance += (math.sin(math.radians(self.curr_degrees)) * value_cm)   
        elif 270 < self.curr_degrees < 360: #drone has rotated and is facing upper right quadrant
            self.x_distance -= (math.cos(math.radians(self.curr_degrees)) * value_cm)
            self.y_distance += (math.sin(math.radians(self.curr_degrees)) * value_cm)
        elif self.curr_degrees == 0: #drone is not rotated facing forward 
            self.x_distance -= value_cm
            self.y_distance += 0
        elif self.curr_degrees == 180: #drone is facing backwards
            self.x_distance += value_cm
            self.y_distance += 0
        elif self.curr_degrees == 90: #drone is facing exactly left. x position won't change when moving back
            self.x_distance += 0
            self.y_distance -= value_cm
        else: #drone is facing exactly right. x position wont change when moving back
            self.x_distance += 0
            self.y_distance += value_cm
        # Log message
        print(f">> MOVED BACK {value_cm}cm <<")
        return


    def move_left(self, value_cm):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot move LEFT b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot move LEFT b/c drone is grounded")
        # Simulate time delay
        delay = (value_cm // 100) + 2 * random.random()
        time.sleep(delay)
        self._battery_level -= 1
        if 0 < self.curr_degrees < 90: #drone has rotated facing upper left quadrant
            self.y_distance += (math.sin(math.radians(self.curr_degrees)) * value_cm)
            self.x_distance -= (math.cos(math.radians(self.curr_degrees)) * value_cm)
            print('ADDING TO Y_DISTANCE', math.cos(math.radians(self.curr_degrees)) * value_cm)
        elif 90 < self.curr_degrees < 180: #drone has rotated and is facing lower left quadrant
            self.y_distance -= (math.sin(math.radians(self.curr_degrees)) * value_cm)
            self.x_distance -= (math.cos(math.radians(self.curr_degrees)) * value_cm)
        elif 180 < self.curr_degrees < 270: #drone has rotated and is facing lower right quadrant
            self.y_distance += (math.sin(math.radians(self.curr_degrees)) * value_cm)
            self.x_distance += (math.cos(math.radians(self.curr_degrees)) * value_cm)
        elif 270 < self.curr_degrees < 360: #drone has rotated and is facing upper right quadrant
            self.y_distance -= (math.sin(math.radians(self.curr_degrees)) * value_cm)
            self.x_distance += (math.cos(math.radians(self.curr_degrees)) * value_cm)
        elif self.curr_degrees == 0: #drone is not rotated facing forward 
            self.y_distance += value_cm
        elif self.curr_degrees == 180: #drone is facing backwards
            self.y_distance -= value_cm
        elif self.curr_degrees == 90: #drone is facing exactly left. y position won't change but x will
            self.y_distance += 0
            self.x_distance -= value_cm
        else: #drone is facing directly right. y position wont change but x will
            self.y_distance += 0
            self.x_distance += value_cm
        # Log message
        print(f">> MOVED LEFT {value_cm}cm <<")
        return


    def move_right(self, value_cm):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot move RIGHT b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot move RIGHT b/c drone is grounded")
        # Simulate time delay
        delay = (value_cm // 100) + 2 * random.random()
        time.sleep(delay)
        self._battery_level -= 1
        if 0 < self.curr_degrees < 90: #drone has rotated facing upper left quadrant
            self.y_distance -= (math.sin(math.radians(self.curr_degrees)) * value_cm)
            self.x_distance += (math.cos(math.radians(self.curr_degrees)) * value_cm)
            print('ADDING TO Y_DISTANCE', math.cos(math.radians(self.curr_degrees)) * value_cm)
        elif 90 < self.curr_degrees < 180: #drone has rotated and is facing lower left quadrant
            self.y_distance += (math.sin(math.radians(self.curr_degrees)) * value_cm)
            self.x_distance += (math.cos(math.radians(self.curr_degrees)) * value_cm)
        elif 180 < self.curr_degrees < 270: #drone has rotated and is facing lower right quadrant
            self.y_distance += (math.sin(math.radians(self.curr_degrees)) * value_cm)
            self.x_distance -= (math.cos(math.radians(self.curr_degrees)) * value_cm)
        elif 270 < self.curr_degrees < 360: #drone has rotated and is facing upper right quadrant
            self.y_distance -= (math.sin(math.radians(self.curr_degrees)) * value_cm)
            self.x_distance -= (math.cos(math.radians(self.curr_degrees)) * value_cm)
        elif self.curr_degrees == 0: #drone is not rotated facing forward 
            self.y_distance -= value_cm
        elif self.curr_degrees == 180: #drone is facing backwards
            self.y_distance += value_cm
        elif self.curr_degrees == 90: #drone is facing exactly left. y position won't change but x will
            self.y_distance += 0
            self.x_distance += value_cm
        else: #drone is facing directly right. y position wont change but x will
            self.y_distance += 0
            self.x_distance -= value_cm
        # Log message
        print(f">> MOVED RIGHT {value_cm}cm <<")
        return


    def rotate_counter_clockwise(self, degrees):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot ROT CCW b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot ROT CCW b/c drone is grounded")
        self.curr_degrees += degrees
        self.curr_degrees = self.curr_degrees % 360
        # Simulate time delay
        delay = 1.5 * random.random()
        time.sleep(delay)
        self._battery_level -= 1

        # Log message
        print(f">> ROTATED CCW {degrees}° <<")
        return


    def rotate_clockwise(self, degrees):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot ROT CW b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot ROT CW b/c drone is grounded")
        self.curr_degrees += -degrees % 360
        self.curr_degrees = self.curr_degrees % 360
        # Simulate time delay
        delay = 1.5 + 2 * random.random()
        time.sleep(delay)
        self._battery_level -= 1

        # Log message
        print(f">> ROTATED CW {degrees}° <<")
        return


    def get_height(self):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot get height b/c drone is not connected")

        # Perform requested operation
        return self._height


    def get_temperature(self):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot get battery level b/c drone is not connected")

        # Perform requested operation
        return 95.5


    def get_battery(self):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot get battery level b/c drone is not connected")

        # Perform requested operation
        return self._battery_level


    def get_barometer(self):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot get battery level b/c drone is not connected")

        # Perform requested operation... assumes that ground level is 10 meters
        return self._height + 10000

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
    def degrees(self) -> int:
        try:
            return int(round(self.curr_degrees % 360, 0))
        except Exception as excp:
            self.log.warning("Cannot round degrees to a whole number")

    def fly_home(self, drone, direct_flight = False):
        if direct_flight == True:
            direction = 'ccw'
            if self.curr_degrees <= 180: #drone is facing forward or left side of coord plane
                turn_degrees = 180 - self.curr_degrees
                print('IN FLY HOME. DEGREES TO TURN IS ', turn_degrees)
            else: #drone is facing right side of coord plane
                direction = 'cw'
                turn_degrees = self.curr_degrees - 180
                distance_to_home = math.sqrt((self.curr_move ** 2) + (self.last_move ** 2) - (2 * self.curr_move * self.last_move * math.cos(math.radians(turn_degrees))))
                print("DISTANCE TO HOME IS", distance_to_home)
            if direction == 'ccw':
                self.rotate_counter_clockwise(turn_degrees)
                distance_to_home = math.sqrt((self.curr_move ** 2) + (self.last_move ** 2) - (2 * self.curr_move * self.last_move * math.cos(math.radians(turn_degrees))))
                print("DISTANCE TO HOME IS", distance_to_home)
                pyth_to_home = math.sqrt((self.x_distance**2) + (self.y_distance ** 2))
                print("PYTH DISTANCE TO HOME IS", pyth_to_home)
                drone.move_forward(distance_to_home, True)


    def rotate_to_bearing(self, degrees):
        degrees_to_rotate = math.abs(degrees - self.curr_degrees)
        if degrees_to_rotate > 180:
            ccw_degrees = (degrees_to_rotate - 360) % 360
            self.rotate_counter_clockwise(ccw_degrees)
        else:
            self.rotate_clockwise(degrees_to_rotate)


    def fly_to_coordinates(self, x_coord, y_coord, direct_flight=False):
        if direct_flight == False:
            if self.curr_degrees == 0 and self.x_distance == 0 and self.y_distance == 0: #flying to coordinates from start. drone is not rotated or moved
                if x_coord > 0 and y_coord > 0: #coordinates are in upper left quadrant
                    self.move_forward(x_coord - self.position_x)
                    self.move_left(y_coord - self.position_y)
                elif x_coord < 0 and y_coord > 0: #coordinates are in lower left quadrant
                    self.move_back(-x_coord)
                    self.move_left(y_coord)
                elif x_coord < 0 and y_coord < 0: #coordinates are in lower right quadrant
                    self.move_back(-x_coord)
                    self.move_right(-y_coord)
                elif x_coord > 0 and y_coord < 0: #coordinates are in upper right quadrant
                    self.move_forward(x_coord)
                    self.move_right(-y_coord)
            elif 0 < self.curr_degrees < 90 and self.x_distance == 0 and self.y_distance == 0: #flying to coordinates|drone is not moved and is rotated facing upper left quadrant
                hypotenuse = math.dist([x_coord, y_coord], [self.x_distance, self.y_distance])
                beta = self.curr_degrees
                alpha = math.atan(y_coord / x_coord)
                theta = beta - alpha
                width = hypotenuse * math.sin(theta)
                length = hypotenuse * math.cos(theta)
                if x_coord > 0 and y_coord > 0: #going to upper left quadrant
                    self.move_forward(length)
                    if y_coord > self.y_distance:
                        self.move_left(width)
                    else:
                        self.move_right(width)
                elif x_coord < 0 and y_coord > 0: #going to lower left quadrant
                    self.move_left(length)
                    if y_coord > self.y_distance:
                        self.move_forward(width)
                    else:
                        self.move_back(width)
                elif x_coord > 0 and y_coord < 0: #going to upper right quadrant
                    self.move_right(length)
                    if y_coord > self.y_distance:
                        self.move_forward(width)
                    else:
                        self.move_back(width)
                else: #going to lower right quadrant
                    self.move_back(length)
                    if y_coord > self.y_distance:
                        self.move_left(width)
                    else:
                        self.move_right(width)
            elif 90 < self.curr_degrees < 180 and self.x_distance == 0 and self.y_distance == 0: #flying to coordinates|drone is not moved and is rotated facing lower left quadrant
                hypotenuse = math.dist([x_coord, y_coord], [self.x_distance, self.y_distance])
                beta = self.curr_degrees
                faux_x = self.x_distance if self.x_distance > 0 else 1
                faux_y = self.y_distance
                alpha = math.atan(y_coord / x_coord)
                theta = beta - alpha
                alpha = 180 - (theta + beta)
                width = math.sin(theta) * hypotenuse
                length = math.sqrt((hypotenuse ** 2) - (width ** 2))
                if x_coord > 0 and y_coord > 0: #going to upper left quadrant
                    self.move_right(length)
                    if y_coord > self.y_distance:
                        self.move_forward(width)
                    else:
                        self.move_back(width)
                elif x_coord < 0 and y_coord > 0: #going to lower left quadrant
                    self.move_forward(length)
                    if y_coord > self.y_distance:
                        self.move.right(width)
                    else:
                        self.move.left(width)
                elif x_coord > 0 and y_coord < 0: #going to upper right quadrant  
                    self.move_back(length)
                    if y_coord > self.y_distance:
                        self.move_right(width)
                    else:
                        self.move_left(width)
                else: #going to lower right quadrant
                    self.move_left(length)
                    if y_coord > self.y_distance:
                        self.move_forward(width)
                    else:
                        self.move_back(width)
            elif 180 < self.curr_degrees < 270 and self.x_distance == 0 and self.y_distance == 0: #flying to coordinates|drone is not moved and is rotated facing lower right quadrant
                hypotenuse = math.dist([x_coord, y_coord], [self.x_distance, self.y_distance])
                beta = self.curr_degrees
                faux_x = self.x_distance if self.x_distance > 0 else 1
                faux_y = self.y_distance
                alpha = (90 - math.atan(faux_y / faux_x))
                theta = beta - alpha
                alpha = 180 - (theta + beta)
                width = math.sin(theta) * hypotenuse
                length = math.sqrt((hypotenuse ** 2) - (width ** 2))
                if x_coord > 0 and y_coord > 0: #going to upper left quadrant
                    self.move_back(length)
                    if y_coord > self.y_distance:
                        self.move_left(width)
                    else:
                        self.move_right(width) #HERE
                elif x_coord < 0 and y_coord > 0: #going to lower left quadrant
                    self.move_left(length)
                    if y_coord > self.y_distance:
                        self.move_back(width)
                    else:
                        self.move_forward(width)
                elif x_coord > 0 and y_coord < 0: #going to upper right quadrant  
                    self.move_right(length)
                    if x_coord > self.x_distance:
                        self.move_back(width)
                    else:
                        self.move_forward(width)
                else: #going to lower right quadrant
                    self.move_forward(length)
                    if y_coord > self.y_distance:
                        self.move_left(width)
                    else:
                        self.move_right(width)
            elif 270 < self.curr_degrees < 360 and self.x_distance == 0 and self.y_distance == 0: #flying to coordinates|drone is not moved and is rotated facing upper right quadrant
                hypotenuse = math.dist([x_coord, y_coord], [self.x_distance, self.y_distance])
                beta = self.curr_degrees
                faux_x = self.x_distance if self.x_distance > 0 else 1
                faux_y = self.y_distance
                alpha = math.atan(faux_y / faux_x)
                theta = beta - alpha
                alpha = 180 - (theta + beta)
                width = math.sin(theta) * hypotenuse
                length = math.sqrt((hypotenuse ** 2) - (width ** 2))
                if x_coord > 0 and y_coord > 0: #going to upper left quadrant
                    self.move_left(length)
                    if y_coord > self.y_distance:
                        self.move_forward(width)
                    else:
                        self.move_back(width)
                elif x_coord < 0 and y_coord > 0: #going to lower left quadrant
                    self.move_back(length)
                    if y_coord > self.y_distance:
                        self.move_left(width)
                    else:
                        self.move_right(width)
                elif self.x_distance > 0 and self.y_distance > 0: #going to upper right quadrant  
                    self.move_forward(length)
                    if y_coord > self.y_distance:
                        self.move_left(width)
                    else:
                        self.move_right(width)
                else: #going to lower right quadrant
                    self.move_right(length)
                    if y_coord > self.y_distance:
                        self.move_back(width)
                    else:
                        self.move_forward(width)                     
            elif self.curr_degrees > 0 and self.x_distance > 0 and self.y_distance > 0: #flying to coordinates|drone is moved and rotated
                hypotenuse = math.dist([x_coord, y_coord], [self.x_distance, self.y_distance])
                beta = self.curr_degrees
                faux_x = self.x_distance 
                faux_y = self.y_distance
                alpha = math.atan( y_coord - faux_y / x_coord - faux_x)
                theta = beta - alpha
                alpha = 180 - (theta + beta)
                width = math.sin(theta) * hypotenuse
                length = math.sqrt((hypotenuse ** 2) - (width ** 2))
                if 0 < self.curr_degrees < 180 and self.x_distance > 0 and self.y_distance > 0: #upper left quadrant
                    self.move_back(length)
                    self.move_left(width)
                elif 0 < self.curr_degrees < 180 and self.x_distance < 0 and self.y_distance > 0: #lower left quadrant
                    self.move_back(length)
                    self.move_right(width)
                elif 180 < self.curr_degrees < 360 and self.x_distance > 0 and self.y_distance > 0: #upper right quadrant
                    print("in upper right")
                    self.move_back(length)
                    self.move_right(width)
                else: #lower right quadrant
                    self.move_back(length)
                    self.move_left(width)        
        else: #direct flight
            distance_to = math.dist([x_coord, y_coord], [self.x_distance, self.y_distance])
            angle_to = math.degrees(math.tan(y_coord/x_coord))
            print("ANGLE TO IS", angle_to)
            if x_coord > 0 and y_coord > 0: #flying to upper left quadrant
                to_rotate = 90 - angle_to 
                self.rotate_counter_clockwise(to_rotate)
                print("DISTANCE TO IS", distance_to)
                self.move_forward(distance_to)
            elif x_coord > 0 and y_coord < 0: #flying to upper right quadrant
                print("going to upper right")
                to_rotate = 90 + angle_to
                self.rotate_clockwise(to_rotate)
                self.move_forward(distance_to)
            elif x_coord < 0 and y_coord < 0: #flying to lower right quadrant
                to_rotate = 180 + angle_to
                print("TO ROTATE IS", to_rotate)
                self.rotate_counter_clockwise(to_rotate)
                self.move_forward(distance_to)
            else: #flying to lower left quadrant
                to_rotate = 180 - angle_to
                print("TO ROTATE IS", to_rotate)
                self.rotate_clockwise(to_rotate)
                self.move_forward(distance_to)


if __name__ == "__main__":
    drone = DroneSim()
    drone.connect()
    drone.takeoff()
    drone.fly_to_coordinates(400, 300, True)
    #drone.fly_home(0,0)
    #drone.rotate_counter_clockwise(37)
    #drone.move_forward(5)
    #drone.move_left(7)
    print(drone.x_distance)
    print(drone.y_distance)
    '''drone.rotate_counter_clockwise(45)
    drone.fly_to_coordinates(50, -40)
    print('CURR DEGREES IS__', drone.curr_degrees)
    print('CURR X_DISTANCE IS', drone.x_distance)
    print('CURR Y_DISTANCE IS', drone.y_distance)
    drone.fly_home(drone)
    drone.land()
    print(drone.x_distance)'''
    