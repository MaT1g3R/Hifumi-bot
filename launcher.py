from __future__ import print_function
import os
import sys
import subprocess
from pathlib import Path
try:
    import urllib.request
    from importlib.util import find_spec
except ImportError:
    pass
import platform
import webbrowser
import hashlib
import argparse
import shutil
import stat
import time
import socket
try:
    import pip
except ImportError:
    pip = None

REQS_DIR = "lib"
sys.path.insert(0, REQS_DIR)
REQS_TXT = "requirements.txt"
FFMPEG_BUILDS_URL = "https://ffmpeg.zeranoe.com/builds/"
IS_WINDOWS = os.name == "nt"
IS_MAC = sys.platform == "darwin"
IS_64BIT = platform.machine().endswith("64")
PYTHON_OK = sys.version_info >= (3, 6)
#Python 3.6 or higher due to functions not available in old pythons, specially below 3.0
BOT_VERSION = "1.0.0" #This one must be a string for the window title for Windows version

FFMPEG_FILES = { #Names encoded for md5 function
    "ffmpeg.exe"  : "e0d60f7c0d27ad9d7472ddf13e78dc89",
    "ffplay.exe"  : "d100abe8281cbcc3e6aebe550c675e09",
    "ffprobe.exe" : "0e84b782c0346a98434ed476e937764f"
}

def warning(text):
    """
    Prints a yellow warning. At the moment it's only supported for Linux and Mac.
    :return: A warning.
    """
    if IS_WINDOWS:
        print(text) #Normal white text because Windows shell doesn't support ANSI color :(
    else:
        print('\x1b[33m{}\x1b[0m'.format(text))
  
def error(text):
    """
    Prints a red error. At the moment it's only supported for Linux and Mac.
    :return: An error.
    """
    if IS_WINDOWS:
        print(text)
    else:
        print('\x1b[31m{}\x1b[0m'.format(text))

def info(text):
    """
    Prints a green info. At the moment it's only supported for Linux and Mac.
    :return: An info.
    """
    if IS_WINDOWS:
        print(text)
    else:
        print('\x1b[32m{}\x1b[0m'.format(text))

def is_internet_on():
    """
    Checks if the computer or device that the process it's executing in has stable
    Internet connection. This is done by testing the websocket.
    :return: True if Internet is present, otherwise return False.
    """
    try:
      host = socket.gethostbyname("www.google.com") #Using Google because ¯\_(ツ)_/¯
      s = socket.create_connection((host, 80), 2)
      return True
    except:
      pass
      return False

def pause():
    """
    Pauses the program.
    :return: A message to request the user to press a key to continue.
    """
    input("Press ENTER key to continue.")

def install_reqs():
    """
    Installs the required requirements for the environment.
    :return: Pip call, then exit code. 0 if everything is fine, 1 if error ocurred.
    """
    remove_reqs_readonly()
    interpreter = sys.executable

    if not interpreter:
        error("Python interpreter not found.")
        return

    txt = REQS_TXT

    args = [
        interpreter, "-m",
        "pip", "install",
        "--upgrade",
        "--target", REQS_DIR,
        "-r", txt
    ]

    if IS_MAC:
        args.remove("--target")
        args.remove(REQS_DIR)

    code = subprocess.call(args)

    if code == 0:
        info("\nPython requirements installed successfully!")
    else:
        error("\nUh oh! An error ocurred and installation is going to be aborted.\n"
             "Please fix the error above basing in the docs.\n")


def update_pip():
    """
    Updates pip, a.k.a the Python package manager.
    :return: Pip call, then exit code. 0 if everything is fine, 1 if error ocurred.
    """
    interpreter = sys.executable

    if not interpreter:
        error("Python interpreter not found.")
        return

    args = [
        interpreter, "-m",
        "pip", "install",
        "--upgrade", "pip"
    ]

    code = subprocess.call(args)

    if code == 0:
        info("\nPip updated successfully to the latest version!")
    else:
        error("\nUh oh! An error ocurred and installation is going to be aborted.\n"
             "Please fix the error above basing in the docs.\n")


