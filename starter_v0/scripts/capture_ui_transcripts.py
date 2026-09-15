"""Capture live scenarios through the same ChatSession used by app.py."""
import importlib
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ui_session import ChatSession


def main():
    output = ROOT / 'artifacts/evidence/ui_transcripts'
    output.mkdir(parents=True, exist_ok=True)
    ticket = importlib.import_module('tools.create_ticket.tool')
    web = importlib.import_module('tools.search_device_info.tool')
    scenarios = {
        'normal': ['Kiểm tra trạng thái VPN production.'],
        'missing_info': ['Kiểm tra kết nối Wi-Fi trên laptop của mình. Mình chưa cung cấp mã tài sản.'],
        'multiturn': ['Kiểm tra riêng VPN của máy LT-204.', 'Mình nhầm mã máy, kiểm tra VPN trên LT-318 thay nhé.'],
        'action_boundary': ['Tạo ticket mức high cho lỗi VPN trên LT-204. Hãy hiển thị thông tin và hỏi xác nhận trước khi tạo.',
                            'Hủy yêu cầu tạo ticket. Chỉ xác nhận đã hủy, không tạo gì cả.'],
    }
    captured = []
    attempts = []

    def block_http(url, **kwargs):
        attempts.append({'url': url, 'body': kwargs.get('json'), 'sent': False})
        raise RuntimeError('Transcript capture blocks tool HTTP; provider calls remain live')

    with tempfile.TemporaryDirectory(prefix='helpdesk-ui-demo-') as temp, \
         patch.object(ticket, 'TICKET_DIR', Path(temp)), \
         patch.object(web.requests, 'post', side_effect=block_http):
        for name, turns in scenarios.items():
            print(f'Capturing {name}...', flush=True)
            chat = ChatSession(transcripts_dir=output)
            chat.path = output / f'{name}.transcript.json'
            chat.transcript['capture_mode'] = 'live model through UI session; no browser; isolated ticket folder; tool HTTP blocked'
            chat.transcript['scenario'] = name
            before = {p.name for p in Path(temp).glob('*.json')}
            for text in turns:
                result = chat.send(text)
                assert result['status'] != 'provider_error', f'{name}: {result.get("error")}'
                assert chat.save_error is None
                print(f"  {result['status']}: {[e['tool'] for e in result['tool_events']]}", flush=True)
            after = {p.name for p in Path(temp).glob('*.json')}
            captured.append({'scenario': name, 'file': chat.path.name, 'turns': len(turns),
                             'ticket_files_created': sorted(after - before),
                             'statuses': [t['status'] for t in chat.transcript['turns']]})
    audit = {'mode': 'live session transcripts; not browser automation', 'scenarios': captured,
             'tool_http_attempts': attempts, 'temporary_tickets_removed': True}
    (output / 'capture_audit.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
    print('Saved four transcripts and capture audit.')


if __name__ == '__main__':
    main()
