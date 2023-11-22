import numpy as np
import datetime as dt
import json
import argparse
import pandas as pd

from api.app.v1.model.elevator_model import Elevator as ElevatorModel


# Entry variables
TOTAL_FLOOR = 0
DATASET_LENGHT = 0
MIN_NUM_PEOPLE_X_FLOOR = 0
MAX_NUM_PEOPLE_X_FLOOR = 0
MIN_AVG_AGE_X_FLOOR = 0
MAX_AVG_AGE_X_FLOOR = 0

# Business rules
WEIGHT_GARAGE_1 = 0.0 # weight for garage floor, 0 if no garage
WEIGHT_FLOOR_0 = 0.0 # weight for ground floor for next floor
OLD_PEOPLE_LIMIT = 0
WEIGHT_YOUNG = 0.0
WEIGHT_FLOOR = 0.0
WEIGHT_PEOPLE = 0.0
WEIGHT_AGE = 0.0

avg_people_x_floor_list = []
avg_age_x_floor_list = []


def setup_entry_variables():
    """Set entry variable."""
    global TOTAL_FLOOR
    global DATASET_LENGHT
    global MIN_NUM_PEOPLE_X_FLOOR
    global MAX_NUM_PEOPLE_X_FLOOR
    global MIN_AVG_AGE_X_FLOOR
    global MAX_AVG_AGE_X_FLOOR
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('-t', '--total_floor', metavar='<TOTAL_FLOOR>', type=int,
                            required=False, default=10, help='Total building floor',
                            dest='total_floor')
    arg_parser.add_argument('-d', '--data_lenght', metavar='<DATASET_LENGHT>', type=int,
                            required=False, default=20, help='Data lenght to store in DB',
                            dest='dataset_lenght')
    arg_parser.add_argument('-n', '--min_num_people', metavar='<MIN_NUM_PEOPLE_X_FLOOR>',
                            type=int, required=False, default=1,
                            help='Minimun number of people per floor',
                            dest='min_num_people_x_floor')
    arg_parser.add_argument('-o', '--max_num_people', metavar='<MAX_NUM_PEOPLE_X_FLOOR>',
                            type=int, required=False, default=10,
                            help='Maximun number of people per floor',
                            dest='max_num_people_x_floor')
    arg_parser.add_argument('-p', '--min_avg_age', metavar='<MIN_AVG_AGE_X_FLOOR>', type=int,
                            required=False, default=18, help='Minimun average age per floor',
                            dest='min_avg_age_x_floor')
    arg_parser.add_argument('-q', '--max_avg_age', metavar='<MAX_AVG_AGE_X_FLOOR>', type=int,
                            required=False, default=90, help='Maximun average age per floor',
                            dest='max_avg_age_x_floor')

    args = arg_parser.parse_args()

    TOTAL_FLOOR = args.total_floor
    DATASET_LENGHT = args.dataset_lenght
    MIN_NUM_PEOPLE_X_FLOOR = args.min_num_people_x_floor
    MAX_NUM_PEOPLE_X_FLOOR = args.max_num_people_x_floor
    MIN_AVG_AGE_X_FLOOR = args.min_avg_age_x_floor
    MAX_AVG_AGE_X_FLOOR = args.max_avg_age_x_floor


def load_business_rules():
    """Load business rules.

    Raises:
        ValueError: if value greater that 1.
        ValueError: if value greater that 1.
        ValueError: if value greater that 1.
    """
    global WEIGHT_GARAGE_1
    global WEIGHT_FLOOR_0
    global OLD_PEOPLE_LIMIT
    global WEIGHT_YOUNG
    global WEIGHT_FLOOR
    global WEIGHT_PEOPLE
    global WEIGHT_AGE
    try:
        with open('business_rules.json', 'r', encoding='utf8') as file:
            data = json.load(file)
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
    WEIGHT_GARAGE_1 = data['weight_garage_1']
    WEIGHT_FLOOR_0 = data['weight_floot_0']
    WEIGHT_YOUNG = data['weight_young']
    OLD_PEOPLE_LIMIT = data['old_people_limit']
    WEIGHT_FLOOR = data['weight_floor']
    WEIGHT_PEOPLE = data['weight_people']
    WEIGHT_AGE = data['weight_age']

    if WEIGHT_GARAGE_1 + WEIGHT_FLOOR_0 > 1:
        raise ValueError("'weight_garage_1 + weight_floot_0' value in JSON file must be lower or "\
                         "equal than 1")
    if WEIGHT_YOUNG > 1:
        raise ValueError("weight_young value in JSON file must be lower or equal than 1")
    if WEIGHT_FLOOR + WEIGHT_PEOPLE + WEIGHT_AGE > 1:
        raise ValueError("'weight_floor + weight_people + weight_age' value in JSON file " \
                         "must be lower or equal than 1")


