#High Flyers Mission 14
import HFMController as drone
import time
import threading
from djitellopy import Tello
import cv2

if __name__ == "__main__":
    params = {'floor':100, 'ceiling':300, 'min_takeoff_power':25, 'min_operating_power':10, 'tether':1000}
    my_robomaster = Tello()
    drone = drone.HighFlyers(my_robomaster, params)
    drone.log.info("Colt is about to takeoff. Mission 13 commencing.")
    drone.takeoff()
    stop_video_event = threading.Event()
    video_thread = threading.Thread(target=drone.record_video, args=(drone, stop_video_event, True))
    video_thread.setDaemon(True)
    video_thread.start()
    drone.rotate_clockwise(90)
    drone.fly_forward(30)
    drone.rotate_clockwise(90)
    drone.fly_forward(30)
    drone.fly_home()
    drone.flip_forward()
    stop_video_event.set()
    video_thread.join(0.5)
    print("Destroying all picture windows")
    cv2.destroyAllWindows()
    # Turn off the video stream and the drone
    print("Closing connection")
    print(f"Battery level is {drone.get_battery()}%")
    drone.end()
    print("Mission Complete")
    drone.log.info("Mission success!")