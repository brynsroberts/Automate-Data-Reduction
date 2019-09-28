
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def msflo(file_path):

    browser = webdriver.Chrome(executable_path="/Users/newuser/Desktop/chromedriver")
    browser.get("https://msflo.fiehnlab.ucdavis.edu/#/submit")

    #select ms-dial button
    msdial_button = browser.find_element_by_xpath("/html/body/div/div/form/div[2]/div/div[2]/label/input")
    msdial_button.click()

    #input file
    browse = browser.find_element_by_xpath("/html/body/div/div/form/div[3]/div/span/span/input")
    browse.send_keys(file_path)

    #unclick contaminant ion removal button
    contaminant_ion_removal_button = browser.find_element_by_xpath("/html/body/div/div/form/div[5]/div[2]/label/input")
    contaminant_ion_removal_button.click()

    #unclick adducts button
    adducts_button = browser.find_element_by_xpath("/html/body/div/div/form/div[5]/div[15]/label/input")
    adducts_button.click()

    #update duplicates form
    dup_peak_height = browser.find_element_by_xpath("/html/body/div/div/form/div[5]/div[8]/input")
    dup_peak_height.send_keys('500')

    #update isotope form
    isotope_mz_tolerance = browser.find_element_by_xpath("/html/body/div/div/form/div[5]/div[11]/input")
    isotope_mz_tolerance.send_keys('0.005')

    isotope_rt_tolerance = browser.find_element_by_xpath("/html/body/div/div/form/div[5]/div[12]/input")
    isotope_rt_tolerance.send_keys('0.01')

    isotope_match = browser.find_element_by_xpath("/html/body/div/div/form/div[5]/div[13]/input")
    isotope_match.send_keys('0.7')

    #click submit button
    submit_button = browser.find_element_by_xpath("/html/body/div/div/form/div[6]/input")
    submit_button.click()

    # keep web browser open
    input("Click enter to exit")

