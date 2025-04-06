import abc
from enum import Enum
from collections import defaultdict
from typing import List, Set
import threading

"""
Question link:
- https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/parking-lot.md

assumptions:
- plate_num is unique 
"""


class VehicleType(Enum):
    CAR = 1
    MOTOCYCLE = 2
    TRUCK = 3
    NONE = -1


class Vehicle:
    def __init__(self, plate_num):
        self.plate_num = plate_num
        self.vehicle_type = VehicleType.NONE

    def get_plate_num(self):
        return self.plate_num

    def get_vehicle_type(self):
        return self.vehicle_type


class Car(Vehicle):
    def __init__(self, plate_num):
        super().__init__(plate_num)
        self.vehicle_type = VehicleType.CAR


class Motocycle(Vehicle):
    def __init__(self, plate_num):
        super().__init__(plate_num)
        self.vehicle_type = VehicleType.MOTOCYCLE


class Truck(Vehicle):
    def __init__(self, plate_num):
        super().__init__(plate_num)
        self.vehicle_type = VehicleType.TRUCK


class ParkingLotBuilder:
    def __init__(self):
        self.levels = {}

    def reset(self):
        self.levels = {}

    def add_level(self, level: int):
        if level not in self.levels:
            self.levels[level] = {}

    def add_parking_spot(self, level: int, type: VehicleType):
        if type not in self.levels[level]:
            self.levels[level][type] = 1
        else:
            self.levels[level][type] += 1

    def get_parking_lot(self):
        return self.levels


class Director:
    def __init__(self):
        self.parking_log_builder = ParkingLotBuilder()

    def built_aws_parking_lot(self):
        self.parking_log_builder.reset()
        self.parking_log_builder.add_level(1)
        self.parking_log_builder.add_level(2)
        self.parking_log_builder.add_level(3)
        self.parking_log_builder.add_level(4)
        self.parking_log_builder.add_parking_spot(1, VehicleType.CAR)
        self.parking_log_builder.add_parking_spot(1, VehicleType.CAR)
        self.parking_log_builder.add_parking_spot(1, VehicleType.CAR)
        self.parking_log_builder.add_parking_spot(1, VehicleType.MOTOCYCLE)
        self.parking_log_builder.add_parking_spot(1, VehicleType.TRUCK)
        self.parking_log_builder.add_parking_spot(2, VehicleType.CAR)
        self.parking_log_builder.add_parking_spot(2, VehicleType.CAR)
        self.parking_log_builder.add_parking_spot(3, VehicleType.CAR)
        self.parking_log_builder.add_parking_spot(3, VehicleType.MOTOCYCLE)
        self.parking_log_builder.add_parking_spot(4, VehicleType.TRUCK)
        return self.parking_log_builder.get_parking_lot()


class ParkingLot:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        raise RuntimeError("Call get_instance() instead")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        director = Director()
        self.levels = director.built_aws_parking_lot()
        self.plate_to_vehicle = {}
        self.plate_to_level = {}

    def get_available_spot(self, type):
        for level in self.levels:
            if type in self.levels[level] and self.levels[level][type] > 0:
                return level
        raise Exception(f"No more spot available for type {type}")

    def assign(self, vehicle: Vehicle):
        if vehicle.plate_num in self.plate_to_level:
            raise Exception("vehicle is already in the parking lot")
        self.plate_to_vehicle[vehicle.plate_num] = vehicle
        level = self.get_available_spot(vehicle.get_vehicle_type())
        self.levels[level][vehicle.vehicle_type] -= 1
        self.plate_to_level[vehicle.plate_num] = level
        return level

    def release(self, vehicle: Vehicle):
        if vehicle.plate_num not in self.plate_to_level:
            raise Exception("vehicle not in parking lot")
        level = self.plate_to_level[vehicle.plate_num]
        self.levels[level] += 1
        del self.plate_to_level[vehicle.plate_num]

    def print_parking_lot(self):
        for level in self.levels:
            print(f"level: {level}")
            for type in self.levels[level]:
                print(f"\t type {type}: {self.levels[level][type]} spots")


if __name__ == "__main__":
    parking_lot = ParkingLot.get_instance()
    parking_lot.print_parking_lot()

    car_1 = Car("111")
    car_2 = Car("222")
    car_3 = Car("333")
    truck_1 = Truck("444")
    truck_2 = Truck("555")
    motor_1 = Motocycle("666")

    print(parking_lot.assign(car_1))
    print(parking_lot.assign(car_2))
    print(parking_lot.assign(car_3))
    print(parking_lot.assign(truck_1))
    print(parking_lot.assign(truck_2))
    print(parking_lot.assign(motor_1))
    parking_lot.print_parking_lot()
    print(parking_lot.assign(car_1))
