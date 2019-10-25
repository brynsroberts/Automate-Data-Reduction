#!/usr/bin/env python

""" msflo.py: Puts reduced dataset through Fiehn lab ms-flo web service """

__author__ = "Bryan Roberts"

import os
import time
import zipfile
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def msflo(file_path, CHROME_DRIVER_DIRECTORY, DOWNLOADS_DIRECTORY):
    """ puts file through online Fiehn lab ms-flo software
    Parameters:
            file_path (str): Full directory path of file to be analyzed
            CHROME_DRIVER_DIRECTORY (str): Full directory path to Chrome driver
            DOWNLOADS_DIRECTORY (str): Full directory path to downloads folder
    Returns:
            None
    """

    # open ms-flo in chrome browser
    browser = webdriver.Chrome(
        executable_path=CHROME_DRIVER_DIRECTORY)
    browser.get("https://msflo.fiehnlab.ucdavis.edu/#/submit")

    # select ms-dial button
    msdial_button = browser.find_element_by_xpath(
        "/html/body/div/div/form/div[2]/div/div[2]/label/input")
    msdial_button.click()

    # input file
    browse = browser.find_element_by_xpath(
        "/html/body/div/div/form/div[3]/div/span/span/input")
    browse.send_keys(file_path)

    # unclick contaminant ion removal button
    contaminant_ion_removal_button = browser.find_element_by_xpath(
        "/html/body/div/div/form/div[5]/div[2]/label/input")
    contaminant_ion_removal_button.click()

    # unclick adducts button
    adducts_button = browser.find_element_by_xpath(
        "/html/body/div/div/form/div[5]/div[15]/label/input")
    adducts_button.click()

    # update duplicates form
    dup_peak_height = browser.find_element_by_xpath(
        "/html/body/div/div/form/div[5]/div[8]/input")
    dup_peak_height.send_keys('500')

    dup_rt_tolerance = browser.find_element_by_xpath(
        "/html/body/div/div/form/div[5]/div[7]/input")
    dup_rt_tolerance.send_keys('0.05')

    dup_mz_tolerance = browser.find_element_by_xpath(
        "/html/body/div/div/form/div[5]/div[6]/input")
    dup_mz_tolerance.send_keys('0.005')

    dup_min_peak_match_ratio = browser.find_element_by_xpath(
        "/html/body/div/div/form/div[5]/div[9]/input")
    dup_min_peak_match_ratio.send_keys('0.7')

    # update isotope form
    isotope_match = browser.find_element_by_xpath(
        "/html/body/div/div/form/div[5]/div[13]/input")
    isotope_match.send_keys('0.7')

    # create download file path with ms-flo created filename concatenated onto
    # folder directory
    download_file_path = create_download_file_path(
        file_path, DOWNLOADS_DIRECTORY)

    # click submit button
    submit_button = browser.find_element_by_xpath(
        "/html/body/div/div/form/div[6]/input")
    submit_button.click()

    # will not close chrome browser until file is finished downloading
    wait_for_downloads(download_file_path)

    # unzip downloaded file and send to original filepath
    unzip_msflo_file(download_file_path, os.path.dirname(file_path))
    print(f"ms-flo complete: {os.path.dirname(file_path)}")


def wait_for_downloads(final_download_file_path):
    """ keeps chrome open while files download from ms-flo
    Parameters:
            download_file_path (str): downloads folder for system being used
    Returns:
            None
    """

    # while the file does not exist in the directory, keep the browser open
    while not os.path.exists(final_download_file_path):
        time.sleep(1)


def unzip_msflo_file(download_file_path, send_to_file_path):
    """ unzips files and puts them in directory of original file
    Parameters:
            download_file_path (str): downloads folder for system being used
            send_to_file_path (str): Full directory path to send unzipped files
    Returns:
            None
    """

    with zipfile.ZipFile(download_file_path, 'r') as zip_ref:
        zip_ref.extractall(send_to_file_path)


def create_download_file_path(file_path, download_file_path):
    """ creates filepath in downloads directory with correct file name concatenated
    Parameters:
            file_path (str): Full directory path of file to be analyzed
            download_file_path (str): downloads folder for system being used
    Returns:
            final_download_path (str): download folder path with ms-flo .zip file name concatenated
    """

    assert (os.path.isdir(download_file_path)
            ), "download_file_path is not a directory"

    # convert .txt filename to .zip file name
    file_name = os.path.basename(file_path)
    file_name_zip = file_name[:len(file_name) - 4] + ".zip"

    # join .zip filename with download path directory
    final_download_path = os.path.join(download_file_path, file_name_zip)

    # make sure file path is valid
    assert(not os.path.exists(final_download_path)
           ), f"{final_download_path} already exists"

    return final_download_path

