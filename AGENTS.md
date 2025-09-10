Project Agent Guidelines

Purpose
- Make the assistant’s guidance easy to follow in this project.

Plain‑Language Commands
- Before any shell command, state a one‑sentence, common‑language explanation of what it does and why it’s needed.
- Prefer Windows PowerShell phrasing/examples when relevant (this repo runs on Windows paths).
- Clearly call out whether a command only reads information or will make changes.
- For commands that change files or settings, mention how to undo/revert in simple terms.
- Group related commands under one short explanation instead of explaining each line separately when they form a single action.

Communication Style
- Be concise and action‑oriented; avoid jargon where a plain word works.
- When proposing multiple steps, number them and keep each step to one sentence.
- If a step requires approvals/escalation, say so plainly and explain why in one sentence.

Repo Context
- This project includes static HTML/JS for an election chart; prefer minimal, targeted edits and keep styles consistent with existing code.
- Do not introduce unrelated tooling or broad refactors unless explicitly requested.

Validation
- When you change files, summarize what changed and where (paths), and suggest the minimal manual check to confirm it worked.
