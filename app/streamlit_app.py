# from __future__ import annotations

# import json
# import os
# from datetime import date, datetime, time, timezone
# from pathlib import Path

# import streamlit as st

# try:
#     from api_client import APIError, analyze_task, get_health, get_metadata, schedule_tasks
# except ImportError:
#     from app.api_client import APIError, analyze_task, get_health, get_metadata, schedule_tasks

# PROJECT_ROOT = Path(__file__).resolve().parents[1]
# EDA_ROOT = PROJECT_ROOT / 'notebooks' / 'outputs' / 'milestone_01_eda'

# st.set_page_config(page_title='Adaptive Timeline', page_icon=None, layout='wide', initial_sidebar_state='expanded')

# st.markdown('''
# <style>
# @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
# :root { --ink:#172033; --muted:#657089; --line:#e6eaf0; --navy:#14213d; --blue:#4f66e8; --teal:#11a899; --amber:#f3a63b; --rose:#df6b7d; }
# html, body, [class*="css"] { font-family:'DM Sans', sans-serif; }
# .stApp { background:linear-gradient(180deg,#f8faff 0%,#ffffff 38%); color:var(--ink); }
# [data-testid="stSidebar"] { background:#111a2d; border-right:1px solid #22304e; }
# [data-testid="stSidebar"] * { color:#dbe5ff !important; }
# [data-testid="stSidebar"] .stCaption { color:#91a4cb !important; }
# [data-testid="stSidebar"] input,
# [data-testid="stSidebar"] textarea,
# [data-testid="stSidebar"] [data-baseweb="select"] > div,
# [data-testid="stSidebar"] [data-baseweb="input"] > div { background:#ffffff !important; color:#172033 !important; }
# [data-testid="stSidebar"] [data-baseweb="select"] *,
# [data-testid="stSidebar"] [data-baseweb="input"] * { color:#172033 !important; }
# /* Streamlit's time_input text lives on the input element itself. */
# [data-testid="stSidebar"] input,
# [data-testid="stSidebar"] input[type="text"],
# [data-testid="stSidebar"] input[type="time"],
# [data-testid="stSidebar"] [data-baseweb="input"] input {
#     color:#172033 !important;
#     -webkit-text-fill-color:#172033 !important;
#     caret-color:#172033 !important;
#     opacity:1 !important;
# }
# [data-testid="stSidebar"] input::placeholder {
#     color:#657089 !important;
#     -webkit-text-fill-color:#657089 !important;
#     opacity:1 !important;
# }
# /* Chromium renders native time fields through these internal parts. */
# [data-testid="stSidebar"] input[type="time"]::-webkit-datetime-edit,
# [data-testid="stSidebar"] input[type="time"]::-webkit-datetime-edit-fields-wrapper,
# [data-testid="stSidebar"] input[type="time"]::-webkit-datetime-edit-text,
# [data-testid="stSidebar"] input[type="time"]::-webkit-datetime-edit-hour-field,
# [data-testid="stSidebar"] input[type="time"]::-webkit-datetime-edit-minute-field,
# [data-testid="stSidebar"] input[type="time"]::-webkit-datetime-edit-second-field,
# [data-testid="stSidebar"] input[type="time"]::-webkit-datetime-edit-ampm-field {
#     color:#172033 !important;
#     -webkit-text-fill-color:#172033 !important;
# }
# [data-testid="stSidebar"] .badge.ok { color:#087e71 !important; }
# [data-testid="stSidebar"] .badge.warn { color:#9a6110 !important; }
# [data-testid="stSidebar"] .badge.urgent { color:#b33c51 !important; }
# .block-container { max-width:1440px; padding:2.2rem 3rem 4rem; }
# .brand { color:#8fa6ff; font-size:.72rem; letter-spacing:.18em; font-weight:700; margin-bottom:1rem; }
# .hero h1 { font-family:'Space Grotesk'; font-size:3.25rem; line-height:1.04; letter-spacing:-.06em; margin:0; color:#14213d; }
# .hero p { max-width:720px; color:var(--muted); font-size:1.05rem; line-height:1.65; margin-top:1rem; }
# .eyebrow { color:#4f66e8; text-transform:uppercase; letter-spacing:.12em; font-size:.7rem; font-weight:700; }
# .panel { background:white; border:1px solid var(--line); border-radius:18px; padding:1.25rem 1.35rem; box-shadow:0 12px 34px rgba(25,42,73,.055); }
# .card-label { color:#7b879d; text-transform:uppercase; letter-spacing:.1em; font-size:.66rem; font-weight:700; }
# .card-value { color:#172033; font-family:'Space Grotesk'; font-size:1.42rem; font-weight:700; margin-top:.4rem; }
# .card-sub { color:#7b879d; font-size:.8rem; margin-top:.25rem; }
# .metric-row { display:flex; gap:.8rem; flex-wrap:wrap; margin:1.5rem 0; }
# .metric { min-width:170px; flex:1; background:#fff; border:1px solid var(--line); border-radius:15px; padding:1rem 1.1rem; }
# .metric.blue { border-top:3px solid #4f66e8; } .metric.teal { border-top:3px solid #11a899; } .metric.amber { border-top:3px solid #f3a63b; } .metric.rose { border-top:3px solid #df6b7d; }
# .metric .label { color:#7b879d; font-size:.68rem; text-transform:uppercase; letter-spacing:.1em; font-weight:700; }
# .metric .value { color:#172033; font-family:'Space Grotesk'; font-size:1.35rem; font-weight:700; margin-top:.35rem; }
# .metric .hint { color:#8b94a6; font-size:.76rem; margin-top:.25rem; }
# .badge { display:inline-block; border-radius:999px; padding:.33rem .66rem; font-size:.72rem; font-weight:700; background:#eef1ff; color:#4257ce; }
# .badge.ok { background:#e7faf6; color:#087e71; } .badge.warn { background:#fff5e7; color:#9a6110; } .badge.urgent { background:#ffedf0; color:#b33c51; }
# .section-title { font-family:'Space Grotesk'; color:#172033; font-size:1.25rem; font-weight:700; margin:.2rem 0 .2rem; }
# .section-subtitle { color:#7b879d; font-size:.86rem; margin-bottom:1rem; }
# .reason { border-left:3px solid #11a899; background:#f5fbfa; padding:.72rem .9rem; border-radius:0 10px 10px 0; color:#405168; font-size:.86rem; margin:.45rem 0; }
# .warning { border-left:3px solid #f3a63b; background:#fff9ef; padding:.72rem .9rem; border-radius:0 10px 10px 0; color:#725321; font-size:.82rem; margin:.4rem 0; }
# .quadrant { border-radius:16px; padding:1.25rem; background:linear-gradient(135deg,#162443,#253d75); color:white; min-height:145px; }
# .quadrant .q-label { color:#a9baff; font-size:.7rem; text-transform:uppercase; letter-spacing:.13em; font-weight:700; }
# .quadrant .q-name { font-family:'Space Grotesk'; font-size:1.6rem; margin-top:.4rem; }
# .quadrant .q-help { color:#ced8f4; font-size:.82rem; margin-top:.35rem; }
# .small-note { color:#7b879d; font-size:.78rem; line-height:1.5; }
# [data-testid="stForm"] { border:0; padding:0; }
# .stButton > button,
# [data-testid="stFormSubmitButton"] button,
# [data-testid="stBaseButton-primary"] { border-radius:10px; border:0; background:#4f66e8 !important; color:#ffffff !important; font-weight:700; padding:.6rem 1rem; }
# .stButton > button *,
# [data-testid="stFormSubmitButton"] button *,
# [data-testid="stBaseButton-primary"] * { color:#ffffff !important; }
# .stButton > button:hover,
# [data-testid="stFormSubmitButton"] button:hover,
# [data-testid="stBaseButton-primary"]:hover { background:#3d51ca !important; color:#ffffff !important; }
# [data-testid="stBaseButton-secondary"] { color:#172033 !important; }
# [data-testid="stBaseButton-secondary"] * { color:#172033 !important; }
# [data-testid="stMetric"] { background:#fff; border:1px solid var(--line); padding:1rem; border-radius:14px; }
# footer { visibility:hidden; }
# </style>
# ''', unsafe_allow_html=True)


