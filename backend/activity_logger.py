import pandas as pd
from datetime import datetime
import os

LOG_FILE = "user_activity_log.xlsx"

def log_activity(email: str, action: str, details: str = ""):
    """
    Append a log entry to the Excel file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {
        "Timestamp": timestamp,
        "Email": email,
        "Action": action,
        "Details": details
    }
    
    try:
        if os.path.exists(LOG_FILE):
            df = pd.read_excel(LOG_FILE)
            new_df = pd.DataFrame([new_entry])
            df = pd.concat([df, new_df], ignore_index=True)
        else:
            df = pd.DataFrame([new_entry])
            
        df.to_excel(LOG_FILE, index=False)
        print(f"Logged activity: {action} for {email}")
    except Exception as e:
        print(f"Failed to log activity: {e}")
