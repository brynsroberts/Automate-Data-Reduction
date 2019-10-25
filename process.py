#!/usr/bin/env python

""" process.py: Reduces extraneous peaks from MS-Dial import and creates file for direct MS-Flo analysis """

__author__ = "Bryan Roberts"

import os

import reduce  # local source
import msflo
import instruments
import report

if __name__ == "__main__":

    # input file with full directory
    file_location = input("Enter full file directory including file: ")

    # validate file location input
    file_location = reduce.validate_file_location(file_location)

    # default values for user directory locations
    CHROME_DRIVER_DIRECTORY = ""
    DOWNLOADS_DIRECTORY = ""

    # get locations of Chrome Driver if default is not correct
    if not (os.path.exists(CHROME_DRIVER_DIRECTORY)):

        CHROME_DRIVER_DIRECTORY = input("Enter full directory for Chrome driver: ")

        # if user put in quotation marks, delete quotation marks
        if CHROME_DRIVER_DIRECTORY[0] == "\"":

            CHROME_DRIVER_DIRECTORY = CHROME_DRIVER_DIRECTORY[1:len(CHROME_DRIVER_DIRECTORY) - 1]
        
        assert(os.path.exists(CHROME_DRIVER_DIRECTORY))

    # get location of Downloads directory if default is not correct
    if not (os.path.exists(DOWNLOADS_DIRECTORY)):

        DOWNLOADS_DIRECTORY = input("Enter full directory for Downloads folder: ")

        # if user put in quotation marks, delete quotation marks
        if DOWNLOADS_DIRECTORY[0] == "\"":

            DOWNLOADS_DIRECTORY = DOWNLOADS_DIRECTORY[1:len(DOWNLOADS_DIRECTORY) - 1]
        
        assert(os.path.exists(DOWNLOADS_DIRECTORY))

    # ask if user would like to input reduction numbers of use default values
    if instruments.user_specified_values():

        # fold2 for annotated compounds (sample_max/blank_average)
        known_fold2 = int(input("Enter known fold2 reduction: "))
        assert (known_fold2 >= 0), "known fold2 must be greater than or equal to 0"

        # fold2 for unknown compounds (sample_max/blank_average)
        unknown_fold2 = int(input("Enter unknown fold2 reduction: "))
        assert (unknown_fold2 >=
                0), "unknown fold2 must be greater than or equal to 0"

        # annotated compounds should have a sample max greater than this value
        known_sample_max = int(
            input("Enter value which known sample max must be greater than: "))
        assert(known_sample_max >=
               0), "known sample max must be greater than or equal to 0"

        # unknown compounds should have a sample average greater than this
        # value
        unknown_sample_average = int(
            input("Enter value which unknown sample average must be greater than: "))
        assert(unknown_sample_average >=
               0), "unknown sample average must be greater than or equal to 0"

    # use defualt values
    else:

        known_fold2 = 5
        unknown_fold2 = 5

        # Agilent QTOF or Sciex TTOF
        if instruments.choose_instrument():

            known_sample_max = 1000
            unknown_sample_average = 3000

        # Thermo QEHF
        else:

            known_sample_max = 10000
            unknown_sample_average = 50000

    # make data frame from excel sheet and determine feature type
    df = reduce.filter_file(file_location)
    reduce.determine_feature_type(df)

    # find columns with matching names
    blanks = []
    biorecs = []
    pools = []
    samples = []
    reduce.filter_samples(df, blanks, biorecs, pools, samples)

    # add reduction columns
    reduce.add_reduction_columns(df, blanks, samples, pools)

    # update Metabolite name, InChiKey, Species
    names = df['Metabolite name'].str.split("[", n = 1, expand = True)
    inchikey = names[1].str.split("_", n = 1, expand = True)
    species = inchikey[0]
    inchikey = inchikey[1]
    name = names[0]
    
    #update inchikey
    inchi = []
    for mzrt, msdial in zip(inchikey, df['INCHIKEY']):
    
        if mzrt != None:
        
            inchi.append(mzrt)
        
        else:
        
            inchi.append(msdial)
    
    #update species
    adduct = []        
    for mzrt, msdial in zip(species, df['Adduct type']):
    
        if mzrt != None:
        
            adduct.append("[" + mzrt)
        
        else:
        
            adduct.append(msdial)
            
    for i in range(len(name)):
    
        if name[i][-1] == "_":
            
            name[i] = name[i][:-1]
            
        if name[i][-2] == ";":
            
            name[i] = name[i][:-2]
            
     
    # update values in columns
    df['INCHIKEY'] = inchi
    df['Metabolite name'] = name
    df['Adduct type'] = adduct
    df.sort_values(by=['Metabolite name'], inplace=True)

    # create data frame for each type of annotated feature
    internal_standards = df[(df['Type'] == 'iSTD')]
    knowns = df[(df['Type'] == 'known')]
    unknowns = df[(df['Type'] == 'unknown')]

    # reduce annotated features
    knowns_before_reduction = len(knowns.index)
    knowns = knowns[(knowns['Fold 2'] > known_fold2)]
    knowns = knowns[(knowns['Sample Max'] > known_sample_max)]
    
    # reduce unknowns
    unknowns_before_reduction = len(unknowns.index)
    unknowns = unknowns[(unknowns['Fold 2'] > unknown_fold2)]
    unknowns = unknowns[(unknowns['Sample Average'] > unknown_sample_average)]
    unknowns['Metabolite name'] = ""
    unknowns['INCHIKEY'] = ""
    unknowns['Adduct type'] = ""

    # len of knowns and unknowns after reduction
    knowns_after_reduction = len(knowns.index)
    unknowns_after_reduction = len(unknowns.index)

    # make report figures
    report.number_of_features_changed(
        knowns_before_reduction,
        knowns_after_reduction,
        unknowns_before_reduction,
        unknowns_after_reduction)
    report.chart_feature_cv(internal_standards)
    report.chart_feature_cv(knowns)
    
    # create text file of all reduced feature for ms-flo analysis
    file_path = reduce.create_to_be_processed_txt(
        internal_standards, knowns, unknowns, file_location, samples)

    # perform online ms-flo analysis
    msflo.msflo(file_path, CHROME_DRIVER_DIRECTORY, DOWNLOADS_DIRECTORY)

    # creat excel file for manual curation
    after_msflo_file = msflo.create_excel_file(file_path)

    # create single point quant file 
    msflo.create_single_point_file(file_path, after_msflo_file)