# def _api_status() -> dict:
#     try:
#         return get_health()
#     except APIError as exc:
#         return {'status': 'offline', 'error': str(exc), 'models': {}}


# def _iso_deadline(deadline_date: date | None, deadline_time: time | None) -> str | None:
#     if deadline_date is None:
#         return None
#     value = datetime.combine(deadline_date, deadline_time or time(23, 59))
#     return value.replace(tzinfo=timezone.utc).isoformat()


# def _metric(label: str, value: str, hint: str, style: str) -> str:
#     return f'<div class="metric {style}"><div class="label">{label}</div><div class="value">{value}</div><div class="hint">{hint}</div></div>'


# def _display_analysis(data: dict) -> None:
#     urgency = data['urgency']
#     context = data.get('context')
#     priority = data['priority']
#     importance = data['importance']
#     temporal = data['temporal']
#     quadrant = data['quadrant']
#     location = context['location']['label'] if context else 'Unavailable'
#     slot = context['time_slots'][0]['label'] if context and context['time_slots'] else 'Unavailable'
#     priority_label = priority['label'] or 'Unavailable'
#     urgency_label = 'Urgent' if urgency['is_urgent'] else 'Not urgent'
#     urgency_style = 'urgent' if urgency['is_urgent'] else ''

#     st.markdown('<div class="eyebrow">Analysis complete</div><div class="section-title">Decision layer</div><div class="section-subtitle">Predictions, explicit rules, and your input are shown separately.</div>', unsafe_allow_html=True)
#     st.markdown('<div class="metric-row">' + ''.join([
#         _metric('Best working window', slot, 'Model A · context prediction', 'blue'),
#         _metric('Likely location', location, 'Model A · context prediction', 'teal'),
#         _metric('Priority suggestion', priority_label, f"Model B · {priority.get('probability', 0) or 0:.0%} confidence", 'amber'),
#         _metric('Urgency', f"{urgency['score']:.0%} · {urgency_label}", 'Transparent rule score', 'rose'),
#     ]) + '</div>', unsafe_allow_html=True)

#     left, right = st.columns([1.35, 1], gap='large')
#     with left:
#         st.markdown('<div class="panel"><div class="section-title">Why this result?</div><div class="section-subtitle">A traceable explanation of the current task state.</div>', unsafe_allow_html=True)
#         if temporal['deadline']:
#             st.markdown(f"<div class='reason'><b>Deadline</b> · {temporal['deadline']} · source: {temporal['deadline_source']}</div>", unsafe_allow_html=True)
#         else:
#             st.markdown("<div class='reason'><b>Deadline</b> · No deadline stated or entered.</div>", unsafe_allow_html=True)
#         st.markdown(f"<div class='reason'><b>Urgency inputs</b> · deadline proximity {urgency['deadline_proximity']:.0%} · cue strength {urgency['explicit_cue_strength']:.0%} · slot recency {urgency['slot_recency']:.0%}</div>", unsafe_allow_html=True)
#         importance_text = 'Confirmed important' if importance['important'] is True else 'Confirmed not important' if importance['important'] is False else 'Not confirmed'
#         st.markdown(f"<div class='reason'><b>Importance</b> · {importance_text} · source: {importance['source']}</div>", unsafe_allow_html=True)
#         if importance.get('disagreement'):
#             st.markdown("<div class='warning'><b>Model/user disagreement</b> · your importance decision remains authoritative.</div>", unsafe_allow_html=True)
#         st.markdown('</div>', unsafe_allow_html=True)
#     with right:
#         q_help = {'Q1 - Do now':'Urgent and important', 'Q2 - Schedule':'Important, not urgent', 'Q3 - Delegate/Batch':'Urgent, not important', 'Q4 - Defer/Drop':'Neither urgent nor important', 'Unresolved':'Confirm importance to classify'}
#         st.markdown(f"<div class='quadrant'><div class='q-label'>Eisenhower quadrant</div><div class='q-name'>{quadrant}</div><div class='q-help'>{q_help.get(quadrant, '')}</div></div>", unsafe_allow_html=True)
#         st.markdown('<div style="height:.8rem"></div>', unsafe_allow_html=True)
#         effort = data['effort']
#         if effort.get('status') == 'ready':
#             effort_value = f"{effort.get('bucket')} · {effort.get('difficulty')}"
#             effort_sub = (
#                 f"{effort.get('estimated_minutes')} min typical · "
#                 f"range {effort.get('estimated_range_minutes', {}).get('low')}–{effort.get('estimated_range_minutes', {}).get('high')} min · "
#                 f"{effort.get('probability', 0):.0%} confidence"
#             )
#         else:
#             effort_value = 'Unavailable'
#             effort_sub = effort.get('reason', 'No deployable effort candidate is available.')
#         st.markdown(f"<div class='panel'><div class='card-label'>Effort layer</div><div class='card-value'>{effort_value}</div><div class='card-sub'>{effort_sub}</div></div>", unsafe_allow_html=True)

