import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

blacklisted_words = ['password', 'secret', 'admin']  # Example list of blacklisted words


def scan_changed_files_for_blacklisted_words(pr_number):
    logging.info(pr_number)
    repo = os.environ['GITHUB_REPOSITORY']
    token = os.environ['GITHUB_TOKEN']
    logging.info("Recieved token - %s", token)
    logging.info("Repo - %s", repo)

    headers = {'Authorization': f'token {token}'}
    url = f'https://api.github.com/repos/{repo}/pulls/{pr_number}/files'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    files = response.json()
    logging.info(files);

    findings = []

    for file in files:
        filename = file['filename']
        patch_url = file['patch']
        lines = get_changed_lines_from_patch(patch_url)
        logging.info("changed lines - %s", lines)
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


def get_changed_lines_from_patch(patch_url):
    response = requests.get(patch_url)
    response.raise_for_status()
    patch_content = response.text
    logging.info("content - %s", patch_content)

    # Process the patch content to extract the changed lines
    changed_lines = []
    for line in patch_content.splitlines():
        logging.info("line - %s", line)
        if line.startswith("+"):
            changed_lines.append(line)

    return changed_lines


# Usage example
pr_number = os.environ['PR_NUMBER']

findings = scan_changed_files_for_blacklisted_words(pr_number)

# Output the findings
if findings:
    print('Blacklisted words found:')
    for finding in findings:
        print(f"- File: {finding['file']}, Line: {finding['line']}, Word: {finding['word']}")
else:
    print('No blacklisted words found.')
