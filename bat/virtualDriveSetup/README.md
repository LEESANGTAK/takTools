These files are used to set up or remove a virtual drive. Virtual drive is useful when use same file path for a project.

# Install
Copy the `virtualDriveSetup` folder to the your project directory that want to use as a drive.
```
project
└─── folder1
│   │   file01
│   │   file02
│
└─── virtualDriveSetup
    │   config_virtualDrive.ini
    │   create_virtualDrive.bat
    │   remove_virtualDrive.bat
    │   README.md
```
1. Open `config_virtualDrive.ini` file with text editor.
2. Set a drive letter and save. Default is set to `P`.
3. Run the `create_virtualDrive.bat` file.

You will see a drive you set in the `config_virtualDrive.ini` file.
```
P:
└─── folder1
│   │   file01
│   │   file02
│
└─── virtualDriveSetup
    │   config_virtualDrive.ini
    │   create_virtualDrive.bat
    │   remove_virtualDrive.bat
    │   README.md
```

# Uninstall
Run the file `remove_virtualDrive.bat`.

# License
These files are made first by **Junghoon Kang**. All rights reserved by him. I modified the files to simplify usage. You can contact to me by [ta-note.com](https://ta-note.com).