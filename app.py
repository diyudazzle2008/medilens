import io
import json
import time
import html
import datetime as dt
import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS

st.set_page_config(page_title="MediLens", page_icon="🩺", layout="centered",
                   initial_sidebar_state="collapsed")

MODELS = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-2.5-flash"]

LANGS = {
    "English": "en", "Tamil": "ta", "Hindi": "hi",
    "Telugu (beta)": "te", "Malayalam (beta)": "ml", "Kannada (beta)": "kn",
    "Bengali (beta)": "bn", "Marathi (beta)": "mr", "Gujarati (beta)": "gu",
    "Urdu (beta)": "ur", "Spanish (beta)": "es", "French (beta)": "fr",
    "Arabic (beta)": "ar", "Chinese (beta)": "zh-CN", "Japanese (beta)": "ja",
}

T = {
    "en": {
        "tagline": "YOUR HEALTH, MADE UNDERSTANDABLE",
        "hello": "Hello! How can we help you today?",
        "reports": "Understand Reports",
        "reports_c": "Scan reports, ask questions and understand results.",
        "concern": "Check a Concern",
        "concern_c": "Upload a photo and get safe preliminary guidance.",
        "space": "My Health Space",
        "space_c": "Family profiles, saved reports and comparison.",
        "wellness": "Wellness Tools",
        "wellness_c": "BMI, health readings and period tracking.",
        "back": "← Back to home",
        "emergency": "🚨 In an emergency, call your local emergency number right away "
                     "(112 in India). Do not wait for this app.",
        "disclaimer": "Prototype for demonstration. MediLens gives information, "
                      "not medical advice. Always consult a doctor.",
        "explain": "Explain my report",
        "sample": "Try sample report",
        "read": "🔊 Read aloud",
        "quiz": "Quiz me gently",
        "your_report": "Your report, explained",
        "explainback": "🧠 Explain-Back: check your understanding",
        "ask": "💬 Ask a question about your report",
        "voice": "🎤 Ask by voice",
    },
    "ta": {
        "tagline": "உங்கள் ஆரோக்கியம், எளிதாகப் புரியும்",
        "hello": "வணக்கம்! இன்று நாங்கள் எப்படி உதவலாம்?",
        "reports": "அறிக்கைகளைப் புரிந்துகொள்ளுங்கள்",
        "reports_c": "அறிக்கையை ஸ்கேன் செய்து, கேள்விகள் கேட்டு, முடிவுகளைப் புரிந்துகொள்ளுங்கள்.",
        "concern": "பிரச்சனையைச் சரிபார்க்க",
        "concern_c": "புகைப்படம் பதிவேற்றி பாதுகாப்பான ஆரம்ப வழிகாட்டுதலைப் பெறுங்கள்.",
        "space": "என் ஆரோக்கிய இடம்",
        "space_c": "குடும்ப சுயவிவரங்கள், சேமித்த அறிக்கைகள், ஒப்பீடு.",
        "wellness": "நலவாழ்வு கருவிகள்",
        "wellness_c": "BMI, உடல்நலப் பதிவுகள், மாதவிடாய் கண்காணிப்பு.",
        "back": "← முகப்புக்குத் திரும்பு",
        "emergency": "🚨 அவசரநிலையில் உடனே உங்கள் அவசர உதவி எண்ணை அழைக்கவும் "
                     "(இந்தியாவில் 112). இந்த செயலிக்காகக் காத்திருக்க வேண்டாம்.",
        "disclaimer": "இது ஒரு மாதிரி செயலி. MediLens தகவல்களை மட்டுமே தருகிறது, "
                      "மருத்துவ ஆலோசனை அல்ல. எப்போதும் மருத்துவரை அணுகவும்.",
        "explain": "என் அறிக்கையை விளக்கு",
        "sample": "மாதிரி அறிக்கையை முயற்சி",
        "read": "🔊 சத்தமாகப் படி",
        "quiz": "மெதுவாக என்னைச் சோதி",
        "your_report": "உங்கள் அறிக்கை, எளிய விளக்கத்துடன்",
        "explainback": "🧠 புரிதல் சோதனை",
        "ask": "💬 உங்கள் அறிக்கை பற்றி கேளுங்கள்",
        "voice": "🎤 குரலில் கேளுங்கள்",
    },
    "hi": {
        "tagline": "आपका स्वास्थ्य, आसानी से समझें",
        "hello": "नमस्ते! आज हम आपकी कैसे मदद कर सकते हैं?",
        "reports": "रिपोर्ट समझें",
        "reports_c": "रिपोर्ट स्कैन करें, सवाल पूछें और नतीजे समझें।",
        "concern": "समस्या जाँचें",
        "concern_c": "फोटो अपलोड करें और सुरक्षित शुरुआती मार्गदर्शन पाएँ।",
        "space": "मेरा स्वास्थ्य स्थान",
        "space_c": "परिवार की प्रोफ़ाइल, सहेजी रिपोर्ट और तुलना।",
        "wellness": "वेलनेस टूल्स",
        "wellness_c": "BMI, स्वास्थ्य रीडिंग और पीरियड ट्रैकिंग।",
        "back": "← होम पर वापस",
        "emergency": "🚨 आपातकाल में तुरंत अपने स्थानीय आपातकालीन नंबर पर कॉल करें "
                     "(भारत में 112)। इस ऐप का इंतज़ार न करें।",
        "disclaimer": "यह एक डेमो प्रोटोटाइप है। MediLens केवल जानकारी देता है, "
                      "चिकित्सा सलाह नहीं। हमेशा डॉक्टर से सलाह लें।",
        "explain": "मेरी रिपोर्ट समझाएँ",
        "sample": "नमूना रिपोर्ट आज़माएँ",
        "read": "🔊 सुनें",
        "quiz": "मुझसे धीरे से पूछें",
        "your_report": "आपकी रिपोर्ट, आसान भाषा में",
        "explainback": "🧠 समझ की जाँच",
        "ask": "💬 अपनी रिपोर्ट के बारे में पूछें",
        "voice": "🎤 बोलकर पूछें",
    },
}