#     st.markdown('<div style="height:1.4rem"></div>', unsafe_allow_html=True)
#     st.markdown('<div class="panel"><div class="section-title">Context probabilities</div><div class="section-subtitle">Top Model A time-slot candidates; these are probabilities, not commitments.</div>', unsafe_allow_html=True)
#     if context:
#         for item in context['time_slots']:
#             st.progress(item['probability'], text=f"{item['label']} · {item['probability']:.0%}")
#     else:
#         st.info('Context model is not loaded. The API returned the rule layer and validation warnings.')
#     st.markdown('</div>', unsafe_allow_html=True)
#     if data.get('warnings'):
#         with st.expander('System notes and limitations'):
#             for warning in data['warnings']:
#                 st.markdown(f"<div class='warning'>{warning}</div>", unsafe_allow_html=True)


# def _render_sidebar() -> tuple[str, float, str, dict]:
#     st.sidebar.markdown('<div style="font-family:Space Grotesk;font-size:1.2rem;font-weight:700;color:white">AT / Adaptive Timeline</div><div class="small-note" style="margin-top:.35rem">A transparent planning layer for your next task.</div>', unsafe_allow_html=True)
#     st.sidebar.markdown('<div style="height:1.1rem"></div>', unsafe_allow_html=True)
#     health = _api_status()
#     if health.get('status') == 'ok':
#         st.sidebar.markdown('<span class="badge ok">API connected</span>', unsafe_allow_html=True)
#     elif health.get('status') == 'degraded':
#         st.sidebar.markdown('<span class="badge warn">API degraded</span>', unsafe_allow_html=True)
#     else:
#         st.sidebar.markdown('<span class="badge urgent">API offline</span>', unsafe_allow_html=True)
#         st.sidebar.caption(health.get('error', 'Start FastAPI to enable analysis.'))
#     st.sidebar.markdown('### Planning controls')
#     horizon = st.sidebar.selectbox('Planning horizon', ['day', 'week', 'month', 'year'], index=1)
#     hours = st.sidebar.slider('Available hours per day', 1.0, 12.0, 4.0, 0.5)
#     preferred_raw = st.sidebar.text_input(
#         'Preferred start',
#         value='09:00',
#         max_chars=5,
#         help='Enter a 24-hour time in HH:MM format.',
#     ).strip()
#     try:
#         preferred = datetime.strptime(preferred_raw, '%H:%M').time()
#     except ValueError:
#         st.sidebar.error('Use HH:MM format, for example 09:00.')
#         preferred = time(9, 0)
#     st.sidebar.markdown('---')
#     st.sidebar.caption('Model A predicts context. Model B suggests Jira-style priority and coarse effort. Urgency is rule-based. Importance stays yours.')
#     return horizon, hours, preferred.strftime('%H:%M'), health


# def main() -> None:
#     horizon, hours, preferred_start, health = _render_sidebar()
#     st.markdown('<div class="brand">ADAPTIVE TIMELINE / TASK INTELLIGENCE</div>', unsafe_allow_html=True)
#     st.markdown('<div class="hero"><h1>Plan your next move.</h1><p>Turn one task into a transparent decision: when and where it fits, how urgent it is, and which Eisenhower quadrant it belongs to.</p></div>', unsafe_allow_html=True)
#     st.markdown('<div style="height:1.3rem"></div>', unsafe_allow_html=True)

#     analyze_tab, planner_tab, evidence_tab = st.tabs(['Analyze a task', 'Build a plan', 'Evidence'])
#     with analyze_tab:
#         with st.form('task_analysis_form', clear_on_submit=False):
#             left, right = st.columns([1.35, 1], gap='large')
#             with left:
#                 task_title = st.text_input('Task title', placeholder='Finish the final project report', help='You can include explicit cues such as tomorrow, Friday, or ASAP.')
#                 list_title = st.text_input('List or context', value='university', placeholder='study, work, personal')
#                 description = st.text_area('Optional description', placeholder='Complete the introduction, references, and final proofreading.', height=92)
#                 importance_choice = st.radio('Importance', ['Let the model suggest', 'Important', 'Not important'], horizontal=True)
#             with right:
#                 use_deadline = st.checkbox('I have a deadline', value=False, help='Enable this before submitting if you want the deadline sent to FastAPI.')
#                 deadline_date = st.date_input('Deadline date', value=date.today(), min_value=date.today(), help='Choose the date, then submit the form. Leave the checkbox off to send no deadline.')
#                 deadline_time = st.time_input('Deadline time', value=time(17, 0), help='The selected date and time are sent as one UTC timestamp when enabled.')
#                 duration = st.number_input('Duration override (minutes)', min_value=0, max_value=1440, value=0, step=15, help='Optional user estimate. It is not a trained ground-truth label.')
#             submitted = st.form_submit_button('Analyze task', use_container_width=True)
#         if submitted:
#             if not task_title.strip():
#                 st.error('Enter a task title first.')
#             else:
#                 importance = None if importance_choice == 'Let the model suggest' else importance_choice == 'Important'
#                 payload = {
#                     'task_title': task_title,
#                     'list_title': list_title or 'general',
#                     'description': description or '',
#                     'importance': importance,
#                     'deadline': _iso_deadline(deadline_date if use_deadline else None, deadline_time if use_deadline else None),
#                     'duration_override_minutes': duration or None,
#                 }
#                 try:
#                     st.session_state['analysis'] = analyze_task(payload)
#                 except APIError as exc:
#                     st.error(str(exc))
#         if st.session_state.get('analysis'):
#             _display_analysis(st.session_state['analysis'])
#         else:
#             st.markdown('<div class="panel" style="margin-top:1.5rem"><div class="section-title">Start with one task</div><div class="section-subtitle">The backend owns preprocessing, model inference, rules, and response metadata. Streamlit only collects inputs and presents the result.</div></div>', unsafe_allow_html=True)

