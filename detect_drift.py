import pandas as pd
import numpy as np
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
import os
import json

# 1. Load "Reference" Data (The data your model was trained on)
# We simulate a healthy dataset: normal distribution
reference_data = pd.DataFrame({
    'age': np.random.normal(30, 5, 1000),             # Mean age 30
    'salary': np.random.normal(50000, 10000, 1000),   # Mean salary 50k
    'clicks': np.random.randint(0, 100, 1000)
})

# 2. Simulate "Current" Production Data (The new data coming in today)
# We INTENTIONALLY drift the 'salary' column (Mean shifts to 75k) to trigger an alert
current_data = pd.DataFrame({
    'age': np.random.normal(30, 5, 1000),             # Age stays same
    'salary': np.random.normal(75000, 10000, 1000),   # <--- DRIFT! Salary spiked
    'clicks': np.random.randint(0, 100, 1000)
})

# 3. Generate the Drift Report
report = Report(metrics=[
    DataDriftPreset(), 
])

report.run(reference_data=reference_data, current_data=current_data)

# 4. Save the visual report (HTML) for GitHub Pages
os.makedirs("site", exist_ok=True)
report.save_html("site/index.html")

# 5. Check if Drift actually happened (for the Discord Alert)
# We convert the report to a Python dict to check the "dataset_drift" boolean
result = report.as_dict()
drift_detected = result['metrics'][0]['result']['dataset_drift']

print(f"Drift Detected: {drift_detected}")

# We create a small JSON file that GitHub Actions can read later
with open("drift_status.json", "w") as f:
    json.dump({"drift": drift_detected}, f)