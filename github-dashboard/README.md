# GitHub Dashboard (Terminal)

A terminal-based GitHub profile dashboard built with Python. Fetches live data from the GitHub API and displays it as a styled CLI dashboard using the `rich` library.

## Features

- Profile info (name, bio, location, company, joined date)
- Stats overview (repos, stars, followers, following, years active)
- Top languages breakdown with visual bar chart
- Notable repos sorted by stars
- Recent activity sorted by last updated

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Your own profile (default)
python dashboard.py

# Any GitHub user
python dashboard.py torvalds
```

## Tech Stack

- Python
- `requests` — GitHub REST API
- `rich` — terminal UI (panels, tables, styled text)
