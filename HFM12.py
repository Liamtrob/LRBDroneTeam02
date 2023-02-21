#High Flyers Mission 12 Updated for Basketball Court
import HFMController as drone
import time

if __name__ == "__main__":
    params = {'floor':50, 'ceiling':100, 'min_takeoff_power':25, 'min_operating_power':10, 'tether':200}
    my_robomaster = Tello()
    drone = drone.HighFlyers(my_robomaster, params)
    drone.log.info("Colt is about to takeoff. Mission 12 commencing.")
    drone.takeoff()
    drone.move_forward_long(1520)
    drone.rotate_counter_clockwise(90)
    drone.move_forward_long(2870)
    drone.rotate_counter_clockwise(90)
    drone.move_forward_long(1520)
    drone.rotate_counter_clockwise(90)
    drone.move_forward_long(2870)
    drone.rotate_counter_clockwise(90)
    time.sleep(3)
    drone.flip_forward()
    drone.land()
    drone.log.info("Mission success!")
