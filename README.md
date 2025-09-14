# Shabbat_Laptop_PC_Mute
Need to mute your laptop or device during Shabbat? Have no fear, python is here to save the day. 

# Shabbat Laptop Mute Script for macOS

I've created a comprehensive Python script that automatically mutes your laptop when Shabbat starts and unmutes it when Shabbat ends, with dynamic crontab management throughout the year.  It's unfortunate if you need your laptop to run and do not want to shut it off, and forget to mute and sounds are playing on Shabbat. 

## Main Script Features

The script leverages the **Hebcal API** to fetch accurate Shabbat times for New York and uses **AppleScript commands** to control macOS microphone input volume. It employs the **python-crontab library** for dynamic cron job management.[1][2][3][4][5]

**Key Capabilities:**
- **Automatic Shabbat Detection**: Queries Hebcal API for precise candle lighting and Havdalah times[6][1]
- **Smart Audio Control**: Uses AppleScript to mute/unmute microphone while preserving original volume levels[2][7]
- **Self-Managing Crontab**: Dynamically updates cron entries as Shabbat times change throughout the year[3][8]
- **Continuous Monitoring**: Runs throughout Shabbat to ensure microphone stays muted
- **Robust Error Handling**: Comprehensive logging and fallback mechanisms

## How It Works

1. **Initial Setup**: Run once to schedule the first Shabbat
2. **Friday Evening**: Cron triggers script at candle lighting time, mutes microphone, enters monitoring mode
3. **Shabbat Duration**: Script continuously monitors and maintains muted state
4. **Saturday Evening**: At Havdalah time, unmutes microphone and schedules next week's Shabbat
5. **Self-Perpetuating**: Automatically adjusts for seasonal time changes

## Technical Implementation

The script uses **macOS AppleScript integration** for audio control:[7][9]
```applescript
set volume input volume 0  ```ute
set volume input```lume 75 # Unmute to```ored level
```

**Crontab management** handles dynamic scheduling:[10][8]
```python
from crontab import CronTab
cron = CronTab(user```ue)
job = cron.new(command=```ipt_command)
job.setall(sh```at_time)
```

**API integration** fetches precise times:[11][1]
```python
url = f"https://www.hebcal.com/shabbat```g=json&geonameid={GEONAME_ID```=on&m={HAVDALAH_MINUTES}"````
```

# Shabbat Laptop Mute Script - Setup Instructions

## Prerequisites
1. Install required Python packages:
   ```bash
   pip3 install requests python-crontab
   ```

## Installation Steps

1. **Create the scripts directory:**
   ```bash
   mkdir -p /Users/yourUsername/scripts/python
   ```

2. **Copy the script:**
   ```bash
   cp shabbat_mute.py /Users/yourUsername/scripts/python/
   chmod +x /Users/yourUsername/scripts/python/shabbat_mute.py
   ```

3. **Initial setup (run once):**
   ```bash
   cd /Users/yourUsername/scripts/python
   python3 shabbat_mute.py
   ```

   This will:
   - Fetch the next Shabbat times for New York
   - Create initial crontab entries
   - Set up logging

## Usage Commands

- **Check status:** `python3 shabbat_mute.py status`
- **Manual scheduling:** `python3 shabbat_mute.py schedule`
- **Test mute:** `python3 shabbat_mute.py test_mute`
- **Test unmute:** `python3 shabbat_mute.py test_unmute`

## How It Works

1. **Friday before Shabbat:** Script runs automatically via cron, mutes microphone, and enters monitoring mode
2. **During Shabbat:** Script continuously monitors and ensures microphone stays muted
3. **Saturday after Havdalah:** Script unmutes microphone and schedules next Shabbat
4. **Self-updating:** Each week, the script automatically updates crontab with new Shabbat times

## Customization

- **Location:** Change `GEONAME_ID` in the script (find your city's ID at geonames.org)
- **Havdalah time:** Adjust `HAVDALAH_MINUTES` (default: 50 minutes after sunset)
- **Log location:** Modify `LOG_FILE` path if desired

## Troubleshooting

- Check logs: `tail -f /Users/yourUsername/scripts/python/shabbat_mute.log`
- View crontab: `crontab -l | grep shabbat`
- Test API connection: Run `python3 shabbat_mute.py status`

## macOS Permissions

The script may require permission to:
- Control system audio (automatic prompt)
- Access network for API calls
- Modify crontab (should work automatically)