def create_excel_file(file_path):
    """ updates values from msflo output and creates excel file
    Parameters:
            file_path (str): Full directory path of file to be analyzed
    Returns:
            file (data_frame): data frame of currated msflo output
    """

    # name of processed file from msflo
    processed_name = file_path[:len(file_path) - 4] + "_processed.txt"

    # read in msflo processed file
    file = pd.read_csv(processed_name, sep='\t')
    
    # update name to get rid of "_" characters from duplicate combination
    new_name = [name[:-1] if type(name) == str and name[-1] == "_" else name for name in file['Metabolite name']]
    new_name = [name[1:] if type(name) == str and len(name) > 0 and name[0] == "_" else name for name in new_name]
    file['Metabolite name'] = new_name
    
    # determine mode of data analysis
    mode = file_path.split("_")[2][:3]

    # change blank species to [M+H]+ if no value
    if mode == "pos":
        
        species = ["[M+H]+" if type(species) != str else species for species in file['Adduct type']]
    
    # change blank species to [M-H]- if no value
    elif mode == "neg":
        
        species = ["[M-H]-" if type(species) != str else species for species in file['Adduct type']]
    
    # update data frame
    file['Adduct type'] = species

    return file

def create_single_point_file (file_path, file):
    """ generates excel file to be put through single point iSTD quant script
    Parameters:
            file_path (str): Full directory path of file to be analyzed
            file (data_frame): currated file to be put into format for single point quant
    Returns:
            None
    """

    # create data frame exculding unknowns
    # file = file[(file['Type'] == 'iSTD') | (file['Type'] == 'known')]
    
    # set adducts dictionary depending on method being analyzed
    if "posCSH" in file_path:

        adducts = {'CE': '[M+Na]+',
        'Cer': '[M+H]+',
        'Cholesterol': '[M+H-H2O]+',
        'DAG': '[M+Na]+',
        'LPC': '[M+H]+',
        'LPE': '[M+H]+',
        'PC': '[M+H]+',
        'PE': '[M+H]+',
        'SM': '[M+H]+',
        'TAG': '[M+NH4]+'}
        
    elif "negCSH" in file_path:
    
        adducts = {"FA": "[M-H]-",
        "Ceramide": "[M+Cl]-",
        "PG": "[M-H]-",
        "LPC": "[M+CH3COO]-",
        "LPE": "[M-H]-",
        "PC": "[M+CH3COO]-",
        "PE": "[M-H]-",
        "SM": "[M+CH3COO]-",
        "5-PAHSA-d9": "[M-H]-",
        "PI": "[M-H]-",
        "PS": "[M-H]-"}
        
    elif "posHILIC" in file_path:
        
        adducts = {"D3-Creatinine": "[M+H]+",
                    "D9-Choline": "[M]+",
                    "D9-TMAO": "[M+H]+",
                    "D3-1-Methylnicotinamide": "[M]+",
                    "D8-Tryptophan": "[M+H]+",
                    "D8-Phenylalanine": "[M+H]+",
                    "Val-Tyr-Val": "[M+H]+",
                    "D10-Leucine": "[M+H]+",
                    "D3-ACar(2:0)": "[M+H]+",
                    "D10-Isoleucine": "[M+H]+",
                    "D9-Betaine": "[M+H]+",
                    "D3-Histamine,": "[M+H]+",
                    "D8-Methionine": "[M+H]+",
                    "D7-Tyrosine": "[M+H]+",
                    "D8-Valine": "[M+H]+",
                    "D7-Proline": "[M+H]+",
                    "D3-L-Carnitine": "[M+H]+",
                    "D4-Alanine": "[M+H]+",
                    "D3-Creatine": "[M+H]+",
                    "D5-Threonine": "[M+H]+",
                    "D5-L-Glutamine": "[M+H]+",
                    "D3-Asparagine": "[M+H]+",
                    "D3-Serine": "[M+H]+",
                    "D5-Glutamic": "[M+H]+",
                    "D3-Aspartic": "[M+H]+",
                    "D5-Histidine": "[M+H]+",
                    "D7-Arginine": "[M+H]+",
                    "D8-Lysine": "[M+H]+",
                    "D2-Ornithine": "[M+H]+",
                    "D4-Cystine": "[M+H]+"}

    # generated to hold class number pairs
    standards = {}

    # will hold number associated with class for all knowns
    iSTD_match = []

    # set to true of false if adduct and species are not in standards
    drop = []
    
    # generate standards dictionary for CSH methods
    i = 1
    for name, adduct in zip(file['Metabolite name'], file['Adduct type']):
    
        try:
            
            name = name.split()[0]

            if name[:2] == "1_":
        
                name = name.split("_")[1]

        except:

            name = ""
    
        if "CSH" in file_path and name not in standards:
        
            standards[name] = i
            i += 1
        
        #generate standards dictionary for HILIC method
        elif "HILIC" in file_path:

            for key in adducts.keys():

                if name in key and name != "":

                    name = key
                    break

            if name not in standards:

                standards[name] = i
                i += 1
                
        iSTD_match.append(standards[name])
    
        # determine if feature will be dropped from data_frame
        if name in adducts and name != "":
        
            if adducts[name] in adduct:
        
                drop.append(True)
        
            else:
            
                drop.append(False)
    
        else:
        
            drop.append(False)

    # create new file path name   
    file_name = file_path[:len(file_path) - 18] + "_processed.xlsx"

    # add iSTD match and drop to data_frame     
    file.insert(9, 'iSTD Type', iSTD_match)
    file.insert(8, 'Keep for iSTD Single Point Quant', drop)

    # create excel file and output to console completion of task
    file.to_excel(file_name, index=False)
    print(f"file saved: {file_name}")
