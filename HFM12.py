#High Flyers Mission 12

import HFMController as drone

if __name__ == "__main__":
    params = {'floor':50, 'ceiling':100, 'min_takeoff_power':25, 'min_operating_power':10, 'tether':200}
    my_robomaster = Tello()
    drone = drone.HighFlyers(my_robomaster, params)
    drone.log.info("Colt is about to takeoff. Mission 12 commencing.")
    drone.takeoff()
    drone.move_track_curve() #fly around first curve of track
    drone.move_forward_long(8439) #fly on first straight of track
    drone.move_track_curve() #fly on second curve of track
    drone.move_forward_long(8439) #fly on second straight of track back to home
    drone.land()
    drone.log.info("Mission success!")
