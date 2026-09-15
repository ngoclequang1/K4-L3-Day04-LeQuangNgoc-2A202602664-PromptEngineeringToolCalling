# Simple IT Helpdesk UI

## Start

Double-click `start_ui.bat`, or run from `starter_v0/`:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address=127.0.0.1 --server.port=8501 --browser.gatherUsageStats=false
```

Open **http://127.0.0.1:8501**. If it is already running on this port, use the existing page. Stop the server with Ctrl+C in its terminal.

Dependencies are in `requirements.txt`; this implementation was tested with Streamlit 1.63.0. On a new environment, install them with `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`. The provider key stays in the existing `.env`; the default provider is OpenRouter. No key needs to be pasted into the chat.

## Use

1. Type a request in the chat box.
2. Open **Tool calls and results** below a response to see each round, tool name, arguments, result, and any tool error.
3. Reply in the chat when the agent asks for missing information or confirmation.
4. Use **Download transcript** to export the conversation. Turns also save automatically under `transcripts/`.
5. **New chat** clears the current conversation while preserving its saved file. Changing provider/model starts a new conversation too.

The sidebar shows the exact model, artifact version, hashes, and transcript path. Artifacts are frozen when a conversation starts; start a new chat after editing them. A modified artifact is labeled `working` instead of claiming to be the tested v3 snapshot.

`app.py` uses `ui_session.ChatSession`, which calls the existing `chat.run_model_tool_loop`. There is no second agent loop. The visible reply extracts `reply` when the model returns JSON; the raw response remains available in an expander and the transcript. Five prior user/assistant exchanges are retained as model context, matching the CLI default.

## Saved Step 5 evidence

These are live OpenRouter runs through the same session code used by the UI; they are not recordings of browser clicks. Separate Streamlit AppTest checks exercise the screen with an offline provider and real local tools.

| Requirement | Transcript | Observed behavior |
|---|---|---|
| Normal request | [normal](artifacts/evidence/ui_transcripts/normal.transcript.json) | Read VPN production status and summarized the degraded service |
| Missing information | [missing_info](artifacts/evidence/ui_transcripts/missing_info.transcript.json) | Asked for an asset ID and paused |
| Multi-turn correction | [multiturn](artifacts/evidence/ui_transcripts/multiturn.transcript.json) | Inspected LT-204 VPN, then used corrected LT-318 on the next turn |
| Action boundary | [action_boundary](artifacts/evidence/ui_transcripts/action_boundary.transcript.json) | Presented the ticket payload for confirmation, then accepted cancellation without creating a ticket |

[Capture audit](artifacts/evidence/ui_transcripts/capture_audit.json): six user turns, zero provider errors, no ticket writes and no tool HTTP attempts. Capture isolated ticket output and blocked tool HTTP; the normal UI uses the existing tool implementations without that capture harness.

[UI checks](artifacts/evidence/ui_checks.json) cover rendering, submitting a message, argument/result displays, history, tool and provider errors, saving transcripts, no duplicate submission on rerun, resetting, and changing provider. Run them with `python scripts/check_ui.py`; no model API requests are made.

## Known limits

This is a local lab UI. The [Step 4 safety findings](artifacts/TEAM-SAFETY-EVIDENCE.md) remain; the UI does not repair confirmation or external-data enforcement. Use fictional lab inputs. Saved transcripts may include internal fixture details, so review exports before sharing.

The live responses sometimes use English/plain text despite the Vietnamese input and JSON instruction. The UI displays these responses without changing the tested prompt. Normal/tool-assisted replies were reviewed against tool results; the first multi-turn reply adds a generic troubleshooting suggestion beyond the stored snapshot. No claim of fixing the device is made.

A provider failure is displayed and saved by error type without its raw error body. The existing loop does not return partial rounds if a later provider request throws, so such a failed turn may omit earlier tool activity; check actual side effects before retrying a write. Local save failures keep the conversation available for download.
