import random
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--path", type=str, default="./testcases")
    parser.add_argument("--pay_prob", type=float, default=0.25)
    parser.add_argument("--pay_max", type=int, default=10000)
    args = parser.parse_args()
    random.seed(args.seed)
    return args


def generate_one_testcase(args, path):
    n = random.randint(1, 1000)
    with open(path, "w") as f:
        f.write(str(n))
        f.write("\n")
        entr = [i for i in range(4)]
        exit = [i for i in range(4)]

        position = []  # to record what zone the car is at this "arrival time"

        arrival_time = 0
        num_veh = -1

        for vehicle_id in range(n):

            start = random.choice(entr)
            while start in position:  # Avoid generating the car at the same position at the same time
                start = random.choice(entr)

            position.append(start)

            end = random.choice(exit)
            while start == end:
                end = random.choice(exit)

            is_want_to_pay = random.random() < args.pay_prob
            payment = random.randint(1, args.pay_max) if is_want_to_pay else 0

            f.write(f"{vehicle_id} {arrival_time} {start} {end} {payment}")
            f.write("\n")

            if num_veh == -1:  # new arrival time(to decide how many cars will arrive at the same time)
                num_veh = random.randint(0, 3)  # select the number of cars that will arrive at the same time

            if num_veh == 0:
                to_add_arrival_time = random.randint(1, 5)  # select the arrival time of next car
                num_veh = -1
            else:
                to_add_arrival_time = 0
                num_veh = num_veh - 1

            if to_add_arrival_time:
                arrival_time = arrival_time + to_add_arrival_time
                position.clear()


def main():
    args = parse_args()
    for testcase_ind in range(args.n):
        path = args.path + "/testcase" + str(testcase_ind) + ".txt"
        generate_one_testcase(args, path)


if __name__ == "__main__":
    main()
