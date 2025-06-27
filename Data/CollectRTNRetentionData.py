import os
import pandas as pd
import re
from collections import defaultdict

# Set the path to your root directory
ROOT_DIR = "/home/evan/Bench-Test-Automation-Suite/Data"

# Files to look for
RETENTION_PATTERN = "SuccessCompleteProgramRetentionOutput_"
RTN_PATTERN = "SuccessCompleteProgramRTNOutput_"

# Dictionary to hold data for each conductance target
retention_targets = defaultdict(list)
rtn_targets = defaultdict(list)

def extract_device_id(path):
    match = re.search(r'TPTE\d+', path)
    return match.group(0) if match else None

def load_csv_strip_header(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Find the line that starts with 'Time' – the real header
    data_start_index = next(i for i, line in enumerate(lines) if line.startswith('Time'))
    data = pd.read_csv(filepath, skiprows=data_start_index)
    return data

def process_file(filepath, is_retention=True):
    device_id = extract_device_id(filepath)
    if not device_id:
        return
    
    df = load_csv_strip_header(filepath)
    for col in df.columns[1:]:  # skip 'Time (s)'
        gtarget = col.split("_")[-2]  # e.g., '400.00' from 'Conductance_Target_400.00 uS'
        gtarget = gtarget.strip()
        entry = df[['Time (s)', col]].rename(columns={col: device_id})
        entry = entry.set_index('Time (s)')
        if is_retention:
            retention_targets[gtarget].append(entry)
        else:
            rtn_targets[gtarget].append(entry)

# Walk through directory tree
for root, _, files in os.walk(ROOT_DIR):
    for fname in files:
        if fname.startswith(RETENTION_PATTERN) and fname.endswith('.csv'):
            process_file(os.path.join(root, fname), is_retention=True)
        elif fname.startswith(RTN_PATTERN) and fname.endswith('.csv'):
            process_file(os.path.join(root, fname), is_retention=False)

# Save all 20 combined CSVs
os.makedirs("CombinedOutput", exist_ok=True)

for gtarget, dfs in retention_targets.items():
    combined = pd.concat(dfs, axis=1)
    combined.to_csv(f"CombinedOutput/Retention_Conductance_Target_{gtarget}_uS.csv")

for gtarget, dfs in rtn_targets.items():
    combined = pd.concat(dfs, axis=1)
    combined.to_csv(f"CombinedOutput/RTN_Conductance_Target_{gtarget}_uS.csv")

print("✅ RTN and Retention data compiled into 20 files in CombinedOutput/")
