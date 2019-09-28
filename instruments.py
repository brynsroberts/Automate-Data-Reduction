#!/usr/bin/env python

""" instruments.py: provide default values for different instruments in the lab """

__author__ = "Bryan Roberts"


def user_specified_values():

    while(True):
        print("Select an option for data reduction: ")
        print("1) use default values")
        print("2) input user defined values")

        user_selection = input()

        if user_selection == "1":
            return False
        elif user_selection == "2":
            return True


def choose_instrument():

    while(True):
        print("Select an instrument: ")
        print("1) Agilent QTOF or Sciex TTOF")
        print("2) Thermo QEHF")

        user_selection = input()

        if user_selection == "1":
            return True
        elif user_selection == "2":
            return False
