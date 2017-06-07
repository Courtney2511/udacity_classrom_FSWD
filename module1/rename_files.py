import os

def rename_files():
    #1 get file names from a folder
    file_list = os.listdir("/Users/courtneynoonan/Documents/Udacity/downloads/prank")
    saved_path = os.getcwd()
    print ("Current WD is " + saved_path)
    os.chdir("/Users/courtneynoonan/Documents/Udacity/downloads/prank")
    #2 for each file, rename the file
    for file_name in file_list:
        print("Old name - " + file_name)
        print("New name - " + file_name.translate(None, "0123456789"))
        os.rename(file_name, file_name.translate(None, "0123456789"))
    os.chdir(saved_path)

rename_files()
