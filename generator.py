import random
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--testcase", type=int, default=5)
    parser.add_argument("-t", "--time", type=int, default=10)
    parser.add_argument("-c", "--num_cars", type=float, default=2.0)
    parser.add_argument("-u", "--allow_u_turn", action="store_true", default=False)
    parser.add_argument("-p", "--path", type=str, default="./testcases")
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--pay_prob", type=float, default=0.25)
    parser.add_argument("--pay_max", type=int, default=100)
    args = parser.parse_args()
    random.seed(args.seed)
    return args


#     | 0 | 3 |
# | 0 | 0 | 3 | 3 |
# | 1 | 1 | 2 | 2 |
#     | 1 | 2 |


def generate_one_testcase(args, path):
    n = random.randint(1, 1000)

    weights = [0.2 + (args.num_cars - 2) * 0.1 * i for i in range(-2, 3)]

    with open(path, "w") as f:
        f.write(str(n))
        f.write("\n")
        zone = [i for i in range(4)]
        zone = [i for i in range(4)]

        vehicle_id = 0

        for time in range(args.time):
            num_vehicle = random.choices(range(5), weights=weights)[0]

            start_pos = random.sample(range(4), num_vehicle)

            for i in range(num_vehicle):
                start = start_pos[i]
                end = random.choice(zone)

                while start == (end + 1) % 4:
                    if args.allow_u_turn:
                        break
                    end = random.choice(zone)

                is_want_to_pay = random.random() < args.pay_prob
                payment = random.randint(1, args.pay_max) if is_want_to_pay else 0

                f.write(f"{vehicle_id} {time} {start} {end} {payment}")
                f.write("\n")
                vehicle_id += 1


def main():
    args = parse_args()
    for testcase_ind in range(args.testcase):
        path = args.path + "/testcase" + str(testcase_ind) + ".txt"
        generate_one_testcase(args, path)


if __name__ == "__main__":
    main()
