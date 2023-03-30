#High Flyers Mission 12
import HFMController as drone
import time
import threading
from djitellopy import Tello
import cv2

if __name__ == "__main__":
    params = {'floor':100, 'ceiling':300, 'min_takeoff_power':10, 'min_operating_power':10, 'tether':1000}
    my_robomaster = Tello()
    drone = drone.HighFlyers(my_robomaster, params)
    drone.log.info("Colt is about to takeoff. Mission 13 commencing.")
    drone.takeoff()
    drone.fly_basketball_court()
    print(f"Battery level is {drone.get_battery()}%")
    drone.end()
    print("Mission Complete")
    drone.log.info("Mission success!")
