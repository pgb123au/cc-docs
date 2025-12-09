---
description: Automate RetellAI simulation call testing - run tests and analyze results
---

# Simulation Call Testing Automation

Streamline the process of running and analyzing RetellAI simulation tests.

## Quick Start

When you run this command, I will:
1. Find the latest test case definitions
2. Show you the test summary and ask which to run
3. Guide you through getting results from RetellAI Dashboard
4. Analyze the results and report issues

## Test Case Location

Latest test cases are in: `retell/Testing/*/TEST_RESULTS/test-cases*.json`

## Workflow

### Step 1: Find Latest Test Cases
```bash
# Find most recent test cases file
find "C:/Users/peter/Downloads/CC/retell/Testing" -name "test-cases*.json" -type f | head -5
```

Read and display the test case summaries:
- Test name
- Description
- Key metrics being validated
- Fixes being tested

### Step 2: Prompt for Action

Ask user:
```
Found N test case(s) in [file]:

1. [Test Name] - [Brief description]
2. [Test Name] - [Brief description]

Options:
A) Run ALL tests (you'll need to use RetellAI Dashboard)
B) Enter test job IDs (if you already ran tests)
C) View test case details

Which option? [A/B/C]
```

### Step 3A: If Running New Tests

Since RetellAI API doesn't support programmatic test creation, provide dashboard instructions:

```
=== MANUAL TEST EXECUTION ===

1. Go to: https://dashboard.retellai.com
2. Navigate to: Agents > [Your Agent] > Tests
3. Click "Create Test" for each test case
4. Copy the test prompts from the JSON file
5. Run each test and note the Job IDs

Test prompts to copy:
--------------------------------------------------
TEST 1: [Name]
[Full user_prompt text]
--------------------------------------------------
TEST 2: [Name]
[Full user_prompt text]
--------------------------------------------------

After running, enter the Job IDs below.
```

### Step 3B: If Entering Job IDs

Prompt user for test job IDs:
```
Enter test job IDs (comma-separated or one per line):
Example: test_job_abc123, test_job_def456

Job IDs:
```

### Step 4: Attempt Results Download

Try to fetch results via API (may fail with 401):
```bash
cd C:\Users\peter\Downloads\CC\retell\scripts
python -c "
import requests
import os

api_key = open('C:/Users/peter/Downloads/Retell_API_Key.txt').read().strip()
job_ids = ['JOB_ID_1', 'JOB_ID_2']  # Replace with actual IDs

for job_id in job_ids:
    resp = requests.get(
        f'https://api.retellai.com/v2/get-batch-test/{job_id}',
        headers={'Authorization': f'Bearer {api_key}'}
    )
    print(f'{job_id}: {resp.status_code}')
    if resp.status_code == 200:
        print(resp.json())
"
```

If API fails (401), provide dashboard export instructions:
```
=== MANUAL RESULT EXPORT ===

API access restricted. Please export manually:

1. Go to: https://dashboard.retellai.com
2. Navigate to: Agents > Tests > View Results
3. For each Job ID, click to view details
4. Copy the transcript and result summary
5. Paste here or save to:
   retell/Testing/[date]/TEST_RESULTS/[job_id]_results.txt

I'll analyze the results once you provide them.
```

### Step 5: Analyze Results

For each test result, check:
- [ ] All expected metrics were hit
- [ ] Tool calls executed correctly
- [ ] Node transitions followed expected paths
- [ ] No unexpected errors or dead ends
- [ ] Conversation completed naturally

### Step 6: Generate Report

```
=== SIMULATION TEST RESULTS ===

Test Run Date: YYYY-MM-DD
Agent Version: vX.XXX

TEST 1: [Name]
  Job ID: test_job_xxx
  Status: [PASS/FAIL/PARTIAL]
  Metrics:
    [x] Metric 1 - achieved
    [x] Metric 2 - achieved
    [ ] Metric 3 - FAILED: [reason]

  Issues Found:
    - [Issue description]

  Recommended Fixes:
    - [Fix suggestion]

TEST 2: [Name]
  Job ID: test_job_yyy
  Status: [PASS/FAIL/PARTIAL]
  ...

OVERALL: X/N tests passed

DONE DONE DONE
```

## Test Case JSON Format Reference

```json
{
  "name": "Test Name",
  "description": "What this tests",
  "dynamic_variables": { ... },
  "metrics": ["metric1", "metric2"],
  "user_prompt": "Full simulation prompt",
  "tool_mocks": [],
  "llm_model": "gpt-4.1-mini"
}
```

## Tips

- **tool_mocks: []** = REAL API calls - use only Peter Ball test data
- Always run tests with dates 14+ days in future
- Check both the transcript AND the tool call logs
- Compare actual node path vs expected path from test case

## Safety

- Only use Peter Ball test data (patient_id: 1805465202989210063)
- Do NOT run tests that could create real appointments without confirmation
- Review tool_mocks before running - empty array = live data
