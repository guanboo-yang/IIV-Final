import random
random.seed(123)

for testcase_ind in range(5):
    path = 'testcase' + str(testcase_ind) + '.txt'
    f = open(path, "w")

    n = random.randint(1, 1000)

    f.write(str(n)) 
    f.write("\r\n")

    entr = [0, 5, 6, 11]
    exit = [1, 2, 9, 10]
    zone = [3, 4, 7, 8]

    to_pay = [0,0,0,1]

    position = [] #to record what zone the car is at this "arrival time"

    arrival_time = 0
    num_veh = -1

    for i in range(n):
        vehicle_id = i
        
        start = random.choice(entr)
        
        while start in position:   #Avoid generating the car at the same position at the same time
            start = random.choice(entr)

        position.append(start)
        
        end = random.choice(exit)
        while (start == 0 and end == 1) or (start == 6 and end == 2) or (start == 11 and end == 10) or (start == 5 and end == 9):
            end = random.choice(exit)
        
        is_want_to_pay = random.choice(to_pay) #let most people not want to pay

        if is_want_to_pay:
            payment = random.randint(1, 10000)
        else:
            payment = 0

        f.write(f"{vehicle_id} {arrival_time} {start} {end} {payment}")
        f.write("\r\n")

        if(num_veh == -1): #new arrival time(to decide how many cars will arrive at the same time)
            num_veh = random.randint(0, 3) #select the number of cars that will arrive at the same time
            
        
        if(num_veh == 0):
            to_add_arrival_time = random.randint(1, 5)     #select the arrival time of next car
            num_veh = -1
        else:
            to_add_arrival_time = 0
            num_veh = num_veh - 1

        if to_add_arrival_time:
            arrival_time = arrival_time + to_add_arrival_time
            position.clear()