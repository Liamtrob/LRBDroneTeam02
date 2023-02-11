#High Flyers Mission 12

import HFMController as drone

if __name__ == "__main__":
    params = {'floor':50, 'ceiling':100, 'min_takeoff_power':25, 'min_operating_power':10}
    my_robomaster = Tello()
    drone = drone.HighFlyers(my_robomaster, params)
    drone.log.info("Colt is about to takeoff. Mission 12 commencing.")
    drone.takeoff()
    drone.move_track_curve()
    drone.move_forward_long(8439)
    drone.move_track_curve()
    drone.move_forward_long(8439)
    drone.land()
    drone.log.info("Mission success!")
