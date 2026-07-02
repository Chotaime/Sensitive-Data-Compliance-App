import csv
import os
from datetime import datetime

LOG_FILE = "audit_log.csv"


def log_event(action, filename="", details=""):

    file_exists = os.path.exists(LOG_FILE)

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Timestamp",
                "Action",
                "File",
                "Details"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            action,
            filename,
            details
        ])