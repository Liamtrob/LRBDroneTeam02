#High Flyers Mission 11

import HFMController as drone

if __name__ == "__main__":
    params = {'floor':50, 'ceiling':100, 'min_takeoff_power':25, 'min_operating_power':10}
    my_robomaster = Tello()
    drone = drone.HighFlyers(my_robomaster, params)
    drone.log.info("Colt is about to takeoff. Mission 11 commencing.")
    drone.takeoff()
    drone.rotate_counter_clockwise(45)
    drone.move_forward(10)
    drone.rotate_counter_clockwise(100)
    drone.move_forward(1000)
    drone.land()
    drone.log.info("Mission success!")
