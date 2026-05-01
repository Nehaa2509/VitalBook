import matplotlib.pyplot as plt
import matplotlib.patches as patches

months_data = [
    {
        "month": "January",
        "days": 31,
        "tasks": [
            {"id": 1, "name": "Requirement Gathering", "start": 1, "end": 7, "color": "#5b9bd5"},
            {"id": 2, "name": "UI/UX Design & Prototyping", "start": 8, "end": 20, "color": "#ed7d31"},
            {"id": 3, "name": "Django Setup & DB Schema", "start": 21, "end": 31, "color": "#a5a5a5"}
        ]
    },
    {
        "month": "February",
        "days": 28,
        "tasks": [
            {"id": 4, "name": "Design of Patient and Admin login", "start": 1, "end": 4, "color": "#ffc000"},
            {"id": 5, "name": "Patient Registration logic", "start": 5, "end": 8, "color": "#70ad47"},
            {"id": 6, "name": "Dashboard design for Patient & Admin", "start": 9, "end": 14, "color": "#5b9bd5"},
            {"id": 7, "name": "Doctor & Specialization Models", "start": 15, "end": 18, "color": "#ed7d31"},
            {"id": 8, "name": "Appointment Booking System Logic", "start": 19, "end": 24, "color": "#ffc000"},
            {"id": 9, "name": "Frontend Dashboard Implementation", "start": 25, "end": 28, "color": "#a5a5a5"}
        ]
    },
    {
        "month": "March",
        "days": 31,
        "tasks": [
            {"id": 10, "name": "Digital Medical Prescriptions (PDF)", "start": 1, "end": 10, "color": "#5b9bd5"},
            {"id": 11, "name": "Admin Dashboard Customization", "start": 11, "end": 18, "color": "#ffc000"},
            {"id": 12, "name": "Payment Gateway (Cashfree)", "start": 19, "end": 25, "color": "#70ad47"},
            {"id": 13, "name": "Automated Email Notifications", "start": 26, "end": 31, "color": "#2f5597"}
        ]
    },
    {
        "month": "April",
        "days": 10, # Show 10 days for April to keep it looking like a table
        "tasks": [
            {"id": 14, "name": "Final Testing & Deployment", "start": 1, "end": 1, "color": "#ed7d31"}
        ]
    }
]

# Calculate height ratios based on number of tasks in each month
height_ratios = [len(m['tasks']) + 2 for m in months_data]
fig, axes = plt.subplots(4, 1, figsize=(18, 14), gridspec_kw={'height_ratios': height_ratios})
plt.subplots_adjust(hspace=0.4)

task_col_width = 16
id_col_width = 1

for ax, month_data in zip(axes, months_data):
    # Set fixed aspect ratio to ensure squares are somewhat consistent
    ax.set_xlim(0, task_col_width + 31)
    num_tasks = len(month_data['tasks'])
    ax.set_ylim(0, num_tasks + 2)
    ax.axis('off')
    
    days = month_data['days']
    tasks = month_data['tasks']
    
    # Draw empty box above TASK
    ax.add_patch(patches.Rectangle((0, num_tasks+1), task_col_width, 1, fill=False, edgecolor='black', lw=1.5))
    
    # Draw Month Header
    ax.add_patch(patches.Rectangle((task_col_width, num_tasks+1), days, 1, fill=False, edgecolor='black', lw=1.5))
    ax.text(task_col_width + days/2, num_tasks+1.5, month_data['month'], ha='center', va='center', fontsize=20, fontweight='bold')
    
    # Draw TASK Header
    ax.add_patch(patches.Rectangle((0, num_tasks), task_col_width, 1, fill=False, edgecolor='black', lw=1.5))
    ax.text(task_col_width/2, num_tasks+0.5, "TASK", ha='center', va='center', fontsize=14, fontweight='bold')
    
    # Draw Day Numbers
    for d in range(1, days + 1):
        ax.add_patch(patches.Rectangle((task_col_width + d - 1, num_tasks), 1, 1, fill=False, edgecolor='black', lw=1))
        ax.text(task_col_width + d - 0.5, num_tasks+0.5, str(d), ha='center', va='center', fontsize=11, fontweight='bold')
        
    # Draw Tasks
    for i, task in enumerate(tasks):
        y = num_tasks - i - 1
        
        # ID Box
        ax.add_patch(patches.Rectangle((0, y), id_col_width, 1, fill=False, edgecolor='black', lw=1))
        ax.text(id_col_width/2, y+0.5, str(task['id']), ha='center', va='center', fontsize=12)
        
        # Name Box
        ax.add_patch(patches.Rectangle((id_col_width, y), task_col_width - id_col_width, 1, fill=False, edgecolor='black', lw=1))
        ax.text(id_col_width + 0.3, y+0.5, task['name'], ha='left', va='center', fontsize=12)
        
        # Day Grid
        for d in range(1, days + 1):
            ax.add_patch(patches.Rectangle((task_col_width + d - 1, y), 1, 1, fill=False, edgecolor='black', lw=0.5))
            
        # Fill Task Bar
        start_idx = task['start'] - 1
        duration = task['end'] - task['start'] + 1
        ax.add_patch(patches.Rectangle((task_col_width + start_idx, y), duration, 1, fill=True, color=task['color'], edgecolor='black', lw=1))

plt.savefig('month_wise_gantt.png', dpi=300, bbox_inches='tight', facecolor='white')
print("Month-wise Gantt chart saved.")
