import asyncio
import json
import os
import zipfile
import argparse
from datetime import datetime
from playwright.async_api import async_playwright

CONFIG_FILENAME = "gradescope.json"

def timestamp():
    return datetime.now().strftime("%H:%M:%S.%f")[:-2]

def log(msg):
    print(f"[{timestamp()} {msg}")

def load_config():
    if not os.path.exists(CONFIG_FILENAME):
        raise FileNotFoundError(f"⚠️ Config file '{CONFIG_FILENAME}' not found.")
    with open(CONFIG_FILENAME, "r") as f:
        return json.load(f)

def zip_files(file_patterns, output_filename):
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("."):
            for file in files:
                if file == output_filename:
                    continue
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, ".")
                zipf.write(full_path, arcname)
                print(f"📦 Added: {arcname}")
    print(f"\n✅ Created: {output_filename}")

def print_submission_summary(course_label, assignment_label, file):
    print("\n🧾 Submission Receipt:")
    print(f"✅ Submitted to \"{course_label} > {assignment_label}\"")
    print(f"🕒 Time: {datetime.now().strftime('%I:%M %p, %B %d')}")
    print(f"📁 File: {file}")

async def submit_to_gradescope(course, assignment, file, username, password):
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=False)
    page = await browser.new_page()

    log("🌐 Navigating to Gradescope login...")
    await page.goto("https://www.gradescope.com.au")
    await page.click("button.js-logInButton")
    await page.click("a.js-omniauthChoice")
    await page.click('a[href="/auth/saml/qut"]')

    if "qut.edu.au" in page.url:
        log("👤 QUT login detected. Entering credentials...")
        await page.wait_for_selector('input[name="username"]')
        await page.fill('input[name="username"]', username)
        await page.fill('input[name="password"]', password)
        await page.click('button#kc-login')
        await page.wait_for_selector("a.courseBox")
        log("🔓 QUT login complete")

    log("📘 Searching for course...")
    courses = await page.query_selector_all("a.courseBox")
    course_label = ""
    for c in courses:
        name = (await c.inner_text()).strip().split("\n")[0]
        if course.lower() in name.lower():
            href = await c.get_attribute("href")
            course_label = name
            log(f"➡️ Found course: {course_label}")
            await page.goto(f"https://www.gradescope.com.au{href}")
            await page.wait_for_selector('a[href*="/assignments/"]')
            break

    if not course_label:
        raise Exception(f"❌ Could not find course matching '{course}'")

    log("📄 Searching for assignment...")
    assignment_label = ""

    # Try finding assignment links first
    assignments = await page.query_selector_all('a[href*="/assignments/"]')
    for a in assignments:
        label = (await a.inner_text()).strip()
        if assignment.lower() in label.lower():
            href = await a.get_attribute("href")
            assignment_label = label
            log(f"➡️ Found assignment: {assignment_label}")
            await page.goto(f"https://www.gradescope.com.au{href}")
            await page.wait_for_selector('button.js-submitAssignment')
            break

    # Fallback: try matching visible submission buttons on the same course page
    if not assignment_label:
        buttons = await page.query_selector_all('button.js-submitAssignment')
        for b in buttons:
            label = (await b.inner_text()).strip()
            if assignment.lower() in label.lower():
                assignment_label = label
                log(f"➡️ Found assignment (button only): {assignment_label}")
                break

    if not assignment_label:
        raise Exception(f"❌ Could not find assignment matching '{assignment}'")

    log("📤 Starting submission...")
    resubmit_button = page.locator('button.js-submitAssignment:has-text("Resubmit")')
    submit_button = page.locator(f'button.js-submitAssignment:has-text("{assignment_label}")')

    if await resubmit_button.is_visible():
        await resubmit_button.click()
    elif await submit_button.is_visible():
        await submit_button.click()
    else:
        raise Exception("❌ Could not locate a submission button.")

    await page.wait_for_selector('input#submission_method_upload')
    await page.check('input#submission_method_upload')

    file_input = page.locator('input[type="file"]')
    log("⏳ Waiting for file input to appear...")
    await file_input.wait_for(timeout=10000, state="attached")

    log(f"📤 Uploading: {file}")
    await file_input.set_input_files(file)
    await page.wait_for_timeout(1000)

    upload_button = page.locator('button.tiiBtn-primary.js-submitCode')
    log("📬 Clicking Upload...")
    await upload_button.wait_for(timeout=5000)
    await upload_button.click()

    await page.wait_for_timeout(3000)
    log("✅ File submitted successfully!")
    print_submission_summary(course_label, assignment_label, file)
    log("🕒 Leaving the browser open. Press Enter to exit.")
    await asyncio.get_event_loop().run_in_executor(None, input)

    await browser.close()
    await p.stop()
    return course_label, assignment_label

def main():
    parser = argparse.ArgumentParser(description="Submit to Gradescope with ease.")
    parser.add_argument("command", choices=["submit"], help="Command to execute.")
    parser.add_argument("--course", help="Course name (e.g., CAB202)")
    parser.add_argument("--assignment", help="Assignment name (e.g., Assignment 2)")
    parser.add_argument("--file", help="Filename to submit (e.g., submission.zip)")
    parser.add_argument("--bundle", nargs="+", help="File patterns to include in the zip (e.g., *.py)")

    args = parser.parse_args()
    if args.command == "submit":
        config = load_config()

        course = args.course or config.get("course")
        assignment = args.assignment or config.get("assignment")
        file = args.file or config.get("file", "submission.zip")
        bundle_patterns = args.bundle or config.get("bundle", ["*.py"])
        username = config.get("username")
        password = config.get("password")

        zip_files(bundle_patterns, file)
        asyncio.run(submit_to_gradescope(course, assignment, file, username, password))

if __name__ == "__main__":
    main()
