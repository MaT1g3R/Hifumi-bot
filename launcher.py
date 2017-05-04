s means that it's either not "
                  "installed or not in the PATH environment variable like "
                  "it should be.\n\n")
				  
        if not has_ffmpeg:
            warning("WARNING: FFMPEG not found. This means that it's either not "
                  "installed or not in the PATH environment variable like "
                  "it should be. This program is needed to run music commands, "
                  "so please install it before continue!\n\n")
        if not verify_requirements():
            error("It looks like you're missing some packages, please install them or "
			      "you won't be able to run Hifumi. For that, proceed to step 4.")
        print("Start options:\n")
        print("1. Start Hifumi with autorestart")
        print("2. Start Hifumi with no autorestart")
        print("Core options:\n")
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
