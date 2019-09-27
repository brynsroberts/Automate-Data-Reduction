#!/usr/bin/env python

""" process.py: Reduces extraneous peaks from MS-Dial import and creates file for direct MS-Flo analysis"""

__author__ =    "Bryan Roberts"

import FeatureFilter # local source

if __name__ == "__main__":

    # input file with full directory
    file_location = input("Enter full file directory including file: ")

    # fold2 for annotated compounds (sample_max/blank_average)
    known_fold2 = int(input("Enter known fold2 reduction: "))

    # fold2 for unknown compounds (sample_max/blank_average)
    unknown_fold2 = int(input("Enter unknown fold2 reduction: "))

    # annotated compounds should have a sample max greater than this value
    known_sample_max = int(
        input("Enter value which known sample max must be greater than: "))

    # unknown compounds should have a sample average greater than this value
    unknown_sample_average = int(
        input("Enter value which unknown sample average must be greater than: "))

    # make data frame from excel sheet and determine feature type
    df = FeatureFilter.filter_file(file_location)
    FeatureFilter.determine_feature_type(df)

    # find columns with matching names
    blanks = []
    biorecs = []
    pools = []
    samples = []
    FeatureFilter.filter_samples(df, blanks, biorecs, pools, samples)

    # add reduction columns
    FeatureFilter.add_reduction_columns(df, blanks, samples)

    # create data frame for each type of annotated feature
    internal_standards = df[(df['Type'] == 'iSTD')]
    knowns = df[(df['Type'] == 'known')]
    unknowns = df[(df['Type'] == 'unknown')]

    # reduce annotated features
    knowns = knowns[(knowns['Fold 2'] > known_fold2)]
    knowns = knowns[(knowns['Sample Max'] > known_sample_max)]

    # reduce unknowns
    unknowns = unknowns[(unknowns['Fold 2'] > unknown_fold2)]
    unknowns = unknowns[(unknowns['Sample Average'] > unknown_sample_average)]

    # create text file of all reduced feature for ms-flo analysis
    FeatureFilter.create_to_be_processed_txt(internal_standards, knowns, unknowns, file_location)