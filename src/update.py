import requests
from setup_files.colors import *
import sys
import glob
import os
import shutil
import zipfile

def download_latest_version(url_base='http://durandm.iiens.net/docs/edt-update-files/', base_save_path='./setup_files/', chunk_size=128):
        print(
            f"\n-----------------\n{bcolors.OKCYAN}Downloading latest version from {url_base}...{bcolors.ENDC}")
        os.makedirs(base_save_path + 'update_files/')
        base_save_path += 'update_files/'
        for fichier in ['EDTExtractor.py', 'update.py', 'README.md', 'README.html']:
            try:
                r = requests.get(url_base+f'{fichier}', stream=True)
                print(
                    f"{bcolors.OKGREEN}Downloaded!{bcolors.ENDC}")
            except:
                print(f"{bcolors.FAIL}ERROR: {url_base}{fichier}' -> BAD URL{bcolors.ENDC}")
                print(f"\n{bcolors.WARNING}Program aborting...{bcolors.ENDC}")
                sys.exit(0)

            try:
                with open(base_save_path+f'{fichier}', 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        fd.write(chunk)
                print(
                    f"{bcolors.OKGREEN}\nLatest version saved to temporary files!{bcolors.ENDC}")
            except:
                print(f"{bcolors.FAIL}ERROR: IMPOSSIBLE TO SAVE FILE {fichier}{bcolors.ENDC}")
                print(f"\n{bcolors.WARNING}Program aborting...{bcolors.ENDC}")
                sys.exit(0)


def save_current_version(src="../src/", dst="../previous_version/", symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = src + item
        d = dst + item
        if not(os.path.isdir(s)):
            if os.path.exists(d):
                os.remove(d)
            if(s.split('/')[-1] == 'EDTExtractor.py' or s.split('/')[-1] == 'update.py'):
                shutil.copyfile(s, d)
        else:
            pass


def install_new_version(base_update_files='./setup_files/update_files/'):
    pass
    print(f"\n-----------------\n{bcolors.OKCYAN}Installing new version from {base_update_files}...{bcolors.ENDC}")
                
    for item in os.listdir(base_update_files):
        s = base_update_files + item
        if(item != 'README.md' and item != 'README.html'):
            d = './' + item
        else:
            d = '../' + item
        if os.path.exists(d):
            os.remove(d)
        shutil.copyfile(s, d)
    shutil.rmtree(base_update_files, ignore_errors=True)
    print(f"{bcolors.OKGREEN}\nLatest version installed!{bcolors.ENDC}")

    


#-------------------------------------------------------------
def manual_update():
    print(f"\n-----------------\n{bcolors.OKCYAN}Manual Update mode...{bcolors.ENDC}(todo)")
    if(input("Do you want to ignore copy of current version? (y/N)")!='y'):
        try:
            print(
                f"\n-----------------\n{bcolors.OKCYAN}Copying previous version...{bcolors.ENDC}")
            save_current_version()
            print(
                f"{bcolors.OKGREEN}\nCurrent version saved to \'previous_version/\'!{bcolors.ENDC}")
        except Exception as e:
            print(f"{bcolors.FAIL}ERROR: IMPOSSIBLE TO COPY PREVIOUS VERSION -> {e}{bcolors.ENDC}")
            print(f"\n{bcolors.WARNING}Program aborting...{bcolors.ENDC}")
            sys.exit(0)
    else:
        print(
            f"{bcolors.OKGREEN}\nIgnoring copy of current version...{bcolors.ENDC}")
    file_path = input(
        f"{bcolors.WARNING}Please enter the path to the installation file (.zip): \n{bcolors.ENDC}")
    if(file_path!=""):
        install_new_version(file_path)
    else:
        print(f"{bcolors.FAIL}ERROR: IMPOSSIBLE TO INSTALL NEW VERSION: {file_path} BAD PATH{bcolors.ENDC}")
        print(f"\n{bcolors.WARNING}Program aborting...{bcolors.ENDC}")
        sys.exit(0)

def auto_update():
    print(f"\n-----------------\n{bcolors.OKCYAN}Auto Update mode...{bcolors.ENDC}(todo)")
   
    try:
        print(
            f"\n-----------------\n{bcolors.OKCYAN}Copying previous version...{bcolors.ENDC}")
        save_current_version()
        print(
            f"{bcolors.OKGREEN}\nCurrent version saved to \'previous_version/\'!{bcolors.ENDC}")
    except Exception as e:
        print(f"{bcolors.FAIL}ERROR: IMPOSSIBLE TO COPY PREVIOUS VERSION -> {e}{bcolors.ENDC}")
        print(f"\n{bcolors.WARNING}Program aborting...{bcolors.ENDC}")
        sys.exit(0)
    download_latest_version()
    install_new_version()
