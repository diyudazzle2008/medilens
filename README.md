# 🩺 MediLens

**Your health, made understandable.**

MediLens is an AI-powered healthcare accessibility prototype that helps people understand their medical reports in their own language, by text, voice, or read-aloud.

> ⚠️ Demo prototype. MediLens gives information only, not medical advice. It never diagnoses or prescribes. Always consult a doctor. Use sample or fake data only.

## 🔗 Live demo
PASTE-YOUR-STREAMLIT-LINK-HERE

## ✨ Features

**📄 Understand Reports (core feature)**
- Upload a photo or PDF, or use the camera
- Colour-coded results: normal, a bit off, needs attention
- Shows the exact line from the report behind each explanation
- Questions to ask your doctor, plus a downloadable summary

**🧠 Explain-Back AI**
- Asks simple questions to check you understood
- Gently corrects misunderstandings and re-explains in simpler words

**🌐 Languages and voice**
- 15 languages. Tested: English, Tamil, Hindi. The rest are beta
- Interface translated into Tamil and Hindi
- Read aloud on explanations
- Ask questions by voice

**📷 Check a Concern**
- Photo-based guidance for minor visible concerns
- Describes what is visible, with uncertainty, first-aid information and warning signs
- Never recommends specific medicines

**🗂️ My Health Space**
- Family profiles, saved reports by date, side-by-side report comparison
- Demo storage only: data lasts for the browser session

**🌿 Wellness Tools**
- BMI calculator, manual health-readings log, private period tracker

## 🛡️ Safety and honesty
- No diagnosis and no medicine prescriptions
- Emergency banner on the home screen
- Uncertainty and doctor-consultation reminders throughout
- Smartphones cannot measure blood pressure or oxygen, so readings are entered manually
- No real hospital integration. This would need authorised access
- Free-tier AI requests may be used by the provider to improve its products, so use sample data only

## 🛠️ Built with
Python, Streamlit, Google Gemini API (free tier), gTTS

## ▶️ Run locally
1. Install Python 3.12
2. Run: pip install -r requirements.txt
3. Create .streamlit/secrets.toml containing: GEMINI_API_KEY = "your-key"
4. Run: python -m streamlit run app.py

## 🚧 Limitations and future work
- Tamil and Hindi are tested; other languages need native-speaker review
- Real login and secure storage not yet built
- Hospital record integration and wearable connections planned
- Free-tier rate limits apply

Built for a hackathon.
