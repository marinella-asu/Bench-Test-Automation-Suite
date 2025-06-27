import os
import pandas as pd

# === Input CSVs ===
RETENTION_FILE = "CombinedOutput/Retention_Conductance_Target_Target_uS.csv"
RTN_FILE = "CombinedOutput/RTN_Conductance_Target_Target_uS.csv"

# === Output Folder ===
OUTPUT_FOLDER = "SplitByTarget"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Fixed Conductance Targets in uS ===
conductance_targets = [f"{g:.0f}" for g in range(400, 1400, 100)]  # ['400', '500', ..., '1300']

def split_and_save(input_csv, label):
    df = pd.read_csv(input_csv, index_col=0)

    # Remove TPTE33 columns
    df = df[[col for col in df.columns if not (col.startswith("TPTE34"))]]

    # Group columns into blocks of 10 (one per device)
    num_targets = 10
    device_names = df.columns.unique()

    # Make sure columns are ordered properly for slicing
    df = df[sorted(df.columns, key=lambda x: (x, df.columns.tolist().index(x)))]

    for i, target in enumerate(conductance_targets):
        matching_cols = df.columns[i::num_targets]  # Every 10th column starting at i
        sub_df = df[matching_cols].copy()
        sub_df.columns = [col for col in matching_cols]  # Keep original names

        out_file = os.path.join(OUTPUT_FOLDER, f"{label}_{target}_uS.csv")
        sub_df.to_csv(out_file)
        print(f"✅ Saved: {out_file}")

# === Process both Retention and RTN ===
split_and_save(RETENTION_FILE, "Retention")
split_and_save(RTN_FILE, "RTN")
print("✅ All files split and saved to SplitByTarget/")
