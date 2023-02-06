#High Flyers Mission 9

import HFMController as drone

if __name__ == "__main__":
    params = {'floor':50, 'ceiling':100, 'min_takeoff_power':25, 'min_operating_power':10}
    my_robomaster = Tello()
    drone = drone.HighFlyers(my_robomaster, params)
    drone.log.info("Colt is about to takeoff. Mission 9 commencing.")
    drone.takeoff()
    drone.fly_to_coordinates(400, 300, True)
    drone.log.info("Colt has reached the desired coordinates and will fly home now.")
    drone.fly_home()
    drone.log.info("Colt has returned home. Mission success!")
    #drone.fly_to_coordinates(0,0,True)
    #drone.fly_home(0,0)
    #drone.rotate_counter_clockwise(37)
    #drone.move_forward(5)
    #drone.move_left(7)
    #print(drone.x_distance)
    #print(drone.y_distance)
    #print(drone.curr_degrees)

