"""Offline Streamlit interaction checks; live transcript evidence is separate."""
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from streamlit.testing.v1 import AppTest
from providers.base import ModelResponse, ToolCall
import ui_session


class Provider:
    default_model = 'offline-ui-test'

    def __init__(self):
        self.messages = []
        self.responses = [
            ModelResponse(tool_calls=[ToolCall('check_service_status', {'service': 'vpn', 'environment': 'production'})]),
            ModelResponse(text='{"reply":"VPN is degraded.","intent":"status","action":"answer","evidence_ids":["INC-1042"]}'),
            ModelResponse(tool_calls=[ToolCall('inspect_device', {'asset_id': 'LT-999999', 'check': 'network'})]),
            ModelResponse(text='The asset was not found.'),
            RuntimeError('Synthetic provider failure'),
        ]

    def complete(self, messages, *args, **kwargs):
        self.messages.append(messages)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def main():
    temp_root = ROOT / 'transcripts'
    temp_root.mkdir(exist_ok=True)
    provider = Provider()
    with tempfile.TemporaryDirectory(prefix='ui-check-', dir=temp_root) as folder:
        assert Path(folder).resolve().is_relative_to(temp_root.resolve())
        with patch.object(ui_session, 'TRANSCRIPTS_DIR', Path(folder)), \
             patch.object(ui_session, 'make_provider', return_value=provider):
            app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30).run()
            assert not app.exception
            assert len(app.chat_input) == 1
            app.chat_input[0].set_value('Check VPN production').run()
            assert not app.exception
            assert any(m.value == 'VPN is degraded.' for m in app.markdown)
            assert len(app.get('json')) >= 2, 'Arguments and results must render'
            chat = app.session_state['chat']
            assert len(chat.transcript['turns']) == 1 and chat.path.exists()
            assert json.loads(chat.path.read_text(encoding='utf-8'))['turns'][0]['status'] == 'answered'
            calls = len(provider.messages)
            app.run()
            assert len(provider.messages) == calls, 'A rerun must not resubmit a message'
            app.chat_input[0].set_value('Now inspect LT-999999 network').run()
            assert not app.exception
            assert any(e.value == 'asset_not_found' for e in app.error)
            assert any(m.get('content') == 'Check VPN production' for m in provider.messages[2]), 'History lost'
            app.chat_input[0].set_value('Trigger provider failure').run()
            assert not app.exception
            assert any('Could not get a model response' in e.value for e in app.error)
            chat = app.session_state['chat']
            assert len(chat.transcript['turns']) == 3
            assert chat.transcript['turns'][-1]['error'] == 'RuntimeError'
            assert 'Synthetic provider failure' not in chat.export()
            assert len(chat.history) == 4, 'Failed provider turn should not pollute successful history'
            old_path = chat.path
            next(b for b in app.button if b.label == 'New chat').click().run()
            assert not app.exception
            assert not app.session_state['chat'].transcript['turns']
            assert old_path.exists(), 'New chat must preserve previous saved transcript'
            app.selectbox[0].select('gemini').run()
            assert app.session_state['chat'].provider_name == 'gemini'
    output = {'mode': 'offline Streamlit AppTest with fake provider and real local tools',
              'passed': True, 'checks': ['app renders', 'chat submission', 'JSON reply extraction',
              'tool arguments/results render', 'tool errors visible', 'history carried',
              'rerun does not repeat calls', 'provider error displayed and saved safely',
              'transcript saved', 'new chat preserves old file', 'provider switch starts new session']}
    (ROOT / 'artifacts/evidence/ui_checks.json').write_text(json.dumps(output, indent=2), encoding='utf-8')
    print('PASS:', ', '.join(output['checks']))


if __name__ == '__main__':
    main()
