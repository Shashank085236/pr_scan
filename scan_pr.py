import os
import requests
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

blacklisted_words = ['password', 'secret', 'admin']  # Example list of blacklisted words


def scan_changed_files_for_blacklisted_words(pr_number):
    logging.info(pr_number)
    repo = os.environ['GITHUB_REPOSITORY']
    token = os.environ['GITHUB_TOKEN']
    logging.info("Received token - %s", token)
    logging.info("Repo - %s", repo)

    headers = {'Authorization': f'token {token}'}
    url = f'https://api.github.com/repos/{repo}/pulls/{pr_number}/files'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    files = response.json()
    logging.info(files)

    findings = []

    for file in files:
        filename = file['filename']
        patch_content = file['patch']
        lines = get_changed_lines_from_patch(patch_content)
        logging.info("Changed lines - %s", lines)
        for line_number, line in lines:
            line = line.lower()
            for word in blacklisted_words:
                if word in line:
                    findings.append({
                        'file': filename,
                        'line': line_number,
                        'word': word
                    })

    return findings


def get_changed_lines_from_patch(patch_content):
    logging.info("Content - %s", patch_content)

    # Process the patch content to extract the changed lines
    lines = []
    current_line_number = 0

    for line in patch_content.split('\n'):
        if line.startswith('@@'):
            # Extract the start line number information from the patch header
            _, line_info = line.split('@@', 1)
            line_numbers = line_info.split()[0]
            start_line_number, _ = map(int, line_numbers.split(','))
            current_line_number = start_line_number
        elif line.startswith('+'):
            # Add the changed line to the list
            lines.append((current_line_number, line[1:]))
            current_line_number += 1
        elif line.startswith('-'):
            # Skip deleted lines
            current_line_number += 1

    return lines


# Usage example
pr_number = os.environ['PR_NUMBER']

findings = scan_changed_files_for_blacklisted_words(pr_number)

# Output the findings
if findings:
    print('Blacklisted words found:')
    for finding in findings:
        print(f"- File: {finding['file']}, Line: {finding['line']}, Word: {finding['word']}")
    sys.exit(1)
else:
    print('No blacklisted words found.')
    sys.exit(0)
