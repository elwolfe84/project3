import os
import ctypes
import sys
import win32evtlog
from datetime import datetime

# Folder to store the log files
LOG_FOLDER = r"C:\failedlogs"

def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-run the script with administrative privileges."""
    try:
        script = os.path.abspath(sys.argv[0])
        params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        sys.exit()
    except Exception as e:
        print(f"Failed to elevate permissions: {e}")
        sys.exit(1)

# Ensure the folder exists
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

def fetch_recent_failed_logins():
    """Fetch the most recent Event ID 4625 entries from the Security log."""
    log_type = "Security"
    server = "localhost"  # Local machine
    failed_logins = []

    # Open the Event Log
    handle = win32evtlog.OpenEventLog(server, log_type)
    
    # Flags for reading events (most recent first)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

    # Read events
    events = win32evtlog.ReadEventLog(handle, flags, 0)
    
    if not events:
        print("No events found in the log.")
    
    for event in events:
        if event.EventID == 4625:  # Event ID for failed logins
            event_time = event.TimeGenerated.strftime("%Y-%m-%d %H:%M:%S")
            user_info = event.StringInserts[5] if len(event.StringInserts) > 5 else "N/A"
            ip_address = event.StringInserts[18] if len(event.StringInserts) > 18 else "N/A"

            # Debugging: print out each failed login attempt
            print(f"Event Found: {event_time} | User: {user_info} | IP: {ip_address}")

            # Record details of the failed login attempt
            failed_logins.append(f"{event_time} | User: {user_info} | IP: {ip_address}")

            # Limit to the most recent 10 failed logins
            if len(failed_logins) >= 10:
                break

    # Close the Event Log
    win32evtlog.CloseEventLog(handle)
    
    if not failed_logins:
        print("No failed login attempts found.")
    
    return failed_logins

def write_log_to_file(failed_logins):
    """Write the list of failed logins to a timestamped text file."""
    if not failed_logins:
        print("No recent failed login attempts found.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(LOG_FOLDER, f"failed_logins_{timestamp}.txt")
    
    with open(file_path, "w") as f:
        f.write(f"=== Failed Login Attempts on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        for login in failed_logins:
            f.write(f"{login}\n")

    print(f"Log file created: {file_path}")

if __name__ == "__main__":
    if not is_admin():
        print("Admin privileges required. Elevating...")
        run_as_admin()

    # Main logic
    print("Fetching recent failed login attempts...")
    recent_logins = fetch_recent_failed_logins()
    write_log_to_file(recent_logins)
