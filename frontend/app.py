import streamlit as st
import requests

st.set_page_config(page_title="AI Account Intelligence", page_icon="🎯", layout="wide")

st.markdown("""
<style>
.big-title { font-size: 2.5rem; font-weight: 800; color: #667eea; }
.card { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem; }
.card-label { font-size: 0.75rem; font-weight: 600; color: #9ca3af; text-transform: uppercase; }
.card-val { font-size: 1.1rem; font-weight: 700; color: #111827; }
.green { color: #16a34a; font-size: 1.8rem; font-weight: 800; }
.yellow { color: #d97706; font-size: 1.8rem; font-weight: 800; }
.gray { color: #6b7280; font-size: 1.8rem; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🎯 AI Account Intelligence</div>', unsafe_allow_html=True)
st.markdown("**Enrich any company or IP into a full B2B sales intelligence profile instantly.**")
st.markdown("---")

col1, col2, col3 = st.columns([3, 1.5, 1])
with col1:
    user_input = st.text_input("", placeholder="Type company name e.g. Figma  or IP e.g. 104.18.2.161")
with col2:
    input_type = st.selectbox("", ["Company Name", "IP Address"])
with col3:
    go = st.button("🔍 Enrich", use_container_width=True)

st.caption("Try: `Figma` · `HubSpot` · `Postman` · `Zepto` · IP: `104.18.2.161`")

if go and user_input.strip():
    with st.spinner(f"Enriching {user_input}..."):
        try:
            payload = {"company_name": user_input} if input_type == "Company Name" else {"ip_address": user_input}
            r = requests.post("http://localhost:8000/enrich", json=payload, timeout=30)
            r.raise_for_status()
            d = r.json()["data"]
            t = r.json()["processing_time_seconds"]
            st.success(f"✅ Done in {t}s")

            # Company Profile
            st.markdown("### 🏢 Company Profile")
            c1,c2,c3,c4,c5 = st.columns(5)
            with c1: st.markdown(f'<div class="card"><div class="card-label">Company</div><div class="card-val">{d.get("company_name","—")}</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="card"><div class="card-label">Domain</div><div class="card-val">{d.get("domain","—")}</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="card"><div class="card-label">Industry</div><div class="card-val">{d.get("industry","—")}</div></div>', unsafe_allow_html=True)
            with c4: st.markdown(f'<div class="card"><div class="card-label">Size</div><div class="card-val">{d.get("company_size","—")}</div></div>', unsafe_allow_html=True)
            with c5: st.markdown(f'<div class="card"><div class="card-label">HQ</div><div class="card-val">{d.get("headquarters","—")}</div></div>', unsafe_allow_html=True)

            # Intent
            st.markdown("### 📊 Intent Intelligence")
            score = d.get("intent_score", 0)
            stage = d.get("intent_stage", "Awareness")
            persona = d.get("persona", {})
            css = "green" if score >= 7.5 else "yellow" if score >= 4.5 else "gray"
            badge = "🟢" if "Purchase" in stage else "🟡" if "Evaluation" in stage else "🔵"

            s1,s2,s3 = st.columns(3)
            with s1: st.markdown(f'<div class="card" style="text-align:center"><div class="card-label">Intent Score</div><div class="{css}">{score}/10</div></div>', unsafe_allow_html=True)
            with s2: st.markdown(f'<div class="card" style="text-align:center"><div class="card-label">Stage</div><div class="card-val">{badge} {stage}</div></div>', unsafe_allow_html=True)
            with s3: st.markdown(f'<div class="card"><div class="card-label">Buyer Persona</div><div class="card-val">{persona.get("title","—")}</div><div style="color:#9ca3af">{int(persona.get("confidence",0)*100)}% confidence</div></div>', unsafe_allow_html=True)

            # Tech Stack
            st.markdown("### 🛠️ Tech Stack")
            tech = d.get("tech_stack", {})
            t1,t2,t3,t4 = st.columns(4)
            with t1: st.markdown(f'<div class="card"><div class="card-label">CRM</div><div class="card-val">{tech.get("crm") or "—"}</div></div>', unsafe_allow_html=True)
            with t2: st.markdown(f'<div class="card"><div class="card-label">Analytics</div><div class="card-val">{tech.get("analytics") or "—"}</div></div>', unsafe_allow_html=True)
            with t3: st.markdown(f'<div class="card"><div class="card-label">Marketing</div><div class="card-val">{tech.get("marketing") or "—"}</div></div>', unsafe_allow_html=True)
            with t4:
                other = tech.get("other", [])
                st.markdown(f'<div class="card"><div class="card-label">Other</div><div class="card-val">{", ".join(other) if other else "—"}</div></div>', unsafe_allow_html=True)

            # Leadership + Signals
            st.markdown("### 👥 Leadership  &  📡 Business Signals")
            lc, sc = st.columns(2)
            with lc:
                st.markdown("**Leadership Contacts**")
                for p in d.get("leadership", []):
                    link = f' [🔗]({p["linkedin_url"]})' if p.get("linkedin_url") else ""
                    st.markdown(f'<div style="background:#fff;border-left:4px solid #667eea;padding:8px 12px;margin-bottom:6px;border-radius:0 8px 8px 0"><b>{p.get("name")}</b> — {p.get("title")}{link}</div>', unsafe_allow_html=True)
            with sc:
                st.markdown("**Business Signals**")
                for sig in d.get("business_signals", []):
                    st.markdown(f'<div style="background:#fff;border-left:4px solid #f59e0b;padding:8px 12px;margin-bottom:6px;border-radius:0 8px 8px 0"><b>[{sig.get("signal_type")}]</b> {sig.get("summary")}</div>', unsafe_allow_html=True)

            # AI Summary
            st.markdown("### 🤖 AI Sales Summary")
            st.markdown(f'<div style="background:#f0f4ff;border:1px solid #667eea44;border-radius:12px;padding:1rem 1.5rem;font-size:0.95rem;line-height:1.7">{d.get("ai_summary","—")}</div>', unsafe_allow_html=True)

            # Actions
            st.markdown("### ⚡ Recommended Sales Actions")
            for i, action in enumerate(d.get("recommended_actions", []), 1):
                st.markdown(f'<div style="background:#fff;border-left:4px solid #10b981;padding:8px 12px;margin-bottom:6px;border-radius:0 8px 8px 0"><b>Step {i}:</b> {action}</div>', unsafe_allow_html=True)

            # Raw JSON
            with st.expander("🔍 View Raw JSON"):
                st.json(d)

        except requests.exceptions.ConnectionError:
            st.error("❌ API not running! Open a new terminal and run: uvicorn api.main:app --reload --port 8000")
        except Exception as e:
            st.error(f"❌ Error: {e}")

elif go:
    st.warning("⚠️ Please enter a company name or IP first!")
else:
    st.info("👆 Enter a company name or IP address above and click Enrich to get started!")