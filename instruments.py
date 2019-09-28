#!/usr/bin/env python

""" instruments.py: provide default values for different instruments in the lab """

__author__ = "Bryan Roberts"


def user_specified_values():
    """ allows user to choose default values or input values for reduction

    Parameters:
            None

    Returns:
            bool: True is user defined values, False if default values

    """

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
    """ allows user to choose instrument default values

    Parameters:
            None

    Returns:
            bool: True is data is QTOF or TTOF, False if data is QEHF

    """

    while(True):
        print("Select an instrument: ")
        print("1) Agilent QTOF or Sciex TTOF")
        print("2) Thermo QEHF")

        user_selection = input()

        if user_selection == "1":
            return True
        elif user_selection == "2":
            return False
