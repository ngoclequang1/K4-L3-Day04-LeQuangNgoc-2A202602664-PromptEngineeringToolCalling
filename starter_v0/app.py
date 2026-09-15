"""Run with: python -m streamlit run app.py"""
import streamlit as st

from ui_session import ChatSession, display_reply

st.set_page_config(page_title='IT Helpdesk', page_icon='💬', layout='centered')
st.title('IT Helpdesk')
st.caption('Northstar Labs · Fictional lab data · Local chat demo')

with st.sidebar:
    st.header('Chat settings')
    provider_name = st.selectbox('Provider', ['openrouter', 'openai', 'anthropic', 'gemini'])
    model = st.text_input('Model (optional)', placeholder='Leave blank for provider default').strip()
    reset = st.button('New chat', use_container_width=True)

config = (provider_name, model)
if reset or 'chat' not in st.session_state or st.session_state.get('config') != config:
    st.session_state.chat = ChatSession(provider_name, model or None)
    st.session_state.config = config
chat = st.session_state.chat

with st.sidebar:
    st.caption(f"Model: {chat.model}")
    st.caption('Artifact version')
    st.code(chat.transcript['artifact_version'], language=None)
    with st.expander('Artifact hashes'):
        st.text(f"Prompt: {chat.transcript['prompt_hash']}")
        st.text(f"Tools: {chat.transcript['tools_hash']}")
    st.download_button('Download transcript', data=chat.export(),
                       file_name=chat.path.name, mime='application/json',
                       disabled=not chat.transcript['turns'], use_container_width=True)
    if chat.transcript['turns']:
        st.caption('Transcript file')
        st.text(str(chat.path))

if not chat.transcript['turns']:
    st.info('Ask about a service, device, account, or IT guide.')
    st.caption('Try: “Dịch vụ VPN production hiện có đang gặp sự cố không?”')

for turn in chat.transcript['turns']:
    with st.chat_message('user'):
        st.markdown(turn['user'])
    with st.chat_message('assistant'):
        if turn['status'] == 'provider_error':
            st.error(turn['assistant_text'])
            st.caption(turn.get('error', 'Provider error'))
        else:
            st.markdown(display_reply(turn.get('assistant_text')))
        status = {'answered': 'Answered', 'waiting_for_user': 'Waiting for your reply',
                  'max_tool_rounds': 'Round limit reached', 'provider_error': 'Provider error'}
        st.caption(f"{status.get(turn['status'], turn['status'])} · {len(turn['rounds'])} model round(s)")
        if turn['rounds']:
            with st.expander('Tool calls and results'):
                for round_record in turn['rounds']:
                    st.markdown(f"**Round {round_record['round']}**")
                    events = round_record['tool_results']
                    if not events:
                        st.caption('No tool calls.')
                    for event in events:
                        st.markdown(f"**{event['tool']}**")
                        st.caption('Arguments')
                        st.json(event['args'])
                        result = event.get('result', {})
                        st.caption('Result / error')
                        if result.get('error'):
                            st.error(str(result['error']))
                        st.json(result)
        with st.expander('Raw assistant response'):
            st.code(turn.get('assistant_text') or '', language=None)

if chat.save_error:
    st.warning(chat.save_error)

if user_text := st.chat_input('Ask IT Helpdesk…'):
    with st.spinner('Checking…'):
        chat.send(user_text)
    st.rerun()
