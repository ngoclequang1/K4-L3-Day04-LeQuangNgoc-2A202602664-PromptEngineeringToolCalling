"""Session state shared by the simple UI and its transcript demos."""
from datetime import datetime
import json
from pathlib import Path
from uuid import uuid4

from chat import ROOT, now_iso, run_model_tool_loop, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

TRANSCRIPTS_DIR = ROOT / 'transcripts'


class ChatSession:
    def __init__(self, provider_name='openrouter', model=None, transcripts_dir=None):
        self.provider_name = provider_name
        self.model = model or make_provider(provider_name).default_model
        prompt_path = ROOT / 'artifacts/system_prompt.md'
        tools_path = ROOT / 'artifacts/tools.yaml'
        snapshot = ROOT / 'artifacts/versions/v3'
        version = 'v3' if all((snapshot / p.name).exists() and (snapshot / p.name).read_bytes() == p.read_bytes()
                              for p in (prompt_path, tools_path)) else 'working'
        # Freeze the exact artifacts for this conversation, including their hashes.
        self.prompt = prompt_path.read_text(encoding='utf-8')
        self.tools = to_openai_tools(load_tool_declarations(tools_path))
        session_id = f"ui_{datetime.now():%Y%m%dT%H%M%S}_{uuid4().hex[:8]}"
        self.path = Path(transcripts_dir or TRANSCRIPTS_DIR) / f'{session_id}.transcript.json'
        self.history = []
        self.transcript = {
            'transcript_id': session_id, 'surface': 'streamlit',
            **artifact_version_dict(build_artifact_version(version, prompt_path, tools_path)),
            'provider': provider_name, 'model': self.model,
            'created_at': now_iso(), 'history_window': 5, 'max_tool_rounds': 4,
            'turns': [],
        }
        self.save_error = None

    def send(self, text, provider=None):
        text = text.strip()
        if not text:
            return None
        turn = {'turn_index': len(self.transcript['turns']) + 1, 'user': text,
                'started_at': now_iso(), 'rounds': [], 'tool_events': []}
        try:
            result = run_model_tool_loop(
                provider=provider or make_provider(self.provider_name),
                messages=[{'role': 'system', 'content': self.prompt},
                          *trim_history(self.history, 5), {'role': 'user', 'content': text}],
                tools=self.tools, model=self.model, max_tool_rounds=4)
            turn.update(result)
            self.history.extend([{'role': 'user', 'content': text},
                                 {'role': 'assistant', 'content': result['assistant_text']}])
        except Exception as exc:
            # Avoid writing a provider error body that could contain authentication details.
            turn.update(status='provider_error', error=type(exc).__name__,
                        assistant_text='Could not get a model response. Check the provider key, model, and connection, then try again.')
        turn['ended_at'] = now_iso()
        self.transcript['turns'].append(turn)
        self.save_error = None
        try:
            write_transcript(self.path, self.transcript)
        except OSError:
            self.save_error = 'Could not save locally. Download the transcript to keep this conversation.'
        return turn

    def export(self):
        return json.dumps(self.transcript, ensure_ascii=False, indent=2)


def display_reply(raw):
    """Show the reply field when the model follows its JSON response contract."""
    try:
        payload = json.loads(raw)
        if isinstance(payload, dict) and isinstance(payload.get('reply'), str):
            return payload['reply']
    except (ValueError, TypeError):
        pass
    return raw or 'No text response. See the tool results below.'
