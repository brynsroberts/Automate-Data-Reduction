# Metabolomics-Automate-Data-Reduction

## Authors

* **Bryan Roberts**

## Description: 

Automate data reduction for Metabolomics untargeted LC-MS data and put reduced dataset through online MS-FLO software.  Produces
charts to qc data quality.

## Getting Started

### Prerequisites

* This script requires python 3. Its dependencies may be installed by installing all dependencies from requirements.txt

```
pip install -r requirements.txt
```

* Download ChromeDriver for your version of Chrome

```
https://chromedriver.chromium.org/downloads
```

* Open msflo.py in a text editor and paste the full directory of chromedriver.exe into CHROME_DRIVER_DIRECTORY

```
CHROME_DRIVER_DIRECTORY = "C:\\Users\\Bryan\\Desktop\\chromedriver.exe"
```

* Also in msflo.py, paste the full directory of local Downloads folder in DOWNLOADS_DIRECTORY

```
DOWNLOADS_DIRECTORY = "C:\\Users\\Bryan\\Downloads"
```

* Sample names must be generated from

```
http://carrot.metabolomics.us/lcms
```

* Sample names must match the following format

```
* Sample name and injection number _ MiniX ID _ Analysis Type _ Sample ID - Sample Number

* ex: Bryan001_MX123456_posHILIC_ABA-01
```

### Running Script

* Run process.py

* Paste in full directory of MS-Dial alignment results .txt file

```
Enter full file directory including file: "C:\Data\Height_0_20198231532.txt"
```

* Select to use default values or user defined parameters for data reduction.  Parameters include

```
* known fold 2: sample max peak height for all samples / blank average peak height for all blanks (defualt: 5)
* unknown fold 2: sample max peak height for all samples / blank average peak height for all blanks (defualt: 5)
* Enter value which known sample max must be greater than: (default for QTOF/TTOF: 1000, QEHF: 10000)
* Enter value which unknown sample average must be greater than: (default for QTOF/TTOF: 3000, QEHF: 50000)
```
### Output

* Script will create new reduced and toBeProcessed .txt file and MS-FLO files in same directory as original MS-Dial alignment file.
* Chart displaying number of known and unknown features before and after reduction
* Chart displaying %CV of internal standards in samples and pool qc samples
* Chart displaying %CV of known features in samples and pool qc samples

## Sources

* https://automatetheboringstuff.com/
* http://prime.psc.riken.jp/Metabolomics_Software/MS-DIAL/
* https://msflo.fiehnlab.ucdavis.edu/#/submit
