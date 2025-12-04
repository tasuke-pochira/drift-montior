import pandas as pd
import numpy as np
from evidently import Report
from evidently.presets import DataDriftPreset
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
}
)

# 3. Generate the Drift Report
report = Report(metrics=[
    DataDriftPreset(drift_share=0.1),

])

result = report.run(reference_data=reference_data, current_data=current_data)

# 4. Save the visual report (HTML) for GitHub Pages
os.makedirs("site", exist_ok=True)
result.save_html("site/index.html")
# 5. Check if Drift actually happened (for the Discord Alert)
# We convert the report to a Python dict to check the "dataset_drift" boolean
data = result.dict()
print(result)
drift_detected = False
# Loop through metrics to find "DriftedColumnsCount"
for metric in data['metrics']:
    # Check if this is the metric that counts drifted columns
    if metric['metric_name'].startswith('DriftedColumnsCount'):
        
        # Extract the results from the 'value' key (NOT 'result')
        results = metric['value']
        share = results['share']
        
        # Extract the threshold you set from the config
        threshold = metric['config']['drift_share']
        
        print(f"Found Metric: Drift Share = {share:.2f}, Threshold = {threshold}")

        # MANUALLY check if we failed the threshold
        if share > threshold:
            drift_detected = True
        
        break

print(f"Drift Detected: {drift_detected}")

# We create a small JSON file that GitHub Actions can read later
with open("drift_status.json", "w") as f:
    json.dump({"drift": drift_detected}, f)