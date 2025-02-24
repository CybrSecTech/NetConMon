NetConMon - Network Connection Monitor

NetConMon is a real-time network connection monitoring tool that tracks both TCP and UDP connections on your system. It provides a user-friendly graphical interface for monitoring, analyzing, and exporting network connection data.

FEATURES

NetConMon includes real-time monitoring of TCP and UDP connections, a graphical user interface with connection statistics, automatic data backup, export capabilities to CSV and TXT formats, protocol filtering for TCP/UDP, connection tracking with timestamps, and administrative privilege enforcement for accurate monitoring.

SYSTEM REQUIREMENTS

The program requires Python 3.7 or higher and can run on Windows 7/8/10/11, macOS 10.12 or higher, or most modern Linux distributions. Administrative privileges are required to run the program.

INSTALLATION

Windows Installation:
1. Double-click install.bat
2. If prompted, select "Run as administrator"
3. Follow the on-screen instructions
4. If Python is not installed, the installer will guide you to download it

macOS/Linux Installation:
1. Open Terminal
2. Navigate to the NetConMon directory
3. Run: chmod +x install.sh
4. Run: sudo ./install.sh
5. Follow the on-screen instructions

Required Python Packages:
psutil >= 5.9.0
Pillow >= 9.0.0
tk >= 0.1.0

These packages will be automatically installed during the installation process.

USAGE

Starting the Program:

For Windows:
Right-click on netconmongui.py and select "Run as administrator"

For macOS/Linux:
Open Terminal
Navigate to the NetConMon directory
Run: sudo python3 netconmongui.py

Main Interface:
The main window provides two options: "Run" to start the monitoring interface and "Info" to open this documentation.

Monitoring Interface:
The monitoring window includes Start/Stop buttons to begin or end monitoring, an Export button to save connection data to a selected location, filter checkboxes to toggle TCP/UDP connection display, connection counts to view total, TCP, and UDP connection statistics, and a log area to view real-time connection information.

Data Export:
The program automatically backs up data during monitoring and provides export options in both CSV format (spreadsheet-compatible) and TXT format (human-readable). Users can choose a custom export location using the Export button.

BACKUP SYSTEM

The program performs automatic backups every 5 seconds during monitoring. Backups are stored in the 'backups' folder within the program directory. A final backup is created when monitoring stops. The Export function allows saving to custom locations.

TROUBLESHOOTING

Common Issues:

"Access Denied" error:
Make sure you're running the program with administrator/root privileges.

Python not found:
Ensure Python 3.7+ is installed
Verify Python is added to system PATH
Run installer again

GUI doesn't appear:
Check Tkinter installation
Verify Python installation is complete
Run installer to fix missing dependencies

Export fails:
Check write permissions in target directory
Ensure enough disk space is available

Getting Help:
If you encounter issues not covered here, first check that all requirements are met, verify administrative privileges, try reinstalling the program using the installer, and check system logs for error messages.

For additional support or to report issues, please contact info@cybrsec.tech

DATA PRIVACY

NetConMon only monitors connection metadata. No packet content is captured or stored. All data is stored locally on your machine, and no data is transmitted to external servers.

LICENSE

NetConMon is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program (see COPYING.txt). If not, see https://www.gnu.org/licenses/.

OWNERSHIP

NetConMon is currently owned and maintained by CybrSec LLC. For any questions regarding usage and distribution rights, please contact CybrSec LLC at info@cybrsec.tech.

DISCLAIMER

This tool is for network monitoring and analysis purposes only. Users are responsible for ensuring they have necessary permissions to monitor network connections on their systems.