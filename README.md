# Test-driven planner
> [!NOTE]
> The planner is currently in development and not fully functional.

## About
A simple planner application developed in Python while following test-driven development practices, utilising MongoDB for storing and querying planner tasks.

## Usage
The planner is designed to be used within a terminal.

1. View tasks for today:
```
planner.py
```

2. View tasks for a particular day (e.g., March 10th, 2025):

```
planner.py 2025 3 10
```

3. Insert a new task into the planner by specifying the description inside double quotes and a date (YYYY MM DD).
```
planner.py -i "my task" 2025 12 30
```

4. Update a task based on its initial description and date...
```
planner.py -i "my task" 2025 12 30
planner.py -u "my task" 2025 12 30 "super task" 2025 12 30
```
...or based on its numerical ID (e.g., 12345):
```
planner.py -u 12345 "super task" 2025 12 30
```

5. Delete an unwated task based on description and date or ID:
```
planner.py -d "super task" 2025 12 30
planner.py -d 12345
```