#     with planner_tab:
#         st.markdown('<div class="eyebrow">Planner</div><div class="section-title">Assemble a focused horizon</div><div class="section-subtitle">Add tasks with optional user durations. If no duration is provided, FastAPI uses the calibrated effort candidate when deployable, then a clearly labelled 30-minute planning block.</div>', unsafe_allow_html=True)
#         if 'tasks' not in st.session_state:
#             st.session_state['tasks'] = []
#         with st.form('add_planner_task', clear_on_submit=True):
#             c1, c2, c3 = st.columns([2.2, 1, 1])
#             with c1:
#                 p_title = st.text_input('Task', placeholder='Review lecture notes')
#             with c2:
#                 p_list = st.text_input('List', value='general')
#             with c3:
#                 p_duration = st.number_input('Minutes', min_value=0, max_value=1440, value=30, step=15)
#             p_importance = st.checkbox('Mark as important')
#             p_add = st.form_submit_button('Add to plan')
#         if p_add and p_title.strip():
#             st.session_state['tasks'].append({'task_title': p_title, 'list_title': p_list or 'general', 'importance': p_importance, 'duration_override_minutes': p_duration or None, 'deadline': None})
#         tasks = st.session_state['tasks']
#         if tasks:
#             st.dataframe(tasks, use_container_width=True, hide_index=True)
#             remove_index = st.selectbox('Remove task', ['None'] + [f'{i + 1} · {item["task_title"]}' for i, item in enumerate(tasks)])
#             if remove_index != 'None' and st.button('Remove selected task'):
#                 del tasks[int(remove_index.split(' · ', 1)[0]) - 1]
#                 st.rerun()
#             if st.button(f'Build {horizon} plan', type='primary'):
#                 try:
#                     result = schedule_tasks({'tasks': tasks, 'horizon': horizon, 'available_hours_per_day': hours, 'preferred_start_time': preferred_start})
#                     st.session_state['schedule'] = result
#                 except APIError as exc:
#                     st.error(str(exc))
#             if st.session_state.get('schedule'):
#                 result = st.session_state['schedule']
#                 st.markdown('<div style="height:1rem"></div><div class="panel"><div class="section-title">Scheduled sessions</div>', unsafe_allow_html=True)
#                 if result['sessions']:
#                     for session in result['sessions']:
#                         st.markdown(f"<div class='reason'><b>{session['task_title']}</b> · {session['start'][:16].replace('T',' ')} → {session['end'][:16].replace('T',' ')} · {session['duration_minutes']} min · {session['duration_source']} · {session['quadrant']}</div>", unsafe_allow_html=True)
#                 else:
#                     st.info('No sessions were scheduled.')
#                 if result['unscheduled']:
#                     st.warning(f"{len(result['unscheduled'])} task(s) could not fit in this horizon.")
#                 st.markdown('</div>', unsafe_allow_html=True)
#         else:
#             st.markdown('<div class="panel"><div class="section-title">Your plan is empty</div><div class="section-subtitle">Add tasks above to build a day, week, month, or year view.</div></div>', unsafe_allow_html=True)

#     with evidence_tab:
#         st.markdown('<div class="eyebrow">Evidence layer</div><div class="section-title">Dataset and model context</div><div class="section-subtitle">This view reads exported Milestone 1 artifacts. It does not train models inside Streamlit.</div>', unsafe_allow_html=True)
#         a, b, c = st.columns(3)
#         try:
#             mslatte = json.loads((EDA_ROOT / 'eda_metrics.json').read_text())
#             jira = json.loads((EDA_ROOT / 'jira_eda_metrics.json').read_text())
#             a.metric('MS-LaTTE records', f"{mslatte.get('n_records', '—'):,}" if isinstance(mslatte.get('n_records'), int) else '—', 'Context source')
#             b.metric('Jira sample', f"{jira.get('n_records', '—'):,}" if isinstance(jira.get('n_records'), int) else '—', 'Priority source')
#             c.metric('Runtime contract', 'Three model layers', 'FastAPI manifest')
#             st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
#             st.info('Effort uses a Jira transfer/proxy bucket model trained only on positive timeestimate labels. It returns S/M/L, difficulty, and a calibrated range; explicit user duration remains authoritative.')
#         except (OSError, json.JSONDecodeError):
#             st.warning('Milestone 1 EDA exports were not found at the expected project path.')


# if __name__ == '__main__':
#     main()



from __future__ import annotations

import json
from datetime import date, datetime, time, timezone, timedelta
from pathlib import Path

import streamlit as st

try:
    from api_client import APIError, analyze_task, get_health, get_metadata, schedule_tasks
except ImportError:
    from app.api_client import APIError, analyze_task, get_health, get_metadata, schedule_tasks

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EDA_ROOT = PROJECT_ROOT / 'notebooks' / 'outputs' / 'milestone_01_eda'

EGYPT_TZ = timezone(timedelta(hours=3))

st.set_page_config(
    page_title='Adaptive Timeline',
    page_icon=None,
    layout='wide',
    initial_sidebar_state='expanded'
)

st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --ink:#172033;
    --muted:#657089;
    --line:#e6eaf0;
    --navy:#14213d;
    --blue:#4f66e8;
    --teal:#11a899;
    --amber:#f3a63b;
    --rose:#df6b7d;
}

html, body, [class*="css"] {
    font-family:'DM Sans', sans-serif;
}

