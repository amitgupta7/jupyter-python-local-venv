import sys
from datetime import datetime, timedelta

def generate_dates_from_range(start_date, end_date):
    current_date = start_date
    dates = []
    
    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    return dates

def generate_dates_from_days_back(days):
    today = datetime.now() - timedelta(days=1)
    return [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]

if __name__ == "__main__":
    if len(sys.argv) == 3:
        # Handle date range
        try:
            start_date = datetime.strptime(sys.argv[1], '%Y-%m-%d')
            end_date = datetime.strptime(sys.argv[2], '%Y-%m-%d')
            if start_date > end_date:
                raise ValueError("Start date must be before or equal to end date.")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

        dates = generate_dates_from_range(start_date, end_date)
    
    elif len(sys.argv) == 2:
        # Handle days back
        try:
            days = int(sys.argv[1])
            if days < 1:
                raise ValueError("Number of days must be at least 1.")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

        dates = generate_dates_from_days_back(days)

    else:
        print("Usage: python script.py <start_date> <end_date> OR python script.py <days_back>")
        print("Dates should be in YYYY-MM-DD format.")
        sys.exit(1)

    str = "--exclude '*' "
    for x in dates:
        str += "--include '*"+x+"*.csv' "
    
    metricsArr = ['download_workers_count', 'infra_access_latency'
                  , 'pod_cpu_usage', 'pod_memory_usage', 'root_disk_used'
                  , 'mnt_disk_used', 'install_dir_disk'
                  ] 

    for x in metricsArr:
        str += "--exclude '*"+x+"*.csv' "

    print(str)
