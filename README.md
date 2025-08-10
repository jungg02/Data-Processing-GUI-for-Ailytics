# Data Processing GUI for Ailytics
This GUI aims to optimize processes in the data pipeline through the consolidation of python scripts into an easy-to-use application, powered by tkinter and ttkbootstrap libraries. Pyinstaller is then used to convert the files into a single .exe application for simplicity. The GUI is able to perform various data pre-processing as well as post-processing steps in the form of label verification and checks. 

## The Functionalities of this GUI includes:
- Get Summary (returns summary of class instances)
- Image file conversion (to ".jpg")
- Search up labels (returns files containing instances of a specific class)
- Reduce file size (removal of imageData from JSON files)
- Resize image 
- General dataset checks
  - Correct file formatting (images in ".jpg" or ".jpeg", correct aspect ratio etc.)
  - Duplicate labels
  - Unknown classes
  - Invalid bbox 
  - Uncontained worker PPE (worker PPE not bounded within worker bbox)

Upon conducting a general dataset check on a given folder containing image and JSON files, the GUI will flag out files with errors found, prompting the user to make the respective changes to them, most of which can be performed within the GUI itself.  

To run the application, simply run the main code "labelcheckerbot.py" or run the .exe file in the "dist" folder found here https://drive.google.com/drive/folders/1ea3fBITeq5qFsHKCfPHlWhO82J29yoLs?usp=drive_link