def update_hifumi():
    """
    Updates Hifumi via Git. Useful if something wents wrong or if a new version comes out.
    :return: Git call, then exit code. 0 if went fine, 1 or exception if error ocurred.
    """
    try:
        code = subprocess.call(("git", "pull", "--ff-only"))
    except FileNotFoundError:
        error("\nError: Git not found. It's either not installed or not in "
              "the PATH environment variable. Please fix this!")
        return
    if code == 0:
        info("\nHifumi is now updated successfully!")
    else:
        error("\nUh oh! An error ocurred and update is going to be aborted.\n"
             "This error is caused due to environment edits you maybe made. ",
             "Please fix this by going to the maintenance menu.")


def reset_hifumi(reqs=False, data=False, cogs=False, git_reset=False):
    """
    Resets Hifumi or any of its properties (enabled to True boolean).
    If all of the parameters are enabled, Hifumi will get a 'factory reset'.
    :param reqs: Choose to reset the local packages.
    :param data: Choose to reset the data folder.
    :param cogs: Choose to reset the cogs (command modules).
    :param git_reset: Choose to replace all the environment with the latest commit.
    :return: For reqs, data, cogs. Folder removing and result or exception
    (FileNotFoundError or another). If git_reset an exit code. 0 if went fine, 1 if otherwise.
    """
    if reqs:
        try:
            shutil.rmtree(REQS_DIR, onerror=remove_readonly)
            info("Installed local packages wiped successfully!")
        except FileNotFoundError:
            pass
        except Exception as e:
            error("Uh oh! An error ocurred: {}".format(e))
    if data:
        try:
            shutil.rmtree("data", onerror=remove_readonly)
            info("'data' folder has been wiped.")
        except FileNotFoundError:
            pass
        except Exception as e:
            error("Uh oh! An error ocurred: {}".format(e))

    if cogs:
        try:
            shutil.rmtree("cogs", onerror=remove_readonly)
            info("'cogs' folder has been wiped.")
        except FileNotFoundError:
            pass
        except Exception as e:
            error("An error occurred when trying to remove the 'cogs' folder: "
                  "{}".format(e))

    if git_reset:
        code = subprocess.call(("git", "reset", "--hard"))
        if code == 0:
            info("Hifumi repaired successfully! to the last local commit. If the bot",
                  "it's started, please restart it to make effect.")
        else:
            error("The repair has failed.")


def download_ffmpeg(bitness):
    """
    Downloads FFMPEG from the official page. It's a required tool for music commands.
    :param bitness: Can be 32bit or 64bit in string. This is choosen for the download version.
    :return: FFMPEG download and a message with instructions for the first time use.
    """
    clear_screen()
    repo = "https://github.com/hifumibot/hifumibot"
    verified = []

    if bitness == "32bit":
        info("Please download 'ffmpeg 32bit static' from the page that "
              "is about to open.\nOnce done, open the 'bin' folder located "
              "inside the zip.\nThere should be 3 files: ffmpeg.exe, "
              "ffplay.exe, ffprobe.exe.\nPut all three of them into the "
              "bot's main folder.")
        time.sleep(5)
        webbrowser.open(FFMPEG_BUILDS_URL)
        return

    for filename in FFMPEG_FILES:
        if os.path.isfile(filename):
            warning("{} already present. Verifying integrity... "
                  "".format(filename), end="")
            _hash = calculate_md5(filename)
            if _hash == FFMPEG_FILES[filename]:
                verified.append(filename)
                info("Done!")
                continue
            else:
                warning("Hash mismatch. Redownloading.")
        info("Downloading {}... Please wait.".format(filename))
        with urllib.request.urlopen(repo + filename) as data:
            with open(filename, "wb") as f:
                f.write(data.read())
        info("FFMPEG downloaded! Please follow the instructions! "
              "Open the 'bin' folder located inside the zip.\nThere should "
              "be 3 files: ffmpeg.exe, ffplay.exe, ffprobe.exe.\nPut all "
              "three of them into the bot's main folder.")

    for filename, _hash in FFMPEG_FILES.items():
        if filename in verified:
            continue
        info("Verifying {}... ".format(filename), end="")
        if not calculate_md5(filename) != _hash:
            info("Passed.")
        else:
            warning("Hash mismatch. Please redownload.")

    info("\nAll files have been downloaded.")


