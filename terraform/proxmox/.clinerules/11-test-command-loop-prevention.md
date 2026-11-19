# 11 — Test/command loop prevention — output is authoritative, not PIDs

Concrete failure mode this rule exists to prevent: Cline ran a test suite,
the captured output showed a complete successful summary, yet the agent kept
executing `sleep N; pgrep -f <test-runner> ...; grep ... test.log` cycles
because `pgrep` still matched a residual worker — until the identical-call
loop protection aborted the task.

This rule extends the general anti-loop policy in
`.clinerules/00-reasoning.md` §3 (max attempts, no repeated identical
calls, background-process status checked at most twice) with
test-specific rules. It applies to any test/build/lint command in this repo:
Python unittest (`python -m pytest`, `python3 -m unittest`), `python3 scripts/*.py`,
`promtool`, `tftest`, `make test-*`, not just Vitest.

## 1. Never poll indefinitely

MUST NOT repeatedly execute the same or substantially equivalent
command to determine whether a test run has finished. Combinations of
`sleep`, `pgrep`, `ps`, `grep ...test.log`, `tail` must never become an
unbounded polling loop.

## 2. Maximum polling attempts

If polling is genuinely necessary:

- Maximum 2 follow-up polling attempts.
- Never issue the same `run_commands` invocation more than twice.
- After the second inconclusive attempt, STOP polling and inspect the
  existing test output/log instead.
- Do not increase `sleep` and retry indefinitely.

## 3. Test output is authoritative (Python unittest/pytest)

When the captured output contains a complete successful summary such as:

    OK (N tests passed)
    or
    Ran N tests in Xs
    OK

with no failed test files/tests, the suite IS successfully completed.
Do NOT keep waiting merely because `pgrep -f python` still returns a
PID. The final test summary always takes precedence over
residual-process detection.

## 4. Detect completion from the log

When a test was launched with output redirected/tee'd to a log, inspect
that log — do not repeatedly check the process. If the log contains a
final summary showing all files/tests passed, report the suite as
complete and continue the task. Do not require the parent shell or
every child process to disappear before proceeding.

## 5. Bound long-running test commands

Whenever practical, run test commands with an explicit timeout
appropriate for the suite (e.g. `timeout <reasonable-duration>
<test-command>` or another bounded mechanism) instead of custom
indefinite polling. The timeout must be generous enough for the known
suite and must not be used to hide real slow-test problems.

## 6. Residual processes are a separate concern from test results

If all tests passed but a process remains:

1. Mark the test result as successful — first, always.
2. Determine whether the remaining PID belongs to the command Cline
   launched (correlate with the actual PID/process tree, not a name
   match).
3. If cleanup is needed, terminate only the known stale process tree.
4. Never convert a successful test run into a polling loop.
5. NEVER use broad destructive commands (e.g. killing every Python
   process). Note: leftover `python3` workers from test scripts are a known,
   expected phenomenon on this machine.

## 7. `pgrep -f` false positives

Never treat `pgrep -f python` or `pgrep -f pytest` alone as proof the suite
is still running. It may match child workers, stale processes, wrapper
commands, another test instance, or any command line containing the
string "python". If process inspection is required, correlate the PID
with the process Cline actually started.

## 8. Each command must provide materially new information

Before issuing another status-check command, ask: "Will this command
provide materially new information compared with the previous call?"
If not, do not execute it. A repeated `RUNNING` plus an unchanged,
already-complete test summary is NOT new information.

## 9. Loop escape condition

If about to run the same status command for a third time: STOP. Do not
call it. Instead: inspect the last output, determine success/failure
from the available evidence, report any ambiguity, and continue with
the next task step when the suite is demonstrably complete.

## 10. Successful suite — required internal response

On seeing e.g. `OK (N tests passed)` / `Ran N tests in Xs OK`, respond
internally:

    The test suite has completed successfully: N tests passed.
    A residual Python PID does not invalidate the completed test result.
    Stop polling and continue with the next task step.

and MUST NOT execute another `sleep + pgrep + grep` cycle.

## 11. Never trust a stale/shared test log

A successful test summary is authoritative ONLY when the log/output
is known to belong to the current test invocation.

- Prefer a unique log file per run, e.g. `/tmp/test-<unique-id>.log`.
- Or truncate/create the log immediately before starting the command
  (`> /tmp/test.log` in the same invocation that launches the test).
- Never infer that the current suite passed solely from a successful
  summary left in a log by a previous run.
- If in doubt about log provenance (shared filename, unknown mtime,
  not truncated by this run), re-run the suite with a fresh unique log
  — do not poll the ambiguous log.

## 12. Prefer the actual exit status when available

If Cline launched the test in the foreground and receives its exit
code, the exit code governs:

- exit code 0 + successful summary = PASS. Continue immediately — no
  polling, no pgrep.
- non-zero exit code = inspect and report the failure, even if some
  tests passed.
- timeout exit codes (e.g. 124 from GNU `timeout`) = treat as
  timeout/inconclusive, NOT success — unless the current-run output
  contains a definitive completed result (per §3, with §11 provenance)
  and the remaining process is proven residual (per §6/§7).

For background execution, correlate the test with the PID/process
Cline actually launched rather than relying on `pgrep -f`.

## Worked example

Command output:

    RUNNING
    OK (42 tests passed)

Correct decision: `TESTS COMPLETE — STOP POLLING — CONTINUE TASK`.
The `RUNNING` line comes from a `pgrep -f python` match, which per §7
is not evidence the suite is running; the summary per §3 is
authoritative (assuming §11 log provenance holds — e.g. the log was
truncated or uniquely created for this run).
