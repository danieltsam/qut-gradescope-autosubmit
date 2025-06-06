# Gradescope Auto Submitter for QUT

This tool automates the process of submitting assignments to Gradescope via the QUT SSO login system. It was built to streamline a repetitive and manual process that many QUT students face every week: zipping their files, logging into Gradescope, navigating to the correct course and assignment, uploading their submission, and confirming it. And then repeating this process 1,000,000 times.

I built this script to save time, reduce mistakes, and make assignment submissions feel as smooth as pushing to a Git repo and never leave my IDE. It’s especially useful when working on frequent tutorials, labs, or auto-graded assignments that require consistent resubmissions (could also just be a skill issue).

## What It Does

- Bundles your project files into a zip archive
- Logs into Gradescope using QUT SSO
- Navigates to your course and assignment automatically (based on what you set in the .json)
- Uploads your zip file using the file input
- Leaves the browser open for visual confirmation
- Prints a clear submission receipt in the terminal with timestamp and file info

**All in less than 10 seconds!**

## Setup

### 1. Install Playwright

```bash
pip install playwright
playwright install
```

### 2. Clone or Download This Repo

Place the script and your project in the same directory.

### 3. Create `gradescope.json`

This file stores your config:

```json
{
  "course": "CAB202",
  "assignment": "Tutorial 08",
  "file": "submission.zip",
  "bundle": ["*"],
  "username": "n12345678",
  "password": "yourQUTpassword"
}
```

- You can use `*` to zip all files, or filter by extensions like `*.c`, `*.py`, etc.
- `file` is the name of the zip that will be created.

### ⚠️ Warning: Plaintext Passwords
This script reads your QUT password directly from `gradescope.json`, which is stored in plaintext. Use at your own risk. Do **not** upload your config file to GitHub unless you remove your credentials.

## Directory Structure

Your working directory should look like this:

```
your-folder/
├── gradescope.py
├── gradescope.json
├── the rest of your actual submission files and directories
```

## Usage

```bash
python gradescope.py submit
```

The script will:

- Zip your files
- Open a browser
- Log you into QUT SSO
- Navigate to your Gradescope course and assignment
- Upload your submission
- Wait for you to press Enter before closing

## Example Output

```
📦 Added: main.c
📦 Added: timer.c
📦 Added: platformio.ini
✅ Created: submission.zip

[03:28:06.7162 👤 QUT login detected. Entering credentials...
[03:28:10.8519 🔓 QUT login complete
[03:28:10.9083 ➡️ Found course: CAB202_25se1
[03:28:12.4289 ➡️ Found assignment: CAB202 Tutorial 08
[03:28:16.2370 📤 Uploading: submission.zip
📬 Clicking Upload...
✅ File submitted successfully!

🧾 Submission Receipt:
✅ Submitted to "CAB202_25se1 > CAB202 Tutorial 08"
🕒 Time: 02:59 AM, June 07
📁 File: submission.zip
```

## Notes

- Currently supports QUT's SSO login system with Gradescope Australia.
- You can modify the script or adapt it for other institutions if needed.
- Built for students who want a frictionless way to push updates to Gradescope.