def generate_weight_age_list():
    """Generate a weight list for the average age in each floor. People older than 
    `OLD_PEOPLE_LIMIT` have less likely to use the elevetor than young people. 

    Returns:
        list: Weight list for average age.
    """
    # count amount of older
    count = len([i for i in avg_age_x_floor_list if i >= OLD_PEOPLE_LIMIT])
    # list with weight per age, initialized all floor with same weight
    extra_floor = 1
    if WEIGHT_GARAGE_1 > 0:
        extra_floor += 1
    age_weight_list = [1 / (TOTAL_FLOOR)] * len(avg_age_x_floor_list)
    age_weight_list[0] = 0
    if WEIGHT_GARAGE_1 > 0:
        age_weight_list[1] = 0

    # old factor to substract older position in list per floor
    factor_old = (1 - WEIGHT_YOUNG) / count
    # young factor to add younger position in list
    factor_young = WEIGHT_YOUNG / (TOTAL_FLOOR - count)

    # create age weight list
    for i in range(extra_floor, TOTAL_FLOOR + extra_floor):
        if avg_age_x_floor_list[i] >= OLD_PEOPLE_LIMIT:
            age_weight_list[i] = age_weight_list[i] * (1 - factor_old)
        else:
            age_weight_list[i] = age_weight_list[i] * (1 + factor_young)

    return age_weight_list


def generate_weight_floor_list():
    """Generate a weight list for each floor. Floor 0 more likely to go, set in business rules. 
    Other floors contain the rest of the porcentage. The sum of all elements equal 1"""
    weight_x_floor = round(((1 - (WEIGHT_FLOOR_0 + WEIGHT_GARAGE_1)) / (TOTAL_FLOOR)), 3)
    # weight_floor_0 = 1 - weight_x_floor * (TOTAL_FLOOR)
    extra_floor = 1
    if WEIGHT_GARAGE_1 > 0:
        extra_floor += 1
    weights = [weight_x_floor] * (TOTAL_FLOOR + extra_floor)
    weights[0] = WEIGHT_FLOOR_0
    if WEIGHT_GARAGE_1 > 0:
        weights[1] = WEIGHT_GARAGE_1
    return weights


def generete_weight_avg_people_x_floor():
    """Generate a weight list for people per floor. More people living in a floor, more likely 
    to use the elevator. Sum of all elements equal 1"""
    sum_value = sum(avg_people_x_floor_list)
    return_list = [element/sum_value for element in avg_people_x_floor_list]
    return return_list



def generate_next_floor_list(dataset_lenght: int, weights_list: list):
    """Generate a list of floor number based on a weight list.

    Args:
        dataset_lenght (int): Dataset lenght.

    Returns:
        list: _description_
    """
    # 10 floor + 1 ground floor + 1 garage= list of 12 floor if WEIGHT_GARAGE_1 > 0
    extra_floor = 1
    if WEIGHT_GARAGE_1 > 0:
        extra_floor += 1
    floor_list = [np.random.choice(a=np.arange(0, TOTAL_FLOOR + extra_floor), p=weights_list)
                  for i in range(dataset_lenght)]

    return floor_list


