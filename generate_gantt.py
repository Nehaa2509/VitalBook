import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import datetime

tasks = [
    {"Task": "Requirement Analysis & Planning", "Start": "2026-01-01", "End": "2026-01-10", "Category": "Planning"},
    {"Task": "UI/UX Design & Prototyping", "Start": "2026-01-11", "End": "2026-01-25", "Category": "Design"},
    {"Task": "Django Setup & DB Schema", "Start": "2026-01-26", "End": "2026-01-31", "Category": "Backend"},
    {"Task": "User Auth & Registration", "Start": "2026-02-01", "End": "2026-02-10", "Category": "Backend"},
    {"Task": "Doctor & Patient Models", "Start": "2026-02-11", "End": "2026-02-15", "Category": "Backend"},
    {"Task": "Appointment Booking System", "Start": "2026-02-16", "End": "2026-02-25", "Category": "Backend"},
    {"Task": "Frontend Development", "Start": "2026-02-20", "End": "2026-02-28", "Category": "Frontend"},
    {"Task": "Admin Dashboard Customization", "Start": "2026-03-01", "End": "2026-03-10", "Category": "Backend"},
    {"Task": "Digital Medical Prescriptions", "Start": "2026-03-10", "End": "2026-03-18", "Category": "Advanced Features"},
    {"Task": "Payment Gateway (Cashfree)", "Start": "2026-03-18", "End": "2026-03-25", "Category": "Advanced Features"},
    {"Task": "Email Notifications", "Start": "2026-03-25", "End": "2026-03-31", "Category": "Advanced Features"},
    {"Task": "Final Testing & Deployment", "Start": "2026-04-01", "End": "2026-04-01", "Category": "Testing"}
]

df = pd.DataFrame(tasks)
df['Start'] = pd.to_datetime(df['Start'])
df['End'] = pd.to_datetime(df['End']) + pd.Timedelta(days=1)
df['Duration'] = (df['End'] - df['Start']).dt.days

df = df.sort_values(by='Start', ascending=False)

fig, ax = plt.subplots(figsize=(14, 8))

colors = {'Planning': '#4c72b0', 'Design': '#dd8452', 'Backend': '#55a868', 'Frontend': '#c44e52', 'Advanced Features': '#8172b3', 'Testing': '#937860'}

for i, task in df.iterrows():
    ax.barh(task['Task'], task['Duration'], left=task['Start'], color=colors[task['Category']], edgecolor='black', height=0.6)

ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_minor_locator(mdates.DayLocator([1, 15]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

plt.title('VitalBook Hospital Project Gantt Chart\n(Jan 1 - Apr 1)', fontsize=20, fontweight='bold', pad=20)
plt.xlabel('Timeline', fontsize=14, labelpad=10)
plt.ylabel('Project Phases / Tasks', fontsize=14, labelpad=10)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

import matplotlib.patches as mpatches
legend_patches = [mpatches.Patch(color=color, label=cat) for cat, color in colors.items()]
plt.legend(handles=legend_patches, title='Categories', title_fontsize='13', fontsize='11', bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.savefig('gantt_chart.png', dpi=300, bbox_inches='tight')
print("Gantt chart successfully created and saved as gantt_chart.png")
