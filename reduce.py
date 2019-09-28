#!/usr/bin/env python

""" reduce.py: Functions to import raw MS-Dial export into pandas data-frame and reduce the total number of features"""

__author__ = "Bryan Roberts"

import os

import numpy as np
import pandas as pd
from statistics import stdev


def filter_file(file_location):
    """ Takes in .txt file and returns data-frame with extraneous rows and columns removed

    Parameters:
            file_location (str): Full directory path of file to be analyzed

    Returns:
            data_frame (pandas data-frame): Currated data-frame containing peak heights for all samples and features

    """

    # read in .txt file and make data frame
    data_frame = pd.read_csv(file_location, sep='\t', skiprows=4)

    # columns to keep for data currations
    columns_to_keep = [
        "Average Rt(min)",
        "Average Mz",
        "Metabolite name",
        "Adduct type",
        "MS/MS assigned",
        "INCHIKEY",
        "MSI level",
        "Reverse dot product",
        "Spectrum reference file name"]

    # delete columns not needed for data curration
    for column in data_frame.columns[1: 28]:

        if column not in columns_to_keep:

            data_frame.drop(column, axis=1, inplace=True)

    # delete columns relating to MSMS files
    for column in data_frame.columns:

        if "MSMS" in column:

            data_frame.drop(column, axis=1, inplace=True)

    return data_frame


def filter_samples(data_frame, blanks, biorecs, pools, samples):
    """ Searches for sample types and adds them to associated list

    Parameters:
            data_frame (pandas data-frame):Currated data-frame containing peak heights for all samples and features
            blanks (list): List of all negative control samples from row 1
            biorecs (list): List of all biorec human plasma qc samples from row 1
            pools (list): List of all matrix matched pool qc samples from row 1
            samples (list): List of all study samples from row 1

    Returns:
            None

    """

    for col in data_frame.columns[11:]:

        if "MtdBlank" in col:

            blanks.append(col)

        elif "Biorec" in col:

            biorecs.append(col)

        elif "PoolQC" in col:

            pools.append(col)

        else:

            samples.append(col)


def determine_feature_type(data_frame):
    """ Add 'Type' row to classify each feature as iSTD, known, or unknown

    Parameters:
            data_frame (pandas data-frame):Currated data-frame containing peak heights for all samples and features

    Returns:
            None

    """

    feature_type = []

    for name in data_frame["Metabolite name"]:

        if name[:2] == "1_":

            feature_type.append('iSTD')

        elif ("Unknown" not in name) and ("w/o MS2:" not in name):

            feature_type.append('known')

        else:

            feature_type.append('unknown')

    data_frame.insert(2, 'Type', feature_type)


def add_reduction_columns(data_frame, blanks, samples):
    """ Add blank average, sample averae, sample max, sample stdev, and sample %cv columns to data-frame

    Parameters:
            data_frame (pandas data-frame):Currated data-frame containing peak heights for all samples and features
            blanks (list): List of all negative control samples from row 1
            samples (list): List of all study samples from row 1

    Returns:
            None

    """

    blank_values = []
    blank_average = []

    sample_values = []
    sample_max = []
    sample_avg = []
    sample_stdev = []
    sample_cv = []
    fold2 = []

    for i in range(0, len(data_frame.index)):

        for col in data_frame.columns[11:]:

            if col in blanks:

                blank_values.append(data_frame.at[i, col])

            elif col in samples:

                sample_values.append(data_frame.at[i, col])

        blank_average.append(sum(blank_values) / len(blank_values))
        sample_max.append(max(sample_values))
        sample_avg.append(sum(sample_values) / len(sample_values))
        sample_stdev.append(stdev(sample_values))
        sample_cv.append((sample_stdev[i - 1] / sample_avg[i - 1]) * 100)
        fold2.append(sample_max[i - 1] / blank_average[i - 1])

        blank_values.clear()
        sample_values.clear()

    data_frame['Blank Average'] = blank_average
    data_frame['Sample Average'] = sample_avg
    data_frame['Sample Max'] = sample_max
    data_frame['Fold 2'] = fold2
    data_frame['Sample stdev'] = sample_stdev
    data_frame['%CV'] = sample_cv


def create_to_be_processed_txt(
        internal_standards,
        knowns,
        unknowns,
        file_location,
        samples):
    """ recombines reduced data-frames and creates .txt file to be put through ms-flo in current directory

    Parameters:
            internal_standards (pandas data-frame): Only contains rows of type iSTD
            knowns (pandas data-frame): Only contains rows of type knowns
            unknowns (pandas data-frame): Only contains rows of type unknowns
            file_location (str): file location of original excel file to save feature reduced .txt file
            samples (list): List of all study samples from row 1

    Returns:
            None

    """

    to_be_processed = pd.concat([internal_standards, knowns, unknowns])

    delete_columns = [
        "Blank Average",
        "Sample Average",
        "Sample Max",
        "Fold 2",
        "Sample stdev",
        "%CV"]

    for column in to_be_processed:

        if column in delete_columns:

            to_be_processed.drop(column, axis=1, inplace=True)

    # create sample name to go in sample location as original .txt file put
    # into the program
    sample_information_name = extract_sample_information(samples)
    to_be_processed_path = os.path.join(
        os.path.dirname(file_location),
        sample_information_name +
        '_toBeProcessed.txt')

    # make sure to_be_processed file does not already exist
    assert(not os.path.exists(to_be_processed_path)), f"{to_be_processed_path} already exists"

    # save file as .txt for ms-flo analysis
    to_be_processed.to_csv(
        to_be_processed_path,
        header=True,
        index=False,
        sep='\t',
        mode='a')

    print(f"file save: {to_be_processed_path}")

    return to_be_processed_path


def extract_sample_information(samples):
    """ extract client name, minix, and analysis type from first sample file name

    Parameters:
            samples (list): List of all study samples from row 1

    Returns:
            str in form of client_name + "_" + client_minix + "_" + analysis

    """

    first_sample = samples[0].split('_')
    client_name = first_sample[0][0:len(first_sample[0]) - 3]
    client_minix = first_sample[1]
    analysis = first_sample[2]

    return client_name + "_" + client_minix + "_" + analysis


def validate_file_location(file_location):
    """ validates file location exists and delete quotation marks if user copied them into string

    Parameters:
            file_location (list): Full directory path of file to be analyzed

    Returns:
            file_location (str): Full directory path of file to be analyzed

    """

    # if user pastes file location with quotation marks, delete quotation marks
    if file_location[0] == "\"":

        file_location = file_location[1:len(file_location) - 1]

    assert (os.path.isfile(file_location)), "File location invalid"

    return file_location
