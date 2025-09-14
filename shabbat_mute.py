#!/usr/bin/env python3
"""
Shabbat Laptop Mute Script for macOS
Automatically mutes laptop on Shabbat start and unmutes when Shabbat ends.
Self-manages crontab entries dynamically based on Shabbat times.
"""

import os
import sys
import json
import requests
import subprocess
import time
from datetime import datetime, timedelta
from crontab import CronTab
import logging

# Configuration
SCRIPT_PATH = "/Users/morph13nd/scripts/python/shabbat_mute.py"
LOG_FILE = "/Users/morph13nd/scripts/python/shabbat_mute.log"
LOCATION = "New York, NY"  # Adjust as needed
GEONAME_ID = "5128581"  # New York City GeoNames ID
HAVDALAH_MINUTES = 50  # Minutes after sunset for Havdalah

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def run_applescript(script):
    """Execute AppleScript command"""
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"AppleScript error: {e}")
        return None

def get_current_volume():
    """Get current input volume level"""
    script = "input volume of (get volume settings)"
    result = run_applescript(script)
    return int(result) if result and result.isdigit() else 0

def mute_microphone():
    """Mute the microphone input"""
    current_volume = get_current_volume()
    if current_volume > 0:
        # Store current volume in a file for later restoration
        volume_file = "/tmp/shabbat_volume_store"
        with open(volume_file, 'w') as f:
            f.write(str(current_volume))

        # Mute the microphone
        script = "set volume input volume 0"
        run_applescript(script)
        logging.info(f"Microphone muted. Previous volume: {current_volume}")
        return True
    else:
        logging.info("Microphone already muted")
        return False

def unmute_microphone():
    """Unmute the microphone input"""
    volume_file = "/tmp/shabbat_volume_store"

    # Try to restore previous volume, default to 75 if not found
    try:
        with open(volume_file, 'r') as f:
            previous_volume = int(f.read().strip())
        os.remove(volume_file)  # Clean up
    except (FileNotFoundError, ValueError):
        previous_volume = 75  # Default volume

    script = f"set volume input volume {previous_volume}"
    run_applescript(script)
    logging.info(f"Microphone unmuted. Volume restored to: {previous_volume}")

def get_shabbat_times():
    """Fetch Shabbat times from Hebcal API"""
    try:
        url = f"https://www.hebcal.com/shabbat?cfg=json&geonameid={GEONAME_ID}&M=on&m={HAVDALAH_MINUTES}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        items = data.get('items', [])

        candle_lighting = None
        havdalah = None

        for item in items:
            if item.get('category') == 'candles':
                candle_lighting = item.get('date')
            elif item.get('category') == 'havdalah':
                havdalah = item.get('date')

        if candle_lighting and havdalah:
            # Convert to datetime objects
            candle_time = datetime.fromisoformat(candle_lighting.replace('Z', '+00:00'))
            havdalah_time = datetime.fromisoformat(havdalah.replace('Z', '+00:00'))

            # Convert to local time (assuming ET)
            candle_time = candle_time.replace(tzinfo=None) - timedelta(hours=4)  # EDT offset
            havdalah_time = havdalah_time.replace(tzinfo=None) - timedelta(hours=4)

            return candle_time, havdalah_time
        else:
            logging.error("Could not parse Shabbat times from API response")
            return None, None

    except Exception as e:
        logging.error(f"Error fetching Shabbat times: {e}")
        return None, None

