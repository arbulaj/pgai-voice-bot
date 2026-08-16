# Bug Report


## Bug 1 — Support transfer ends the call without resolving the patient's request

**Severity:** High  
**Call:** `artifacts/transcripts/02_reschedule-28d9810f.txt`  
**Audio:** `artifacts/recordings/02_reschedule-28d9810f.mp3`  
**Timestamp:** `02:20`

**What happened:**  
In multiple scenarios, the practice agent was unable to locate the fictional patient's record and initiated a transfer to patient support. The transfer reached the Pretty Good AI test line, which immediately ended the interaction, leaving the original patient request unresolved.

**Why it matters:**  
This creates a dead end during an important fallback path. A patient who cannot be handled by the automated agent may believe they are being transferred to someone who can help, but instead the call terminates without completing the task.

**Expected behavior:**  
If the agent cannot complete the request, the transfer should successfully connect the caller to the intended support destination. If no support destination is available in the test environment, the agent should clearly explain that limitation instead of presenting the transfer as successful.

**Evidence:**  
In multiple calls, the agent says it is transferring the patient, followed by:

> "Hello, you've reached the Pretty Good AI test line. Goodbye."

---

## Bug 2 — Transfer proceeds despite the patient continuing the conversation

**Severity:** Medium  
**Call:** `artifacts/transcripts/03_cancel-694d6b51.txt`  
**Audio:** `artifacts/recordings/03_cancel-694d6b51.mp3`  
**Timestamp:** `01:35`

**What happened:**  
The patient attempted to continue the conversation or ask an additional question around the time the agent initiated a transfer, but the transfer proceeded and the conversation ended.

**Why it matters:**  
This makes interruption and turn-taking around escalation unreliable. A caller may try to stop or delay a transfer because they still need information, but the system can proceed before that request is handled.

**Expected behavior:**  
Before executing a transfer, the agent should allow the current patient turn to finish and respond appropriately. If the patient indicates they want to continue with the AI, the pending transfer should be canceled when possible.

**Evidence:**  
During the cancellation scenario, the patient restated that they wanted to complete the cancellation before the transfer, but the agent proceeded with the transfer.

---

## Bug 3 — Agent states unsupported general appointment availability

**Severity:** Medium  
**Call:** `artifacts/transcripts/10_unusual_constraint-a84cfba8.txt`  
**Audio:** `artifacts/recordings/10_unusual_constraint-a84cfba8.mp3`  
**Timestamp:** `01:40`

**What happened:**  
After explaining that it could not schedule the new patient, the agent stated that afternoon appointments are available most days and that there are typically openings between 4:00 and 4:30 PM, especially on Wednesdays.

**Why it matters:**  
The agent appears to present appointment availability without actually checking a scheduling system. A patient could interpret this as evidence that appointments exist and make plans based on information that may not be current.

**Expected behavior:**  
If live appointment availability cannot be checked, the agent should say that exact availability must be confirmed by the clinic rather than characterize particular times as typically available.

**Evidence:**  

> "Typically, there are openings between 4 and 4:30 p.m. on weekdays..."

---

## Calls with no meaningful issue

The following completed calls did not show a clear product issue based on transcript review:

- `01_simple_schedule`
- `05_hours_location`
- `06_insurance`
- `08_barge_in`