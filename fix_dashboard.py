import os

file_path = r"c:\Users\zzeel\OneDrive\Desktop\AutoDevOS\frontend\app\dashboard\[jobId]\page.tsx"
with open(file_path, 'a') as f:
    f.write('\n\nexport default function JobDashboard() {\n  return (\n    <ErrorBoundary>\n      <JobDashboardContent />\n    </ErrorBoundary>\n  );\n}\n')
print("✓ Export statement added to dashboard page")