def generate_demanding_floor_list(dataset_lenght: int, weight_floor_list: list,
                                  weigth_avg_people_x_floor: list,
                                  weigth_avg_age_x_floor: list, next_floor_list: list):
    """Generate a weight list for the demanding floor. This list depend on `weights_floor_list`
    affected by a business rule call `WEIGHT_FLOOR`, `weigth_avg_people_x_floor` affected by a 
    business rule call `WEIGHT_PEOPLE` and `weigth_avg_age_x_floor` affected by a business rule 
    call `WEIGHT_AGE`.

    Args:
        dataset_lenght (int): Dataset lenght.
        weights_floor_list (list): Weight per floor list. 
        weigth_avg_people_x_floor (list): Weight per avg people per floor list.
        weigth_avg_age_x_flor (list): Weight per avg age per floor list.
        next_floor_list (list): Next floor list. It cannot be called for the same floor.

    Returns:
        list: Demanding floor list.
    """
    weight_demanding_floor = []

    # weight demanding floor depending on avg people per floor, weight per floor and
    # avg age per floor
    for i, (weight_floor, weight_avg_people, weigth_avg_age) in enumerate(zip(weight_floor_list,
                                                                          weigth_avg_people_x_floor,
                                                                          weigth_avg_age_x_floor)):
        weight_demanding_floor.append((weight_floor * WEIGHT_FLOOR +
                                       weight_avg_people * WEIGHT_PEOPLE +
                                       weigth_avg_age * WEIGHT_AGE))

    # correct weights because choice function need the sum of weight = 1 and due to decimal sometime
    # it does not happend. Sum or substract the same amount for each floor.
    aux_var = 1 - sum(weight_demanding_floor)
    extra_floor = 1
    if WEIGHT_GARAGE_1 > 0:
        extra_floor += 1
    if aux_var != 0:
        for i in range(extra_floor, len(weight_demanding_floor)):
            weight_demanding_floor[i] += aux_var / TOTAL_FLOOR

    demand_list = []
    for i in range(dataset_lenght):
        while True:
            demand_floor = np.random.choice(a=np.arange(0, TOTAL_FLOOR + extra_floor),
                                            p=weight_demanding_floor)
            if demand_floor != next_floor_list[i]:
                demand_list.append(demand_floor)
                break

    return demand_list


def generate_datetime_list():
    """Generate datetime list.

    Returns:
        list: Datetime list.
    """
    date_list = pd.date_range(start=dt.datetime.today(), periods=DATASET_LENGHT, freq='T')
    dt_lst= [element.to_pydatetime() for element in list(date_list)]
    return dt_lst


def save_data(next_f_list, demand_f_list, date_time_list):
    """Save data into DB.

    Args:
        next_f_list (list): Next floor list.
        demand_f_list (list): Demanding floor list.
        date_time_list (list): Timestamp list.
    """
    for next_floor, demand_floor, datetime in zip(next_f_list, demand_f_list, date_time_list):
        db_element = ElevatorModel(
            next_floor=next_floor,
            demand_floor=demand_floor,
            call_datetime=datetime
        )
        db_element.save()


if __name__ == '__main__':
    load_business_rules()

    setup_entry_variables()

    avg_people_x_floor_list = np.random.randint(low=MIN_NUM_PEOPLE_X_FLOOR,
                                                high=MAX_NUM_PEOPLE_X_FLOOR, size=TOTAL_FLOOR)
    avg_age_x_floor_list = np.random.randint(low=MIN_AVG_AGE_X_FLOOR, high=MAX_AVG_AGE_X_FLOOR,
                                             size=TOTAL_FLOOR)
    # Insert ground floor
    avg_people_x_floor_list = np.insert(avg_people_x_floor_list, 0, 0, axis=0)
    avg_age_x_floor_list = np.insert(avg_age_x_floor_list, 0, 0, axis=0)
    # Insert garage floor
    if WEIGHT_GARAGE_1 > 0:
        avg_people_x_floor_list = np.insert(avg_people_x_floor_list, 0, 0, axis=0)
        avg_age_x_floor_list = np.insert(avg_age_x_floor_list, 0, 0, axis=0)

    print("People per floor list")
    print(avg_people_x_floor_list)
    print("Average age per floor")
    print(avg_age_x_floor_list)

    weights_floor_list = generate_weight_floor_list()
    weigth_avg_people_x_floor = generete_weight_avg_people_x_floor()
    weigth_avg_age_x_flor = generate_weight_age_list()

    print("Weight floor list")
    print(weights_floor_list)
    print("Weight average people per floor list")
    print(weigth_avg_people_x_floor)
    print("Weight average age per floor list")
    print(weigth_avg_age_x_flor)

    next_floor_list = generate_next_floor_list(DATASET_LENGHT, weights_floor_list)
    print("Next floor list")
    print(next_floor_list)
    print("Demanding floor list")
    demand_floor_list = generate_demanding_floor_list(DATASET_LENGHT, weights_floor_list,
                                                      weigth_avg_people_x_floor,
                                                      weigth_avg_age_x_flor,
                                                      next_floor_list)
    print(demand_floor_list)
    datetime_list = generate_datetime_list() 
    save_data(next_floor_list, demand_floor_list, datetime_list)