SAMPLE_REPORT = """SAMPLE LAB REPORT (demo data, not a real patient)
Date: 12-Nov-2026
Hemoglobin: 10.2 g/dL (Ref 12.0-15.5)
WBC: 7,200 /uL (Ref 4,000-11,000)
Platelets: 250,000 /uL (Ref 150,000-450,000)
Fasting Blood Sugar: 118 mg/dL (Ref 70-99)
Total Cholesterol: 224 mg/dL (Ref <200)
LDL Cholesterol: 146 mg/dL (Ref <100)
HDL Cholesterol: 48 mg/dL (Ref >50)
Triglycerides: 150 mg/dL (Ref <150)
TSH: 2.4 mIU/L (Ref 0.4-4.0)
"""

STATUS = {
    "normal": ("#dcfce7", "#16a34a", "✅ Normal"),
    "a_bit_off": ("#fef9c3", "#ca8a04", "⚠️ A bit off"),
    "needs_attention": ("#fee2e2", "#dc2626", "🔴 Needs attention"),
}

CSS = """
<style>
html, body, [class*="css"] { font-size: 18px; }
.stApp {
  background:
    radial-gradient(circle at 15% 8%, rgba(139,92,246,.38), transparent 40%),
    radial-gradient(circle at 88% 18%, rgba(34,211,238,.30), transparent 40%),
    radial-gradient(circle at 50% 100%, rgba(236,72,153,.28), transparent 45%),
    #070b1a;
  background-attachment: fixed;
}
.stApp::before {
  content: ""; position: fixed; width: 420px; height: 420px; border-radius: 50%;
  top: -120px; left: -120px; pointer-events: none; z-index: 0;
  background: radial-gradient(circle, rgba(34,211,238,.28), transparent 70%);
  animation: floaty 9s ease-in-out infinite alternate;
}
@keyframes floaty { to { transform: translate(260px, 380px) scale(1.25); } }
.block-container { animation: fadeUp .9s ease both; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(18px); }
                    to { opacity: 1; transform: translateY(0); } }
h1, h2, h3 { color: #67e8f9; text-shadow: 0 0 14px rgba(34,211,238,.55); }
.stButton > button, .stDownloadButton > button {
  background: linear-gradient(135deg, #06b6d4, #8b5cf6, #ec4899);
  background-size: 220% 220%; animation: shimmer 6s ease infinite;
  color: #fff; border: 0; border-radius: 16px; min-height: 3.2rem;
  box-shadow: 0 0 16px rgba(34,211,238,.5), 0 0 34px rgba(139,92,246,.3);
  transition: transform .2s ease, box-shadow .2s ease;
}
.stButton > button p, .stDownloadButton > button p {
  color: #fff !important; font-weight: 700; font-size: 1.05rem;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 0 26px rgba(236,72,153,.75), 0 0 50px rgba(34,211,238,.4);
}
.stButton > button[kind="primary"], button[data-testid="stBaseButton-primary"] {
  background: linear-gradient(135deg, #f59e0b, #ec4899, #8b5cf6);
  background-size: 220% 220%;
  box-shadow: 0 0 22px rgba(245,158,11,.75), 0 0 44px rgba(236,72,153,.5);
}
@keyframes shimmer { 0%,100% { background-position: 0% 50%; }
                     50% { background-position: 100% 50%; } }
.hero { text-align: center; padding: 6px 0 4px; }
.logo { font-size: 66px; animation: pulse 2.2s ease-in-out infinite;
        filter: drop-shadow(0 0 18px #22d3ee); }
@keyframes pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.12); } }
.hero-title {
  font-size: 3.2rem; font-weight: 800; letter-spacing: 1px;
  background: linear-gradient(90deg, #22d3ee, #a78bfa, #f472b6, #22d3ee);
  background-size: 300% 100%; -webkit-background-clip: text; background-clip: text;
  color: transparent; animation: flow 5s linear infinite;
}
@keyframes flow { to { background-position: 300% 0; } }
.tagline { text-align: center; letter-spacing: 2px; color: #a5f3fc; font-weight: 700;
           text-shadow: 0 0 12px rgba(34,211,238,.6); margin-bottom: 14px; }
.splash {
  position: fixed; inset: 0; z-index: 99999; display: flex; flex-direction: column;
  align-items: center; justify-content: center; pointer-events: none;
  background: radial-gradient(circle at 50% 40%, #1e1b4b, #070b1a 70%);
  animation: splashOut .9s ease 2.3s forwards;
}
.splash .logo { font-size: 110px; }
.splash .hero-title { font-size: 3.6rem; }
@keyframes splashOut { to { opacity: 0; visibility: hidden; } }
[data-testid="stAlert"] { border-radius: 14px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

DEFAULTS = {
    "page": "home", "splash_done": False, "lang_label": "English",
    "report": None, "data": None, "raw": None, "context": "", "expl_lang": None,
    "quiz": None, "feedback": None, "answer": None, "voice_answer": None,
    "concern": None, "concern_input": None, "concern_lang": None,
    "compare": None, "space": {"Me": {"reports": []}}, "vitals": [], "periods": [],
}
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)

# ---------------- Splash (first open only) ----------------
if not st.session_state.splash_done:
    st.markdown(
        "<div class='splash'><div class='logo'>🩺</div>"
        "<div class='hero-title'>MediLens</div>"
        "<div class='tagline'>YOUR HEALTH, MADE UNDERSTANDABLE</div></div>",
        unsafe_allow_html=True,
    )
    st.session_state.splash_done = True


# ---------------- Language bar (every page) ----------------
def set_lang(label):
    st.session_state.lang_label = label


QUICK = [("English", "English"), ("தமிழ்", "Tamil"), ("हिन्दी", "Hindi")]
bar = st.columns([1, 1, 1, 2])
for col, (txt, lab) in zip(bar[:3], QUICK):
    with col:
        st.button(txt, key=f"q_{lab}", on_click=set_lang, args=(lab,),
                  type="primary" if st.session_state.lang_label == lab else "secondary",
                  use_container_width=True)
with bar[3]:
    st.selectbox("🌐 More languages", list(LANGS.keys()), key="lang_label",
                 label_visibility="collapsed")

lang_label = st.session_state.lang_label
code = LANGS[lang_label]
lang = lang_label.replace(" (beta)", "")


def t(key):
    return T.get(code, {}).get(key) or T["en"][key]


def go(page):
    st.session_state.page = page


def get_client():
    try:
        key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None
    return genai.Client(api_key=key)


def system_prompt(lang):
    return (
        f"You are MediLens, a kind health-information assistant. Reply in {lang}, "
        "using very simple words a non-medical person understands. You explain medical "
        "reports and give safe, general health information. You NEVER diagnose, never "
        "prescribe or name specific medicines, and never invent values that are not in "
        "the report. Be honest about uncertainty. If anything looks seriously abnormal "
        "or urgent, say clearly to see a doctor or emergency services soon. "
        "Remind that a doctor should confirm everything."
    )


def call(contents, lang, as_json=False):
    client = get_client()
    if client is None:
        st.error("API key not found. Check .streamlit/secrets.toml")
        st.stop()
    cfg_args = {"system_instruction": system_prompt(lang)}
    if as_json:
        cfg_args["response_mime_type"] = "application/json"
    cfg = types.GenerateContentConfig(**cfg_args)
    last = None
    for model in MODELS:
        for _ in range(2):
            try:
                r = client.models.generate_content(
                    model=model, contents=contents, config=cfg)
                if r.text:
                    return r.text
            except Exception as e:
                last = e
                time.sleep(2)
    st.error(f"The AI is busy or the free limit was reached. Wait a minute and try "
             f"again. ({last})")
    st.stop()


def parse_json(text):
    try:
        return json.loads(text[text.index("{"): text.rindex("}") + 1])
    except Exception:
        return None


def report_parts():
    kind, data, mime = st.session_state.report
    if kind == "text":
        return [data]
    return [types.Part.from_bytes(data=data, mime_type=mime)]


def speak(text, lcode):
    clean = text.replace("*", "").replace("#", "").replace("_", " ").replace("|", " ")
    buf = io.BytesIO()
    gTTS(clean[:3000], lang=lcode).write_to_fp(buf)
    return buf.getvalue()


def audio_button(text, lcode, key):
    if st.button(t("read"), key=key):
        with st.spinner("..."):
            try:
                st.audio(speak(text, lcode), format="audio/mp3")
            except Exception as e:
                st.error(f"Audio failed: {e}")


def flatten(data):
    lines = [data.get("summary", "")]
    for r in data.get("results", []):
        lines.append(f"- {r.get('name','')}: {r.get('value','')} "
                     f"(range {r.get('range','')}) [{r.get('status','')}] "
                     f"{r.get('meaning','')}")
    qs = data.get("doctor_questions", [])
    if qs:
        lines.append("Questions for the doctor:")
        lines += [f"- {q}" for q in qs]
    return "\n".join(lines)


def show_results(data):
    st.markdown(f"**{html.escape(data.get('summary', ''))}**")
    for r in data.get("results", []):
        bg, bd, label = STATUS.get(r.get("status"), STATUS["normal"])
        e = lambda k: html.escape(str(r.get(k, "")))
        st.markdown(
            f"<div style='background:{bg};border-left:6px solid {bd};padding:12px 14px;"
            f"border-radius:12px;margin:8px 0;color:#111;"
            f"box-shadow:0 0 18px {bd}66'>"
            f"<b>{e('name')}</b>: {e('value')} "
            f"<span style='opacity:.7;color:#111'>(range: {e('range')})</span> "
            f"&nbsp;<b>{label}</b>"
            f"<br>{e('meaning')}"
            f"<br><small>📎 “{e('source_line')}”</small></div>",
            unsafe_allow_html=True,
        )
    qs = data.get("doctor_questions", [])
    if qs:
        st.markdown("**Questions to ask your doctor**")
        for q in qs:
            st.markdown(f"- {q}")


def back():
    st.button(t("back"), on_click=go, args=("home",))


# ---------------- Home ----------------
def home():
    st.markdown(
        "<div class='hero'><div class='logo'>🩺</div>"
        "<div class='hero-title'>MediLens</div></div>"
        f"<div class='tagline'>{html.escape(t('tagline'))}</div>",
        unsafe_allow_html=True,
    )
    st.subheader(t("hello"))
    c1, c2 = st.columns(2)
    with c1:
        st.button("📄 " + t("reports"), on_click=go, args=("reports",),
                  use_container_width=True)
        st.caption(t("reports_c"))
        st.button("🗂️ " + t("space"), on_click=go, args=("space",),
                  use_container_width=True)
        st.caption(t("space_c"))
    with c2:
        st.button("📷 " + t("concern"), on_click=go, args=("concern",),
                  use_container_width=True)
        st.caption(t("concern_c"))
        st.button("🌿 " + t("wellness"), on_click=go, args=("wellness",),
                  use_container_width=True)
        st.caption(t("wellness_c"))
    st.error(t("emergency"))
    st.info(t("disclaimer"))


# ---------------- Understand Reports ----------------
EXPLAIN_PROMPT = (
    "Explain this medical report. Return ONLY valid JSON with this shape: "
    '{"summary": "2-3 sentence overall summary", '
    '"results": [{"name": "test name", "value": "value with unit", '
    '"range": "normal range shown in the report", '
    '"status": "normal" or "a_bit_off" or "needs_attention", '
    '"meaning": "what it means in simple words", '
    '"source_line": "the exact line copied from the report, unchanged"}], '
    '"doctor_questions": ["3 questions to ask the doctor"]}. '
    "Write summary, meaning and doctor_questions in the requested language. "
    "Keep status values exactly as written in English. Never diagnose."
)


def run_explain():
    with st.spinner("..."):
        raw = call(report_parts() + [EXPLAIN_PROMPT], lang, as_json=True)
    data = parse_json(raw)
    st.session_state.data = data
    st.session_state.raw = raw
    st.session_state.context = flatten(data) if data else raw
    st.session_state.expl_lang = code
    st.session_state.quiz = None
    st.session_state.feedback = None
    st.session_state.answer = None
    st.session_state.voice_answer = None


def reports():
    back()
    st.header("📄 " + t("reports"))
    st.caption("Use sample or fake reports only. Do not upload real medical records.")

    up = st.file_uploader("Upload a report (photo or PDF)",
                          type=["png", "jpg", "jpeg", "pdf"], key="up_r")
    with st.expander("Or use your camera"):
        cam = st.camera_input("Take a photo of the report", key="cam_r")
    file = up or cam

    c1, c2 = st.columns(2)
    run = False
    with c1:
        if file and st.button(t("explain"), use_container_width=True):
            st.session_state.report = ("file", file.getvalue(), file.type)
            run = True
    with c2:
        if st.button(t("sample"), use_container_width=True):
            st.session_state.report = ("text", SAMPLE_REPORT, None)
            run = True

    if run:
        run_explain()
    elif (st.session_state.report and st.session_state.context
          and st.session_state.expl_lang != code):
        run_explain()  # language changed: explain again in the new language

    if st.session_state.context:
        st.divider()
        st.subheader(t("your_report"))
        data = st.session_state.data
        if data:
            show_results(data)
        else:
            st.markdown(st.session_state.raw)
        audio_button(st.session_state.context, code, "read1")

        b1, b2 = st.columns(2)
        with b1:
            st.download_button("⬇️ Summary for your doctor", st.session_state.context,
                               file_name="medilens_summary.txt",
                               use_container_width=True)
        with b2:
            with st.popover("💾 Save to Health Space", use_container_width=True):
                prof = st.selectbox("Profile", list(st.session_state.space.keys()),
                                    key="save_prof")
                rdate = st.date_input("Report date", dt.date.today(), key="save_date")
                if st.button("Save report", key="save_btn"):
                    st.session_state.space[prof]["reports"].append(
                        {"date": str(rdate), "context": st.session_state.context})
                    st.success(f"Saved to {prof}")

        # ---------- Explain-Back ----------
        st.divider()
        st.subheader(t("explainback"))
        if st.button(t("quiz")):
            q = ("Ask the person 2 short, friendly questions to check they understood "
                 "the most important points of this report. Do not give the answers. "
                 "Number the questions.")
            with st.spinner("..."):
                st.session_state.quiz = call(
                    report_parts() + [st.session_state.context, q], lang)
            st.session_state.feedback = None
        if st.session_state.quiz:
            st.markdown(st.session_state.quiz)
            mine = st.text_area("Type your answers in your own words", key="mine")
            if st.button("Check my answers") and mine.strip():
                q = (f"Questions:\n{st.session_state.quiz}\n\nThe person answered:\n"
                     f"{mine}\n\nKindly tell them what they understood correctly, "
                     "gently correct any misunderstanding, and re-explain that part "
                     "more simply.")
                with st.spinner("..."):
                    st.session_state.feedback = call(
                        report_parts() + [st.session_state.context, q], lang)
            if st.session_state.feedback:
                st.success("✨")
                st.markdown(st.session_state.feedback)
                audio_button(st.session_state.feedback, code, "read2")

        # ---------- Typed question ----------
        st.divider()
        st.subheader(t("ask"))
        question = st.text_input("Type your question", key="typed_q")
        if st.button("Ask") and question.strip():
            with st.spinner("..."):
                st.session_state.answer = call(
                    report_parts() + [st.session_state.context,
                                      f"Question: {question}"], lang)
        if st.session_state.answer:
            st.markdown(st.session_state.answer)
            audio_button(st.session_state.answer, code, "read3")

        # ---------- Voice question ----------
        if hasattr(st, "audio_input"):
            st.divider()
            st.subheader(t("voice"))
            st.caption("Record your question, then press the button.")
            voice = st.audio_input("Record your question")
            if voice and st.button("Answer my voice question"):
                with st.spinner("..."):
                    audio = types.Part.from_bytes(data=voice.getvalue(),
                                                  mime_type="audio/wav")
                    st.session_state.voice_answer = call(
                        report_parts() + [st.session_state.context, audio,
                                          "Listen to this spoken question about the "
                                          "report and answer it."], lang)
            if st.session_state.voice_answer:
                st.markdown(st.session_state.voice_answer)
                audio_button(st.session_state.voice_answer, code, "read4")


# ---------------- Check a Concern ----------------
def run_concern():
    b, m, d = st.session_state.concern_input
    prompt = (
        "This is a photo of a minor visible health concern, not a report. "
        f"The person says: '{d}'. Give: 1) What I can observe in the photo "
        "(only what is visible). 2) Possible general causes, clearly uncertain, "
        "never a diagnosis. 3) General first-aid and care information. "
        "4) Warning signs that mean see a doctor soon. 5) When to see a doctor. "
        "Do NOT name or recommend any specific medicine; say to ask a doctor or "
        "pharmacist about treatments. If the photo looks serious, say so first."
    )
    with st.spinner("..."):
        part = types.Part.from_bytes(data=b, mime_type=m)
        st.session_state.concern = call([part, prompt], lang)
    st.session_state.concern_lang = code


def concern():
    back()
    st.header("📷 " + t("concern"))
    st.warning("For minor visible concerns only (a rash, small wound, bite). "
               "Severe pain, heavy bleeding, trouble breathing, chest pain, or "
               "something spreading fast: call emergency services now.")
    up = st.file_uploader("Upload a photo", type=["png", "jpg", "jpeg"], key="up_c")
    with st.expander("Or use your camera"):
        cam = st.camera_input("Take a photo", key="cam_c")
    file = up or cam
    desc = st.text_input("Describe it (how long, pain, itching, fever?)", key="desc_c")

    if file and st.button("Get safe guidance", use_container_width=True):
        st.session_state.concern_input = (file.getvalue(), file.type, desc)
        run_concern()
    elif (st.session_state.concern_input and st.session_state.concern
          and st.session_state.concern_lang != code):
        run_concern()

    if st.session_state.concern:
        st.divider()
        st.markdown(st.session_state.concern)
        audio_button(st.session_state.concern, code, "read_c")
        st.caption("Trusted sources to read more: "
                   "[MedlinePlus](https://medlineplus.gov) · "
                   "[NHS](https://www.nhs.uk) · [WHO](https://www.who.int)")
        st.info("This is not a diagnosis. A doctor or pharmacist should confirm "
                "before you use any treatment.")


# ---------------- My Health Space ----------------
def space():
    back()
    st.header("🗂️ " + t("space"))
    st.caption("Demo storage: data stays only in this browser session and is lost "
               "on refresh. Real hospital connections would need authorised "
               "integration.")

    name = st.text_input("Add a family member (for example: Mother)", key="newp")
    if st.button("➕ Add profile") and name.strip():
        st.session_state.space.setdefault(name.strip(), {"reports": []})

    prof = st.selectbox("Profile", list(st.session_state.space.keys()), key="prof_sel")
    items = st.session_state.space[prof]["reports"]
    st.subheader(f"{prof}'s reports")
    if not items:
        st.info("No saved reports yet. Open Understand Reports, explain a report, "
                "then tap Save to Health Space.")
    for it in sorted(items, key=lambda x: x["date"]):
        with st.expander(f"📄 Report dated {it['date']}"):
            st.text(it["context"])

    if len(items) >= 2:
        st.divider()
        st.subheader("🔍 Compare two reports")
        ordered = sorted(items, key=lambda x: x["date"])
        labels = [f"{n + 1}. {r['date']}" for n, r in enumerate(ordered)]
        a = st.selectbox("Earlier report", labels, index=0, key="cmp_a")
        b = st.selectbox("Later report", labels, index=len(labels) - 1, key="cmp_b")
        if st.button("Compare side by side"):
            ra = ordered[labels.index(a)]
            rb = ordered[labels.index(b)]
            prompt = (
                "Compare these two reports. Make a markdown table with columns: "
                "Test | Earlier | Later | Change (higher / lower / same). Only use "
                "values written in the reports. Do not draw medical conclusions. "
                "End with one sentence telling the person to discuss changes with "
                "their doctor.\n\n"
                f"EARLIER ({ra['date']}):\n{ra['context']}\n\n"
                f"LATER ({rb['date']}):\n{rb['context']}"
            )
            with st.spinner("..."):
                st.session_state.compare = call([prompt], lang)
        if st.session_state.compare:
            st.markdown(st.session_state.compare)
            audio_button(st.session_state.compare, code, "read_cmp")


# ---------------- Wellness Tools ----------------
def wellness():
    back()
    st.header("🌿 " + t("wellness"))
    t1, t2, t3 = st.tabs(["⚖️ BMI", "❤️ Health readings", "🌸 Period tracker"])

    with t1:
        h = st.number_input("Height (cm)", 50.0, 250.0, 165.0, 1.0)
        w = st.number_input("Weight (kg)", 10.0, 300.0, 60.0, 0.5)
        if st.button("Calculate BMI"):
            bmi = w / ((h / 100) ** 2)
            if bmi < 18.5:
                cat = "below the usual range"
            elif bmi < 25:
                cat = "within the usual range"
            elif bmi < 30:
                cat = "above the usual range"
            else:
                cat = "well above the usual range"
            st.metric("Your BMI", f"{bmi:.1f}")
            st.write(f"This is {cat} for adults.")
            st.caption("BMI is only a screening number, not a diagnosis. It does "
                       "not account for muscle, age or body type. Ask a doctor.")

    with t2:
        st.caption("Enter readings from a proper device. A phone cannot measure "
                   "blood pressure or oxygen by itself.")
        c1, c2 = st.columns(2)
        with c1:
            sys_bp = st.number_input("Systolic BP", 50, 260, 120)
            pulse = st.number_input("Pulse (bpm)", 20, 220, 75)
        with c2:
            dia_bp = st.number_input("Diastolic BP", 30, 160, 80)
            spo2 = st.number_input("Oxygen SpO2 (%)", 50, 100, 98)
        if st.button("Add reading"):
            st.session_state.vitals.append(
                {"Time": dt.datetime.now().strftime("%d %b %H:%M"),
                 "Systolic": sys_bp, "Diastolic": dia_bp,
                 "Pulse": pulse, "SpO2": spo2})
        if st.session_state.vitals:
            if st.session_state.vitals:
                cols = ["Time", "Systolic", "Diastolic", "Pulse", "SpO2"]
                rows = st.session_state.vitals
                md = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n"
                for r in rows:
                    md += "| " + " | ".join(str(r[c]) for c in cols) + " |\n"
                    st.markdown(md)
                    csv = ",".join(cols) + "\n" + "\n".join(
                    ",".join(str(r[c]) for c in cols) for r in rows)
                    st.download_button("⬇️ Download readings", csv,
                               file_name="medilens_readings.csv")
        st.caption("Share trends with your doctor. For chest pain, fainting or "
                   "trouble breathing, seek emergency care.")

    with t3:
        st.caption("🔒 Private: stays only in this session. Predictions are "
                   "estimates, not medical advice.")
        d = st.date_input("First day of your period", dt.date.today(), key="pdate")
        if st.button("Add period start"):
            if d not in st.session_state.periods:
                st.session_state.periods.append(d)
        ps = sorted(st.session_state.periods)
        if ps:
            st.write("Logged start dates: " + ", ".join(str(p) for p in ps))
        if len(ps) >= 2:
            gaps = [(ps[i + 1] - ps[i]).days for i in range(len(ps) - 1)]
            avg = round(sum(gaps) / len(gaps))
            nxt = ps[-1] + dt.timedelta(days=avg)
            st.metric("Average cycle length", f"{avg} days")
            st.write(f"Estimated next period around **{nxt}**. This is only an "
                     "estimate; cycles vary.")
        elif ps:
            st.info("Add at least two dates to see an estimate.")
        if st.button("Clear period data"):
            st.session_state.periods = []


PAGES = {"home": home, "reports": reports, "concern": concern,
         "space": space, "wellness": wellness}
PAGES[st.session_state.page]()