.stApp {
    background:linear-gradient(180deg,#f8faff 0%,#ffffff 38%);
    color:var(--ink);
}

[data-testid="stSidebar"] {
    background:#111a2d;
    border-right:1px solid #22304e;
}

[data-testid="stSidebar"] * {
    color:#dbe5ff !important;
}

[data-testid="stSidebar"] .stCaption {
    color:#91a4cb !important;
}

[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"] > div {
    background:#ffffff !important;
    color:#172033 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] *,
[data-testid="stSidebar"] [data-baseweb="input"] * {
    color:#172033 !important;
}

[data-testid="stSidebar"] input,
[data-testid="stSidebar"] input[type="text"],
[data-testid="stSidebar"] input[type="time"],
[data-testid="stSidebar"] [data-baseweb="input"] input {
    color:#172033 !important;
    -webkit-text-fill-color:#172033 !important;
    caret-color:#172033 !important;
    opacity:1 !important;
}

[data-testid="stSidebar"] input::placeholder {
    color:#657089 !important;
    -webkit-text-fill-color:#657089 !important;
    opacity:1 !important;
}

[data-testid="stSidebar"] input[type="time"]::-webkit-datetime-edit,
[data-testid="stSidebar"] input[type="time"]::-webkit-datetime-edit-fields-wrapper,
[data-testid="stSidebar"] input[type="time"]::-webkit-datetime-edit-text,
[data-testid="stSidebar"] input[type="time"]::-webkit-datetime-edit-hour-field,
[data-testid="stSidebar"] input[type="time"]::-webkit-datetime-edit-minute-field,
[data-testid="stSidebar"] input[type="time"]::-webkit-datetime-edit-second-field,
[data-testid="stSidebar"] input[type="time"]::-webkit-datetime-edit-ampm-field {
    color:#172033 !important;
    -webkit-text-fill-color:#172033 !important;
}

[data-testid="stSidebar"] .badge.ok {
    color:#087e71 !important;
}

[data-testid="stSidebar"] .badge.warn {
    color:#9a6110 !important;
}

[data-testid="stSidebar"] .badge.urgent {
    color:#b33c51 !important;
}

.block-container {
    max-width:1440px;
    padding:4rem 3rem 4rem;
}

.brand {
    color:#8fa6ff;
    font-size:.72rem;
    letter-spacing:.18em;
    font-weight:700;
    margin-bottom:1rem;
    display:block;
}

.hero {
    overflow:visible;
}

.hero h1 {
    font-family:'Space Grotesk';
    font-size:3.25rem;
    line-height:1.04;
    letter-spacing:-.06em;
    margin:0;
    color:#14213d;
    overflow:visible;
}

.hero p {
    max-width:720px;
    color:var(--muted);
    font-size:1.05rem;
    line-height:1.65;
    margin-top:1rem;
}

.eyebrow {
    color:#4f66e8;
    text-transform:uppercase;
    letter-spacing:.12em;
    font-size:.7rem;
    font-weight:700;
}

.panel {
    background:white;
    border:1px solid var(--line);
    border-radius:18px;
    padding:1.25rem 1.35rem;
    box-shadow:0 12px 34px rgba(25,42,73,.055);
}

.card-label {
    color:#7b879d;
    text-transform:uppercase;
    letter-spacing:.1em;
    font-size:.66rem;
    font-weight:700;
}

.card-value {
    color:#172033;
    font-family:'Space Grotesk';
    font-size:1.42rem;
    font-weight:700;
    margin-top:.4rem;
}

.card-sub {
    color:#7b879d;
    font-size:.8rem;
    margin-top:.25rem;
}

.metric-row {
    display:flex;
    gap:.8rem;
    flex-wrap:wrap;
    margin:1.5rem 0;
}

.metric {
    min-width:170px;
    flex:1;
    background:#fff;
    border:1px solid var(--line);
    border-radius:15px;
    padding:1rem 1.1rem;
}

.metric.blue {
    border-top:3px solid #4f66e8;
}

.metric.teal {
    border-top:3px solid #11a899;
}

.metric.amber {
    border-top:3px solid #f3a63b;
}

.metric.rose {
    border-top:3px solid #df6b7d;
}

.metric .label {
    color:#7b879d;
    font-size:.68rem;
    text-transform:uppercase;
    letter-spacing:.1em;
    font-weight:700;
}

.metric .value {
    color:#172033;
    font-family:'Space Grotesk';
    font-size:1.35rem;
    font-weight:700;
    margin-top:.35rem;
}

.metric .hint {
    color:#8b94a6;
    font-size:.76rem;
    margin-top:.25rem;
}

.badge {
    display:inline-block;
    border-radius:999px;
    padding:.33rem .66rem;
    font-size:.72rem;
    font-weight:700;
    background:#eef1ff;
    color:#4257ce;
}

.badge.ok {
    background:#e7faf6;
    color:#087e71;
}

.badge.warn {
    background:#fff5e7;
    color:#9a6110;
}

.badge.urgent {
    background:#ffedf0;
    color:#b33c51;
}

.section-title {
    font-family:'Space Grotesk';
    color:#172033;
    font-size:1.25rem;
    font-weight:700;
    margin:.2rem 0 .2rem;
}

.section-subtitle {
    color:#7b879d;
    font-size:.86rem;
    margin-bottom:1rem;
}

.reason {
    border-left:3px solid #11a899;
    background:#f5fbfa;
    padding:.72rem .9rem;
    border-radius:0 10px 10px 0;
    color:#405168;
    font-size:.86rem;
    margin:.45rem 0;
}

.warning {
    border-left:3px solid #f3a63b;
    background:#fff9ef;
    padding:.72rem .9rem;
    border-radius:0 10px 10px 0;
    color:#725321;
    font-size:.82rem;
    margin:.4rem 0;
}

.quadrant {
    border-radius:16px;
    padding:1.25rem;
    background:linear-gradient(135deg,#162443,#253d75);
    color:white;
    min-height:145px;
}

.quadrant .q-label {
    color:#a9baff;
    font-size:.7rem;
    text-transform:uppercase;
    letter-spacing:.13em;
    font-weight:700;
}

.quadrant .q-name {
    font-family:'Space Grotesk';
    font-size:1.6rem;
    margin-top:.4rem;
}

.quadrant .q-help {
    color:#ced8f4;
    font-size:.82rem;
    margin-top:.35rem;
}

.small-note {
    color:#7b879d;
    font-size:.78rem;
    line-height:1.5;
}

[data-testid="stForm"] {
    border:0;
    padding:0;
}

.stButton > button,
[data-testid="stFormSubmitButton"] button,
[data-testid="stBaseButton-primary"] {
    border-radius:10px;
    border:0;
    background:#4f66e8 !important;
    color:#ffffff !important;
    font-weight:700;
    padding:.6rem 1rem;
}

.stButton > button *,
[data-testid="stFormSubmitButton"] button *,
[data-testid="stBaseButton-primary"] * {
    color:#ffffff !important;
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover,
[data-testid="stBaseButton-primary"]:hover {
    background:#3d51ca !important;
    color:#ffffff !important;
}

[data-testid="stBaseButton-secondary"] {
    color:#172033 !important;
}

[data-testid="stBaseButton-secondary"] * {
    color:#172033 !important;
}

[data-testid="stMetric"] {
    background:#fff;
    border:1px solid var(--line);
    padding:1rem;
    border-radius:14px;
}

footer {
    visibility:hidden;
}
</style>
''', unsafe_allow_html=True)


def _api_status() -> dict:
    try:
        return get_health()
    except APIError as exc:
        return {
            'status': 'offline',
            'error': str(exc),
            'models': {}
        }


def _local_iso_datetime(
    selected_date: date | None,
    selected_time: time | None
) -> str | None:
    if selected_date is None:
        return None

    value = datetime.combine(
        selected_date,
        selected_time or time(23, 59)
    )

    return value.replace(
        tzinfo=EGYPT_TZ
    ).isoformat()


def _format_datetime(value: str | None) -> str:
    if not value:
        return 'None'

    try:
        parsed = datetime.fromisoformat(value)

        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(EGYPT_TZ)

        return parsed.strftime(
            '%Y-%m-%d %H:%M'
        )
    except (ValueError, TypeError):
        return value


def _metric(
    label: str,
    value: str,
    hint: str,
    style: str
) -> str:
    return f'<div class="metric {style}"><div class="label">{label}</div><div class="value">{value}</div><div class="hint">{hint}</div></div>'


def _display_analysis(data: dict) -> None:
    urgency = data['urgency']
    context = data.get('context')
    priority = data['priority']
    importance = data['importance']
    temporal = data['temporal']
    quadrant = data['quadrant']

    location = (
        context['location']['label']
        if context
        else 'Unavailable'
    )

    slot = (
        context['time_slots'][0]['label']
        if context and context['time_slots']
        else 'Unavailable'
    )

    priority_label = (
        priority['label']
        or 'Unavailable'
    )

    urgency_label = (
        'Urgent'
        if urgency['is_urgent']
        else 'Not urgent'
    )

    st.markdown(
        '<div class="eyebrow">Analysis complete</div>'
        '<div class="section-title">Decision layer</div>'
        '<div class="section-subtitle">Predictions, explicit rules, and your input are shown separately.</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="metric-row">' + ''.join([
            _metric(
                'Best working window',
                slot,
                'Model A · context prediction',
                'blue'
            ),
            _metric(
                'Likely location',
                location,
                'Model A · context prediction',
                'teal'
            ),
            _metric(
                'Priority suggestion',
                priority_label,
                f"Model B · {priority.get('probability', 0) or 0:.0%} confidence",
                'amber'
            ),
            _metric(
                'Urgency',
                f"{urgency['score']:.0%} · {urgency_label}",
                'Transparent rule score',
                'rose'
            ),
        ]) + '</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns(
        [1.35, 1],
        gap='large'
    )

    with left:
        st.markdown(
            '<div class="panel">'
            '<div class="section-title">Why this result?</div>'
            '<div class="section-subtitle">A traceable explanation of the current task state.</div>',
            unsafe_allow_html=True
        )

        if temporal['deadline']:
            st.markdown(
                f"<div class='reason'><b>Deadline</b> · {_format_datetime(temporal['deadline'])} · source: {temporal['deadline_source']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div class='reason'><b>Deadline</b> · No deadline stated or entered.</div>",
                unsafe_allow_html=True
            )

        st.markdown(
            f"<div class='reason'><b>Urgency inputs</b> · deadline proximity {urgency['deadline_proximity']:.0%} · cue strength {urgency['explicit_cue_strength']:.0%} · slot recency {urgency['slot_recency']:.0%}</div>",
            unsafe_allow_html=True
        )

        importance_text = (
            'Confirmed important'
            if importance['important'] is True
            else 'Confirmed not important'
            if importance['important'] is False
            else 'Not confirmed'
        )

        st.markdown(
            f"<div class='reason'><b>Importance</b> · {importance_text} · source: {importance['source']}</div>",
            unsafe_allow_html=True
        )

        if importance.get('disagreement'):
            st.markdown(
                "<div class='warning'><b>Model/user disagreement</b> · your importance decision remains authoritative.</div>",
                unsafe_allow_html=True
            )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    with right:
        q_help = {
            'Q1 - Do now': 'Urgent and important',
            'Q2 - Schedule': 'Important, not urgent',
            'Q3 - Delegate/Batch': 'Urgent, not important',
            'Q4 - Defer/Drop': 'Neither urgent nor important',
            'Unresolved': 'Confirm importance to classify'
        }

        st.markdown(
            f"<div class='quadrant'>"
            f"<div class='q-label'>Eisenhower quadrant</div>"
            f"<div class='q-name'>{quadrant}</div>"
            f"<div class='q-help'>{q_help.get(quadrant, '')}</div>"
            f"</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            '<div style="height:.8rem"></div>',
            unsafe_allow_html=True
        )

        effort = data['effort']

        if effort.get('status') == 'ready':
            effort_value = (
                f"{effort.get('bucket')} · "
                f"{effort.get('difficulty')}"
            )

            effort_sub = (
                f"{effort.get('estimated_minutes')} min typical · "
                f"range {effort.get('estimated_range_minutes', {}).get('low')}"
                f"–"
                f"{effort.get('estimated_range_minutes', {}).get('high')} min · "
                f"{effort.get('probability', 0):.0%} confidence"
            )
        else:
            effort_value = 'Unavailable'
            effort_sub = effort.get(
                'reason',
                'No deployable effort candidate is available.'
            )

        st.markdown(
            f"<div class='panel'>"
            f"<div class='card-label'>Effort layer</div>"
            f"<div class='card-value'>{effort_value}</div>"
            f"<div class='card-sub'>{effort_sub}</div>"
            f"</div>",
            unsafe_allow_html=True
        )

    st.markdown(
        '<div style="height:1.4rem"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="panel">'
        '<div class="section-title">Context probabilities</div>'
        '<div class="section-subtitle">Top Model A time-slot candidates; these are probabilities, not commitments.</div>',
        unsafe_allow_html=True
    )

    if context:
        for item in context['time_slots']:
            st.progress(
                item['probability'],
                text=f"{item['label']} · {item['probability']:.0%}"
            )
    else:
        st.info(
            'Context model is not loaded. The API returned the rule layer and validation warnings.'
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    if data.get('warnings'):
        with st.expander('System notes and limitations'):
            for warning in data['warnings']:
                st.markdown(
                    f"<div class='warning'>{warning}</div>",
                    unsafe_allow_html=True
                )


def _render_sidebar() -> tuple[str, float, str, date, dict]:
    st.sidebar.markdown(
        '<div style="font-family:Space Grotesk;font-size:1.2rem;font-weight:700;color:white">AT / Adaptive Timeline</div>'
        '<div class="small-note" style="margin-top:.35rem">A transparent planning layer for your next task.</div>',
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        '<div style="height:1.1rem"></div>',
        unsafe_allow_html=True
    )

    health = _api_status()

    if health.get('status') == 'ok':
        st.sidebar.markdown(
            '<span class="badge ok">API connected</span>',
            unsafe_allow_html=True
        )
    elif health.get('status') == 'degraded':
        st.sidebar.markdown(
            '<span class="badge warn">API degraded</span>',
            unsafe_allow_html=True
        )
    else:
        st.sidebar.markdown(
            '<span class="badge urgent">API offline</span>',
            unsafe_allow_html=True
        )
        st.sidebar.caption(
            health.get(
                'error',
                'Start FastAPI to enable analysis.'
            )
        )

    st.sidebar.markdown(
        '### Planning controls'
    )

    horizon = st.sidebar.selectbox(
        'Planning horizon',
        ['day', 'week', 'month', 'year'],
        index=1
    )

    hours = st.sidebar.slider(
        'Available hours per day',
        1.0,
        12.0,
        4.0,
        0.5
    )

    planning_start_date = st.sidebar.date_input(
        'Planning start date',
        value=date.today(),
        help='The first date from which the scheduler can place tasks.'
    )

    preferred_raw = st.sidebar.text_input(
        'Preferred start',
        value='09:00',
        max_chars=5,
        help='Enter a 24-hour time in HH:MM format.'
    ).strip()

    try:
        preferred = datetime.strptime(
            preferred_raw,
            '%H:%M'
        ).time()
    except ValueError:
        st.sidebar.error(
            'Use HH:MM format, for example 09:00.'
        )
        preferred = time(9, 0)

    st.sidebar.markdown('---')

    st.sidebar.caption(
        'Model A predicts context. Model B suggests Jira-style priority and coarse effort. Urgency is rule-based. Importance stays yours.'
    )

    return (
        horizon,
        hours,
        preferred.strftime('%H:%M'),
        planning_start_date,
        health
    )


def main() -> None:
    (
        horizon,
        hours,
        preferred_start,
        planning_start_date,
        health
    ) = _render_sidebar()

    st.markdown(
        '<div class="brand">ADAPTIVE TIMELINE / TASK INTELLIGENCE</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hero">'
        '<h1>Plan your next move.</h1>'
        '<p>Turn one task into a transparent decision: when and where it fits, how urgent it is, and which Eisenhower quadrant it belongs to.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div style="height:1.3rem"></div>',
        unsafe_allow_html=True
    )

    analyze_tab, planner_tab, evidence_tab = st.tabs(
        ['Analyze a task', 'Build a plan', 'Evidence']
    )

    # =============================================================
    # ANALYZE
    # =============================================================

    with analyze_tab:
        with st.form(
            'task_analysis_form',
            clear_on_submit=False
        ):
            left, right = st.columns(
                [1.35, 1],
                gap='large'
            )

            with left:
                task_title = st.text_input(
                    'Task title',
                    placeholder='Finish the final project report',
                    help='You can include explicit cues such as tomorrow, Friday, or ASAP.'
                )

                list_title = st.text_input(
                    'List or context',
                    value='university',
                    placeholder='study, work, personal'
                )

                description = st.text_area(
                    'Optional description',
                    placeholder='Complete the introduction, references, and final proofreading.',
                    height=92
                )

                importance_choice = st.radio(
                    'Importance',
                    [
                        'Let the model suggest',
                        'Important',
                        'Not important'
                    ],
                    horizontal=True
                )

            with right:
                use_deadline = st.checkbox(
                    'I have a deadline',
                    value=False,
                    help='Enable this before submitting if you want the deadline sent to FastAPI.'
                )

                deadline_date = st.date_input(
                    'Deadline date',
                    value=date.today(),
                    min_value=date.today()
                )

                deadline_time = st.time_input(
                    'Deadline time',
                    value=time(17, 0)
                )

                duration = st.number_input(
                    'Duration override (minutes)',
                    min_value=0,
                    max_value=1440,
                    value=0,
                    step=15
                )

            submitted = st.form_submit_button(
                'Analyze task',
                use_container_width=True
            )

        if submitted:
            if not task_title.strip():
                st.error(
                    'Enter a task title first.'
                )
            else:
                importance = (
                    None
                    if importance_choice == 'Let the model suggest'
                    else importance_choice == 'Important'
                )

                payload = {
                    'task_title': task_title,
                    'list_title': list_title or 'general',
                    'description': description or '',
                    'importance': importance,
                    'deadline': _local_iso_datetime(
                        deadline_date if use_deadline else None,
                        deadline_time if use_deadline else None
                    ),
                    'duration_override_minutes': duration or None,
                }

                try:
                    st.session_state['analysis'] = analyze_task(
                        payload
                    )
                except APIError as exc:
                    st.error(str(exc))

        if st.session_state.get('analysis'):
            _display_analysis(
                st.session_state['analysis']
            )
        else:
            st.markdown(
                '<div class="panel" style="margin-top:1.5rem">'
                '<div class="section-title">Start with one task</div>'
                '<div class="section-subtitle">The backend owns preprocessing, model inference, rules, and response metadata. Streamlit only collects inputs and presents the result.</div>'
                '</div>',
                unsafe_allow_html=True
            )

    # =============================================================
    # BUILD PLAN
    # =============================================================

    with planner_tab:
        st.markdown(
            '<div class="eyebrow">Planner</div>'
            '<div class="section-title">Assemble a focused horizon</div>'
            '<div class="section-subtitle">Add tasks with their own start date, start time, optional deadline, and duration.</div>',
            unsafe_allow_html=True
        )

        if 'tasks' not in st.session_state:
            st.session_state['tasks'] = []

        c1, c2, c3 = st.columns(
            [2.2, 1, 1]
        )

        with c1:
            p_title = st.text_input(
                'Task',
                placeholder='Review lecture notes',
                key='planner_task_title'
            )

        with c2:
            p_list = st.text_input(
                'List',
                value='general',
                key='planner_list'
            )

        with c3:
            p_duration = st.number_input(
                'Minutes',
                min_value=0,
                max_value=1440,
                value=30,
                step=15,
                key='planner_duration'
            )

        p_importance = st.checkbox(
            'Mark as important',
            key='planner_importance'
        )

        # ---------------------------------------------------------
        # START DATE
        # ---------------------------------------------------------

        st.markdown(
            '<div style="height:.8rem"></div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">Task start</div>'
            '<div class="section-subtitle">Choose the date and time when this specific task becomes available to the scheduler.</div>',
            unsafe_allow_html=True
        )

        start_option = st.radio(
            'Start date option',
            [
                'Use global planning date',
                'Choose a different date'
            ],
            horizontal=True,
            key='planner_start_option'
        )

        if start_option == 'Use global planning date':
            p_start_date = planning_start_date

            st.info(
                f'This task will start from the global planning date: {planning_start_date}'
            )
        else:
            p_start_date = st.date_input(
                'Task start date',
                value=planning_start_date,
                min_value=planning_start_date,
                key='planner_task_start_date'
            )

        p_start_time = st.time_input(
            'Task start time',
            value=time(9, 0),
            key='planner_task_start_time'
        )

        # ---------------------------------------------------------
        # DEADLINE
        # ---------------------------------------------------------

        st.markdown(
            '<div class="section-title">Task deadline</div>'
            '<div class="section-subtitle">Optionally set the latest time this task should be completed.</div>',
            unsafe_allow_html=True
        )

        has_deadline = st.checkbox(
            'This task has a deadline',
            value=False,
            key='planner_has_deadline'
        )

        p_deadline = None

        if has_deadline:
            deadline_date = st.date_input(
                'Deadline date',
                value=p_start_date,
                min_value=p_start_date,
                key='planner_deadline_date'
            )

            deadline_time = st.time_input(
                'Deadline time',
                value=time(17, 0),
                key='planner_deadline_time'
            )

            p_deadline = _local_iso_datetime(
                deadline_date,
                deadline_time
            )

        # ---------------------------------------------------------
        # ADD TASK
        # ---------------------------------------------------------

        st.markdown(
            '<div style="height:.5rem"></div>',
            unsafe_allow_html=True
        )

        if st.button(
            'Add to plan',
            use_container_width=True
        ):
            if not p_title.strip():
                st.warning(
                    'Enter a task title first.'
                )
            else:
                st.session_state['tasks'].append(
                    {
                        'task_title': p_title.strip(),
                        'list_title': p_list.strip() or 'general',
                        'description': '',
                        'importance': p_importance,
                        'duration_override_minutes': p_duration or None,
                        'deadline': p_deadline,
                        'start_date': p_start_date.isoformat(),
                        'start_time': p_start_time.strftime('%H:%M'),
                    }
                )

                st.session_state.pop(
                    'schedule',
                    None
                )

                st.success(
                    'Task added to your plan.'
                )

        tasks = st.session_state['tasks']

        # ---------------------------------------------------------
        # TASK TABLE
        # ---------------------------------------------------------

        if tasks:
            display_tasks = []

            for item in tasks:
                start_date_value = item.get(
                    'start_date'
                )

                start_time_value = item.get(
                    'start_time',
                    '09:00'
                )

                deadline_value = item.get(
                    'deadline'
                )

                display_tasks.append(
                    {
                        'Task': item['task_title'],
                        'List': item['list_title'],
                        'Minutes': item.get(
                            'duration_override_minutes'
                        ),
                        'Important': (
                            'Yes'
                            if item.get('importance')
                            else 'No'
                        ),
                        'Start': (
                            f'{start_date_value} '
                            f'{start_time_value}'
                        ),
                        'Deadline': _format_datetime(
                            deadline_value
                        ),
                    }
                )

            st.dataframe(
                display_tasks,
                use_container_width=True,
                hide_index=True
            )

            remove_index = st.selectbox(
                'Remove task',
                ['None'] + [
                    f'{i + 1} · {item["task_title"]}'
                    for i, item in enumerate(tasks)
                ]
            )

            if (
                remove_index != 'None'
                and st.button('Remove selected task')
            ):
                index = int(
                    remove_index.split(
                        ' · ',
                        1
                    )[0]
                ) - 1

                del tasks[index]

                st.session_state.pop(
                    'schedule',
                    None
                )

                st.rerun()

            # -----------------------------------------------------
            # BUILD PLAN
            # -----------------------------------------------------

            if st.button(
                f'Build {horizon} plan',
                type='primary',
                use_container_width=True
            ):
                schedule_payload = {
                    'tasks': tasks,
                    'horizon': horizon,
                    'available_hours_per_day': hours,
                    'preferred_start_time': preferred_start,
                    'start_date': planning_start_date.isoformat(),
                }

                try:
                    result = schedule_tasks(
                        schedule_payload
                    )

                    st.session_state['schedule'] = result

                except APIError as exc:
                    st.error(
                        str(exc)
                    )

            # -----------------------------------------------------
            # SCHEDULE RESULT
            # -----------------------------------------------------

            if st.session_state.get('schedule'):
                result = st.session_state['schedule']

                st.markdown(
                    '<div style="height:1rem"></div>'
                    '<div class="panel">'
                    '<div class="section-title">Scheduled sessions</div>',
                    unsafe_allow_html=True
                )

                if result['sessions']:
                    for session in result['sessions']:
                        start_text = _format_datetime(
                            session['start']
                        )

                        end_text = _format_datetime(
                            session['end']
                        )

                        deadline_text = _format_datetime(
                            session.get('deadline')
                        )

                        st.markdown(
                            f"<div class='reason'>"
                            f"<b>{session['task_title']}</b>"
                            f" · {start_text}"
                            f" → {end_text}"
                            f" · {session['duration_minutes']} min"
                            f" · {session['quadrant']}"
                            f"<br>"
                            f"<span style='font-size:.78rem'>"
                            f"Deadline: {deadline_text}"
                            f"</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                else:
                    st.info(
                        'No sessions were scheduled.'
                    )

                if result['unscheduled']:
                    st.warning(
                        f"{len(result['unscheduled'])} task(s) could not fit in this horizon."
                    )

                    for item in result['unscheduled']:
                        st.markdown(
                            f"<div class='warning'>"
                            f"<b>{item['task_title']}</b>"
                            f" · {item['reason']}"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

        else:
            st.markdown(
                '<div class="panel">'
                '<div class="section-title">Your plan is empty</div>'
                '<div class="section-subtitle">Add tasks above to build a day, week, month, or year view.</div>'
                '</div>',
                unsafe_allow_html=True
            )

    # =============================================================
    # EVIDENCE
    # =============================================================

    with evidence_tab:
        st.markdown(
            '<div class="eyebrow">Evidence layer</div>'
            '<div class="section-title">Dataset and model context</div>'
            '<div class="section-subtitle">This view reads exported Milestone 1 artifacts. It does not train models inside Streamlit.</div>',
            unsafe_allow_html=True
        )

        a, b, c = st.columns(3)

        try:
            mslatte = json.loads(
                (
                    EDA_ROOT / 'eda_metrics.json'
                ).read_text()
            )

            jira = json.loads(
                (
                    EDA_ROOT / 'jira_eda_metrics.json'
                ).read_text()
            )

            a.metric(
                'MS-LaTTE records',
                (
                    f"{mslatte.get('n_records', '—'):,}"
                    if isinstance(
                        mslatte.get('n_records'),
                        int
                    )
                    else '—'
                ),
                'Context source'
            )

            b.metric(
                'Jira sample',
                (
                    f"{jira.get('n_records', '—'):,}"
                    if isinstance(
                        jira.get('n_records'),
                        int
                    )
                    else '—'
                ),
                'Priority source'
            )

            c.metric(
                'Runtime contract',
                'Three model layers',
                'FastAPI manifest'
            )

            st.markdown(
                '<div style="height:1rem"></div>',
                unsafe_allow_html=True
            )

            st.info(
                'Effort uses a Jira transfer/proxy bucket model trained only on positive timeestimate labels. It returns S/M/L, difficulty, and a calibrated range; explicit user duration remains authoritative.'
            )

        except (
            OSError,
            json.JSONDecodeError
        ):
            st.warning(
                'Milestone 1 EDA exports were not found at the expected project path.'
            )


if __name__ == '__main__':
    main()
