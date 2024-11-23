#!/bin/bash

# Variables
folder="/home/student/failed_logon"
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
output_file="$folder/$timestamp.txt"
log_file="/var/log/auth.log"
email_recipient="logs@turnanewleaf.com"

# Create the folder if it doesn't exist
mkdir -p "$folder"

# Get the last 10 minutes of failed login attempts
sudo grep "authentication" "$log_file" | awk -v Date="$(date --date='10 minutes ago' '+%b %d %H:%M')" '$0 >= Date {print $0}' > "$output_file"

# Extract IP addresses and count occurrences
# using AWK command to generate the line 
awk '{print $11}' "$output_file" | sort | uniq -c | while read count ip; do
    if [ "$count" -gt 10 ]; then
        # If any IP fails login more than 10 times in the last 10 minutes, send an email
        echo "Brute force detected from IP: $ip with $count failed attempts" | mail -s "Brute Force Alert: $ip" "$email_recipient"
    fi
done

echo "Log file created: $output_file"