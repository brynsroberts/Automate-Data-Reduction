#!/usr/bin/env python

""" FeatureFilter.py: Functions to import raw MS-Dial export into pandas data-frame and reduce the total number of features"""

__author__ = 	"Bryan Roberts"

import numpy as np
import pandas as pd
from statistics import stdev

def save_filepath(path):
    """ Returns file path with the excel sheet taken out of the string

	Parameters:
		path (str): Full directory path of file to be analyzed

	Returns:
		path (str): The full directory path string minus the file being analyzed

    """

    count = 0

    for letter in path[::-1]:
        if (letter == '/') or (letter == '\\'):
            break
        else:
            count += 1

    return path[:len(path) - count]

def filter_excel(file_location):
	""" Takes in excel file and returns data-frame with extraneous rows and columns removed

	Parameters:
		file_location (str): Full directory path of file to be analyzed

	Returns:
		data_frame (pandas data-frame): Currated data-frame containing peak heights for all samples and features

    """

	# read in excel file and make data frame
	try:

		data_frame = pd.read_excel(file_location, header=None, skiprows=4)

	except:

		print("File location failed")

	# drop the first 4 rows of information from the file
	data_frame.rename(columns=data_frame.iloc[0], inplace=True)
	data_frame.drop(data_frame.index[0], inplace=True)

	# columns to keep for data currations
	columns_to_keep = ["Average Rt(min)", "Average Mz", "Metabolite name", "Adduct type",
						"MS/MS assigned", "INCHIKEY", "MSI level", "Reverse dot product",
						"Spectrum reference file name"]

	# delete columns not needed for data curration
	for column in data_frame.columns[1: 29]:

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

	for i in range(1, len(data_frame.index) + 1):
    
		for col in data_frame.columns[9:]:
        
			if col in blanks:
            
				blank_values.append(data_frame.at[i,col])
            
			elif col in samples:
            
				sample_values.append(data_frame.at[i,col])
            
		blank_average.append(sum(blank_values)/len(blank_values))
		sample_max.append(max(sample_values))
		sample_avg.append(sum(sample_values)/len(sample_values))
		sample_stdev.append(stdev(sample_values))
		sample_cv.append((sample_stdev[i - 1]/sample_avg[i - 1]) * 100) 
		fold2.append(sample_max[i - 1]/blank_average[i - 1])
    
		blank_values.clear()
		sample_values.clear()

	data_frame['Blank Average'] = blank_average
	data_frame['Sample Average'] = sample_avg
	data_frame['Sample Max'] = sample_max
	data_frame['Fold 2'] = fold2
	data_frame['Sample stdev'] = sample_stdev
	data_frame['%CV'] = sample_cv

def create_to_be_processed_txt(internal_standards, knowns, unknowns, file_location):
	""" recombines reduced data-frames and creates .txt file to be put through ms-flo in current directory

	Parameters:
		internal_standards (pandas data-frame): Only contains rows of type iSTD
		knowns (pandas data-frame): Only contains rows of type knowns
		unknowns (pandas data-frame): Only contains rows of type unknowns
		file_location (str): file location of original excel file to save feature reduced .txt file

	Returns:
		None

    """

	to_be_processed = pd.concat([internal_standards, knowns, unknowns])

	delete_columns = ["Blank Average", "Sample Average", "Sample Max", "Fold 2",
					"Sample stdev", "%CV"]

	for column in to_be_processed:

		if column in delete_columns:

			to_be_processed.drop(column, axis=1, inplace=True)

	to_be_processed_path = save_filepath(file_location) + 'toBeProcessed.txt'

	to_be_processed.to_csv(to_be_processed_path, header=True, index=False, sep='\t', mode='a')
