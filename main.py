import time
from scanner import check_signals

if __name__ == "__main__":
    while True:
        check_signals()
        time.sleep(60 * 5)  # Scan every 5 minutes