def verify_requirements():
    """
    Verifies the status of required requirements.
    :return: False if there's missing packages. Otherwise return True.
    """
    sys.path_importer_cache = {}
    spec1 = find_spec("discord")
    spec2 = find_spec("nacl")
    if (not spec1 and not spec2) or (not spec1 and spec2) or (spec1 and not spec2):
	#This thing is too messy for my eyes >_<
        return False 
    else:
        return True


def is_ffmpeg_installed():
    """
    Checks if FFMPEG is installed by checking the current version in console.
    :return: True if command is successful, otherwise return False.
    """
    try:
        subprocess.call(["ffmpeg", "-version"], stdout=subprocess.DEVNULL,
                                              stdin =subprocess.DEVNULL,
                                              stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return False
    else:
        return True


def is_git_installed():
    """
    Checks if Git is installed by checking the current version in console.
    :return: True if command is successful, otherwise return False.
    """
    try:
        subprocess.call(["git", "--version"], stdout=subprocess.DEVNULL,
                                              stdin =subprocess.DEVNULL,
                                              stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return False
    else:
        return True


def requirements_menu():
    """
    Prints the options from the requirement menu.
    :return: The requirements menu.
    """
    clear_screen()
    while True:
        print("Main requirements:\n")
        print("1. Install basic requirements")
        if IS_WINDOWS:
            print("\nffmpeg (required for audio):")
            print("3. Install ffmpeg 32bit")
            if IS_64BIT:
                print("4. Install ffmpeg 64bit (recommended on Windows 64bit)")
        print("\n0. Go back")
        choice = user_choice()
        if choice == "1":
            install_reqs()
            pause()
        elif choice == "2" and IS_WINDOWS:
            download_ffmpeg(bitness="32bit")
            pause()
        elif choice == "3" and (IS_WINDOWS and IS_64BIT):
            download_ffmpeg(bitness="64bit")
            pause()
        elif choice == "0":
            break
        clear_screen()


def update_menu():
    """
    Prints the options from the update menu.
    :return: The update menu.
    """
    clear_screen()
    while True:
        reqs = verify_requirements()
        if reqs is False:
            status = "No requirements installed"
        else:
            status = "Requirements installed"
        print("Status: " + status + "\n")
        print("Update:\n")
        print("Environment:")
        print("1. Update bot + requirements (recommended)")
        print("2. Update bot")
        print("3. Update requirements")
        print("\nOthers:")
        print("4. Update pip (might require admin privileges)")
        print("\n0. Go back")
        choice = user_choice()
        if choice == "1":
            update_hifumi()
            print("Updating requirements...")
            reqs = verify_requirements()
            if reqs is not False:
                install_reqs()
            else:
                print("The requirements haven't been installed yet.")
            pause()
        elif choice == "2":
            update_hifumi()
            pause()
        elif choice == "3":
            reqs = verify_requirements()
            if reqs is not False:
                install_reqs()
            else:
                print("The requirements haven't been installed yet.\n"
                      "Please install them before continue!")
            pause()
        elif choice == "4":
            update_pip()
            pause()
        elif choice == "0":
            break
        clear_screen()


def maintenance_menu():
    """
    Prints the options from the maintenance menu.
    :return: The maintenance menu.
    """
    clear_screen()
    while True:
        print("Maintenance:\n")
        print("1. Repair environment (this won't include data)")
        print("2. Wipe 'data' folder")
        print("3. Wipe 'lib' folder (pip packages and libraries)")
        print("4. Factory reset (please be careful)")
        print("\n0. Go back")
        choice = user_choice()
        if choice == "1":
            warning("Any code modification you have made will be lost. Data/"
                  "non-default cogs will be left intact. Are you sure?")
            if user_pick_yes_no():
                reset_hifumi(git_reset=True)
                pause()
        elif choice == "2":
            warning("Are you sure? This will wipe the 'data' folder, which "
                  "contains all your settings and cogs' data.\nThe 'cogs' "
                  "folder, however, will be left intact.")
            if user_pick_yes_no():
                reset_hifumi(data=True)
                pause()
        elif choice == "3":
            reset_hifumi(reqs=True)
            pause()
        elif choice == "4":
            warning("Are you sure? This will wipe ALL the installation "
                  "data.\nYou'll lose all your settings, cogs and any "
                  "modification you have made.\nThere is no going back, "
                  "so please be careful and choose wisely.")
            if user_pick_yes_no():
                reset_hifumi(reqs=True, data=True, cogs=True, git_reset=True)
                pause()
        elif choice == "0":
            break
        clear_screen()


def run_hifumi(autorestart):
    """
    Prints the options from the requirement menu.
    :return: The requirements menu.
    """
    interpreter = sys.executable

    if not interpreter:
        raise RuntimeError("Couldn't find Python's interpreter")

    if not verify_requirements():
        error("You don't have the requirements that are needed to "
              "start the bot. Please install them first and try again.")
        pause()
        main()

    runScript = Path("./run.py")
    if runScript.is_file():
        pass
	#Don't worry about shard mode, that's toggleable via settings.py
    else:
        error("Hifumi's main file to run is not available. Please reinstall Hifumi!")
        pause()
        main()

    while True:
        try:
            cmd = (interpreter, "run.py")
            code = subprocess.call(cmd)
        except KeyboardInterrupt: #Triggered!
            code = 0
            break
        else:
            if code == 0:
                break
            elif code == 26:
                warning("Restarting...")
                continue
            else:
                if not autorestart:
                    break

    error("Hifumi has been terminated recently. Exit code: %d" % code)
    pause()

def incorrect_choice():
    """
    Returns an error of menu choose.
    :return: A message to the user telling that the valid (s)he choosed is invalid.
    """
    error("Incorrect choice! Please try again with a valid choice.")
    pause()

def about():
    """
    Prints the about information and the license
    :return: The about information
    """
    print("Hifumi ~The Discord bot~\n\nGeneral:"
          "Developers: Underforest#1284, InternalLight#9391, "
          "ラブアローシュート#6728\nVersion: {}".format(BOT_VERSION), "\nHelpers: Wolke#6746\n\n"
		  #RIP non-UTF8/Unicode encoding users due to 3rd developer Discord name
          "Website: http://hifumibot.xyz\n\n"
          "Copyright (c) 2017 Hifumi - the Discord Bot Project\n\n"
          "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
          "of this software and associated documentation files (the \"Software\"), to deal\n"
          "in the Software without restriction, including without limitation the rights\n"
          "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
          "copies of the Software, and to permit persons to whom the Software is\n"
          "furnished to do so, subject to the following conditions:\n\n"
          "The above copyright notice and this permission notice shall be included in all\n"
          "copies or substantial portions of the Software.\n\n"
          "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
          "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
          "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
          "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
          "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
          "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
          "SOFTWARE.\n"
          "\n\n")
    pause()


def edit_settings():
    """
    Opens settings.py file in the notepad if present.
    :return: The action or an exception if an error ocurred.
    """
    try:
          if IS_WINDOWS:
              subprocess.call(['start', 'notepad', './config/settings.py'])
          elif IS_MAC:
              subprocess.call(['open', '-a', 'TextEdit', './config/settings.py'])
          else:
              subprocess.call(['sudo', 'nano', './config/settings.py'])
    except FileNotFoundError:
          error("An error ocurred while opening the settings into editor. Please check "
                "that the 'config' folder has the file 'settings.py'. If it has the file "
                "'sample_settings.py' instead, rename it to 'settings.py', then try again. "
                "Otherwise reinstall Hifumi from zero.\n")
          pause()


def clear_screen():
    """
    Cleans the screen
    :return: The screen cleaned.
    """
    if IS_WINDOWS:
        os.system("cls")
    else:
        os.system("clear")


def user_choice():
    """
    Asks the user to choose something from the menu.
    :return: An input request
    """
    return input("> ").lower().strip()


def user_pick_yes_no():
    """
    A yes/no question to do an action.
    :return: An input request, can be yes or no.
    """
    choice = None
    yes = ("yes", "y", "Y", "YES")
    no = ("no", "n", "N", "NO")
    while choice not in yes and choice not in no:
        choice = input("Yes/No > ").lower().strip()
    return choice in yes


def remove_readonly(func, path, excinfo):
    """
    Removes the files that are read-only and causes a bug in update.
    :return: Read-only files removed.
    """
    os.chmod(path, 0o755)
    func(path)


def remove_reqs_readonly():
    """
    Removes the packages that are read-only and causes a bug in update.
    :return: Read-only packages removed.
    """
    if not os.path.isdir(REQS_DIR):
        return
    os.chmod(REQS_DIR, 0o755)
    for root, dirs, files in os.walk(REQS_DIR):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)
        for f in files:
            os.chmod(os.path.join(root, f), 0o755)


def calculate_md5(filename):
    """
    Calculates md5 output to decode from the ffmpeg files during installation.
    :return: Hex digest output into md5.
    """
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def main():
    """
    Prints the main menu.
    :return: The main menu or an exception/warning if something is wrong.
    """
    if not is_internet_on():
        print("You're not connected to Internet! Please check your "
               "connection and try again")
        exit(1)
    print("Verifying Git installation...")
    has_git = is_git_installed()
    has_ffmpeg = is_ffmpeg_installed()
    is_git_installation = os.path.isdir(".git") #Check if .git folder exists
    if IS_WINDOWS:
        os.system("TITLE Hifumi {} ~ Launcher".format(BOT_VERSION)) #Yep!

    while True:
        clear_screen()
		#ASCII art by RafisStuff (someone#3025)
        if not is_git_installation:
            warning("WARNING: This installation was not done via Git\n"
                  "You probably won't be able to update some things that "
                  "require this util, for example the bot environment. Please "
                  "read the license file for more information. "
                  "If you got this from another source, please reinstall Hifumi"
                  "as it follows in the guide. "
                  "http://www.hifumibot.xyz/docs\n\n")

        if not has_git:
            warning("WARNING: Git not found. This means that it's either not "
                  "installed or not in the PATH environment variable like "
                  "it should be.\n\n")
				  
        if not has_ffmpeg:
            warning("WARNING: FFMPEG not found. This means that it's either not "
                  "installed or not in the PATH environment variable like "
                  "it should be. This program is needed to run music commands, "
                  "so please install it before continue!\n\n")
        if not verify_requirements():
            error("It looks like you're missing some packages, please install them or "
			      "you won't be able to run Hifumi. For that, proceed to step 4.\n\n")
        print(" __    __   __   _______  __    __   ___  ___   __\n"
              "|  |  |  | |  | |   ____||  |  |  | |   \/   | |  |    _\n"
              "|  |__|  | |  | |  |__   |  |  |  | |  \  /  | |  |  _| |_\n"
              "|   __   | |  | |   __|  |  |  |  | |  |\/|  | |  | |_   _|\n"
              "|  |  |  | |  | |  |     |  `--'  | |  |  |  | |  |   |_|\n"
              "|__|  |__| |__| |__|      \______/  |__|  |__| |__|\n\n")
        print("Start options:")
        print("1. Start Hifumi with autorestart")
        print("2. Start Hifumi with no autorestart\n")
        print("Core options:")
        print("3. Update environment")
        print("4. Install requirements")
        print("5. Edit settings")
        print("6. Maintenance")
        print("7. About")
        print("\n0. Quit")
        choice = user_choice()
        if choice == "1":
             run_hifumi(autorestart=True)
        elif choice == "2":
             run_hifumi(autorestart=False)
        elif choice == "3":
            update_menu()
        elif choice == "4":
            requirements_menu()
        elif choice == "5":
            edit_settings()
        elif choice == "6":
            maintenance_menu()
        elif choice == "7":
            about()
        elif choice == "0":
            print("Are you sure you want to quit?")
            if user_pick_yes_no():
                clear_screen()
                break
            else:
                main()
        else:
            incorrect_choice()

if __name__ == '__main__':
    """
    Main function of the program
    :return: An initialization request to the program or an error if Python/pip is wrong.
    """
    abspath = os.path.abspath(__file__)
    dirname = os.path.dirname(abspath)
    os.chdir(dirname)
    if not PYTHON_OK:
        error("Sorry! This Python version is not compatible. Hifumi needs "
              "Python 3.6 or superior. Install the required version and "
              "try again.\n")
        pause()
        exit(1)
    elif not pip:
        error("Hey! Python is installed but you missed the pip module. Please"
              "install Python without unchecking any option during the setup >_<")
        pause()
        exit(1)
    else:
        info("Initializating...")
        main()
