# Youtube watch history to CSV

## Description

This project is a simple Python script that converts the YouTube Watch History data from Google Takeout to a CSV file. The script is written in Python 3.

## Usage

1. Download your YouTube Watch History data from Google Takeout. You can do this by going to [Google Takeout](https://takeout.google.com/) and selecting only the YouTube Watch History data.
2. Extract the downloaded archive.
3. Copy the `watch-history.html` file to the `data` directory.
4. Run the script by executing the following command in the terminal:

```bash
python src/main.py data/watch-history.html output/history.csv
```