def update_crontab(candle_time, havdalah_time):
    """Update crontab with new Shabbat times"""
    try:
        cron = CronTab(user=True)  # Current user's crontab

        # Remove existing Shabbat mute jobs
        cron.remove_all(comment='shabbat_mute_start')
        cron.remove_all(comment='shabbat_mute_end')

        # Add new job for Shabbat start (mute)
        start_job = cron.new(command=f'cd /Users/morph13nd/scripts/python && python3 {SCRIPT_PATH} mute', 
                           comment='shabbat_mute_start')
        start_job.setall(candle_time)

        # Add new job for Shabbat end (unmute and reschedule)
        end_job = cron.new(command=f'cd /Users/morph13nd/scripts/python && python3 {SCRIPT_PATH} unmute_and_reschedule', 
                         comment='shabbat_mute_end')
        end_job.setall(havdalah_time)

        # Write changes
        cron.write()

        logging.info(f"Crontab updated - Mute: {candle_time.strftime('%a %H:%M')}, "
                    f"Unmute: {havdalah_time.strftime('%a %H:%M')}")
        return True

    except Exception as e:
        logging.error(f"Error updating crontab: {e}")
        return False

def schedule_next_shabbat():
    """Schedule the next Shabbat mute/unmute cycle"""
    candle_time, havdalah_time = get_shabbat_times()

    if candle_time and havdalah_time:
        return update_crontab(candle_time, havdalah_time)
    else:
        logging.error("Failed to get Shabbat times for scheduling")
        return False

def run_mute_cycle():
    """Run the continuous mute cycle during Shabbat"""
    logging.info("Starting Shabbat mute cycle")
    mute_microphone()

    # Get Shabbat end time
    _, havdalah_time = get_shabbat_times()

    if not havdalah_time:
        logging.error("Could not determine Shabbat end time")
        return

    # Wait until Shabbat ends
    while datetime.now() < havdalah_time:
        time.sleep(300)  # Check every 5 minutes

        # Ensure microphone stays muted (in case user manually unmuted)
        current_volume = get_current_volume()
        if current_volume > 0:
            logging.info("Microphone was unmuted during Shabbat, re-muting")
            mute_microphone()

    # Shabbat is over
    unmute_microphone()
    logging.info("Shabbat ended, microphone unmuted")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        # First run - schedule next Shabbat
        logging.info("Initial setup - scheduling next Shabbat")
        if schedule_next_shabbat():
            logging.info("Successfully scheduled next Shabbat")
        else:
            logging.error("Failed to schedule next Shabbat")
        return

    command = sys.argv[1]

    if command == "mute":
        # Start Shabbat mute cycle
        run_mute_cycle()

    elif command == "unmute_and_reschedule":
        # Unmute and schedule next Shabbat
        unmute_microphone()
        if schedule_next_shabbat():
            logging.info("Successfully scheduled next Shabbat")
        else:
            logging.error("Failed to schedule next Shabbat")

    elif command == "schedule":
        # Manual scheduling
        if schedule_next_shabbat():
            logging.info("Successfully scheduled next Shabbat")
        else:
            logging.error("Failed to schedule next Shabbat")

    elif command == "test_mute":
        # Test muting
        mute_microphone()

    elif command == "test_unmute":
        # Test unmuting
        unmute_microphone()

    elif command == "status":
        # Show current status
        volume = get_current_volume()
        print(f"Current microphone volume: {volume}")

        candle_time, havdalah_time = get_shabbat_times()
        if candle_time and havdalah_time:
            print(f"Next Shabbat: {candle_time.strftime('%A %B %d, %Y at %H:%M')}")
            print(f"Ends: {havdalah_time.strftime('%A %B %d, %Y at %H:%M')}")
        else:
            print("Could not fetch Shabbat times")

    else:
        print("Usage:")
        print(f"  {sys.argv[0]}                    # Initial setup")
        print(f"  {sys.argv[0]} mute               # Start Shabbat mute cycle")
        print(f"  {sys.argv[0]} unmute_and_reschedule # End Shabbat and reschedule")
        print(f"  {sys.argv[0]} schedule            # Manually schedule next Shabbat")
        print(f"  {sys.argv[0]} test_mute           # Test muting")
        print(f"  {sys.argv[0]} test_unmute         # Test unmuting")
        print(f"  {sys.argv[0]} status              # Show current status")

if __name__ == "__main__":
    main()
