import streamlit as st
import requests

st.set_page_config(page_title="AI Account Intelligence", page_icon="🎯", layout="wide")

st.markdown("""
<style>
.big-title{font-size:2.5rem;font-weight:800;color:#667eea}
.card{background:#f9fafb;border:1px solid #e5e7eb;border-radius:12px;padding:1rem;margin-bottom:0.8rem}
.card-label{font-size:0.75rem;font-weight:600;color:#9ca3af;text-transform:uppercase}
.card-val{font-size:1.1rem;font-weight:700;color:#111827}
.green{color:#16a34a;font-size:1.8rem;font-weight:800}
.yellow{color:#d97706;font-size:1.8rem;font-weight:800}
.gray{color:#6b7280;font-size:1.8rem;font-weight:800}
.vbox{background:#f0f4ff;border:1px solid #667eea55;border-radius:12px;padding:1.2rem;margin-bottom:1rem}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RESULTS FUNCTION - defined first
# ─────────────────────────────────────────────
def show_results(d):
    st.markdown("---")
    st.markdown("### 🏢 Company Profile")
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.markdown(f'<div class="card"><div class="card-label">Company</div><div class="card-val">{d.get("company_name","—")}</div></div>',unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="card"><div class="card-label">Domain</div><div class="card-val">{d.get("domain","—")}</div></div>',unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="card"><div class="card-label">Industry</div><div class="card-val">{d.get("industry","—")}</div></div>',unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="card"><div class="card-label">Size</div><div class="card-val">{d.get("company_size","—")}</div></div>',unsafe_allow_html=True)
    with c5: st.markdown(f'<div class="card"><div class="card-label">HQ</div><div class="card-val">{d.get("headquarters","—")}</div></div>',unsafe_allow_html=True)

    st.markdown("### 📊 Intent Intelligence")
    score=d.get("intent_score",0)
    stage=d.get("intent_stage","Awareness")
    persona=d.get("persona",{})
    css="green" if score>=7.5 else "yellow" if score>=4.5 else "gray"
    badge="🟢" if "Purchase" in stage else "🟡" if "Evaluation" in stage else "🔵"
    s1,s2,s3=st.columns(3)
    with s1: st.markdown(f'<div class="card" style="text-align:center"><div class="card-label">Intent Score</div><div class="{css}">{score}/10</div></div>',unsafe_allow_html=True)
    with s2: st.markdown(f'<div class="card" style="text-align:center"><div class="card-label">Stage</div><div class="card-val">{badge} {stage}</div></div>',unsafe_allow_html=True)
    with s3: st.markdown(f'<div class="card"><div class="card-label">Buyer Persona</div><div class="card-val">{persona.get("title","—")}</div><div style="color:#9ca3af">{int(persona.get("confidence",0)*100)}% confidence</div></div>',unsafe_allow_html=True)

    st.markdown("### 🛠️ Tech Stack")
    tech=d.get("tech_stack",{})
    t1,t2,t3,t4=st.columns(4)
    with t1: st.markdown(f'<div class="card"><div class="card-label">CRM</div><div class="card-val">{tech.get("crm") or "—"}</div></div>',unsafe_allow_html=True)
    with t2: st.markdown(f'<div class="card"><div class="card-label">Analytics</div><div class="card-val">{tech.get("analytics") or "—"}</div></div>',unsafe_allow_html=True)
    with t3: st.markdown(f'<div class="card"><div class="card-label">Marketing</div><div class="card-val">{tech.get("marketing") or "—"}</div></div>',unsafe_allow_html=True)
    with t4:
        other=tech.get("other",[])
        st.markdown(f'<div class="card"><div class="card-label">Other Tools</div><div class="card-val">{", ".join(other) if other else "—"}</div></div>',unsafe_allow_html=True)

    st.markdown("### 👥 Leadership  &  📡 Business Signals")
    lc,sc=st.columns(2)
    with lc:
        st.markdown("**Leadership Contacts**")
        for p in d.get("leadership",[]):
            link=f' [🔗 LinkedIn]({p["linkedin_url"]})' if p.get("linkedin_url") else ""
            st.markdown(f'<div style="background:#fff;border-left:4px solid #667eea;padding:8px 12px;margin-bottom:6px;border-radius:0 8px 8px 0"><b>{p.get("name","Unknown")}</b> — {p.get("title","")}{link}</div>',unsafe_allow_html=True)
    with sc:
        st.markdown("**Business Signals**")
        for sig in d.get("business_signals",[]):
            st.markdown(f'<div style="background:#fff;border-left:4px solid #f59e0b;padding:8px 12px;margin-bottom:6px;border-radius:0 8px 8px 0"><b>[{sig.get("signal_type")}]</b> {sig.get("summary")}</div>',unsafe_allow_html=True)

    st.markdown("### 🤖 AI Sales Summary")
    st.markdown(f'<div style="background:#f0f4ff;border:1px solid #667eea44;border-radius:12px;padding:1rem 1.5rem;font-size:0.95rem;line-height:1.7">{d.get("ai_summary","—")}</div>',unsafe_allow_html=True)

    st.markdown("### ⚡ Recommended Sales Actions")
    for i,action in enumerate(d.get("recommended_actions",[]),1):
        st.markdown(f'<div style="background:#fff;border-left:4px solid #10b981;padding:8px 12px;margin-bottom:6px;border-radius:0 8px 8px 0"><b>Step {i}:</b> {action}</div>',unsafe_allow_html=True)

    with st.expander("🔍 View Raw JSON Output"):
        st.json(d)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="big-title">🎯 AI Account Intelligence</div>', unsafe_allow_html=True)
st.markdown("**Convert anonymous visitor signals or company names into full B2B sales intelligence — instantly.**")
st.markdown("---")

# ─────────────────────────────────────────────
# MODE SELECTOR
# ─────────────────────────────────────────────
mode = st.radio(
    "**Choose Input Mode:**",
    ["🌐 Mode 1: Website Visitor Signal (IP + Page Behavior)", "🏢 Mode 2: Company Name Only"],
    horizontal=True
)
st.markdown("---")

# ─────────────────────────────────────────────
# MODE 1: VISITOR SIGNAL - EXACTLY LIKE PDF
# ─────────────────────────────────────────────
if "Mode 1" in mode:
    st.markdown("### 📡 Website Visitor Signal")
    st.info("💡 This simulates what your website tracker captures automatically when someone visits your site — exactly like the hackathon example.")

    # Sample visitor loader
    sample = st.selectbox("⚡ Load a sample visitor (or fill manually below):", [
        "— Select a sample —",
        "Visitor 001 | IP: 104.18.2.161 | Pricing + Demo + Case Studies | 3 visits | HIGH INTENT",
        "Visitor 002 | IP: 13.32.99.10  | Features page only | 1 visit | MEDIUM INTENT",
        "Visitor 003 | IP: 52.74.12.88  | Homepage only | 1 visit | LOW INTENT",
        "Visitor 004 | IP: 203.0.113.99 | Pricing + API Docs + Contact Sales | 4 visits | HIGH INTENT",
    ])

    # Defaults
    d_ip,d_pages,d_time,d_visits,d_pricing,d_demo,d_repeat = "","",0,1,False,False,False

    if "Visitor 001" in sample:
        d_ip="104.18.2.161"; d_pages="/pricing, /ai-sales-agent, /case-studies"
        d_time=222; d_visits=3; d_pricing=True; d_demo=True; d_repeat=True
    elif "Visitor 002" in sample:
        d_ip="13.32.99.10"; d_pages="/features, /integrations"
        d_time=120; d_visits=1; d_pricing=False; d_demo=False; d_repeat=False
    elif "Visitor 003" in sample:
        d_ip="52.74.12.88"; d_pages="/home"
        d_time=30; d_visits=1; d_pricing=False; d_demo=False; d_repeat=False
    elif "Visitor 004" in sample:
        d_ip="203.0.113.99"; d_pages="/pricing, /api-docs, /case-studies, /contact-sales"
        d_time=480; d_visits=4; d_pricing=True; d_demo=True; d_repeat=True

    # Visitor signal form - exactly like PDF
    st.markdown('<div class="vbox">', unsafe_allow_html=True)
    st.markdown("**📋 Raw Visitor Signal** *(as your website analytics would capture it)*")

    col1, col2 = st.columns(2)
    with col1:
        ip_input = st.text_input("🌐 Visitor IP Address", value=d_ip, placeholder="e.g. 34.201.xxx.xxx")
        pages_input = st.text_input("📄 Pages Visited (comma separated)", value=d_pages, placeholder="/pricing, /ai-sales-agent, /case-studies")
    with col2:
        time_input = st.number_input("⏱️ Time on Site (seconds)", value=d_time, min_value=0, max_value=7200)
        visits_input = st.number_input("� Visits This Week", value=d_visits, min_value=1, max_value=100)

    col3,col4,col5 = st.columns(3)
    with col3: pricing_check = st.checkbox("✅ Visited /pricing", value=d_pricing)
    with col4: demo_check = st.checkbox("✅ Visited /demo", value=d_demo)
    with col5: repeat_check = st.checkbox("✅ Repeat Visitor", value=d_repeat)
    st.markdown('</div>', unsafe_allow_html=True)

    # Show the exact JSON being sent - like PDF input format
    pages_list = [p.strip() for p in pages_input.split(",") if p.strip()]
    mins = time_input // 60
    secs = time_input % 60

    st.markdown("**🔎 Visitor Signal Being Sent to AI Pipeline:**")
    st.code(f"""Visitor Signal:
  IP Address    : {ip_input or "not set"}
  Pages Visited : {", ".join(pages_list) if pages_list else "none"}
  Time on Site  : {mins}m {secs}s
  Visits Week   : {visits_input}
  Pricing Page  : {"Yes ✓" if pricing_check else "No"}
  Demo Page     : {"Yes ✓" if demo_check else "No"}
  Repeat Visitor: {"Yes ✓" if repeat_check else "No"}""")

    go = st.button("🚀 Run AI Enrichment Pipeline", use_container_width=True)

    if go:
        if not ip_input.strip():
            st.warning("⚠️ Please enter an IP address!")
        else:
            with st.spinner(f"🔍 Step 1: Identifying company from IP {ip_input}... then enriching..."):
                try:
                    payload = {
                        "ip_address": ip_input.strip(),
                        "page_behavior": {
                            "visited_pricing": pricing_check,
                            "visited_demo": demo_check,
                            "repeat_visitor": repeat_check,
                            "dwell_time_seconds": int(time_input),
                            "pages_visited": pages_list
                        }
                    }
                    r = requests.post("http://localhost:8000/enrich", json=payload, timeout=30)
                    r.raise_for_status()
                    data = r.json()["data"]
                    t = r.json()["processing_time_seconds"]
                    st.success(f"✅ Visitor identified as **{data.get('company_name')}** — fully enriched in {t}s!")
                    show_results(data)
                except requests.exceptions.ConnectionError:
                    st.error("❌ API not running! Open new terminal and run: uvicorn api.main:app --reload --port 8000")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ─────────────────────────────────────────────
# MODE 2: COMPANY NAME ONLY
# ─────────────────────────────────────────────
else:
    st.markdown("### 🏢 Company Name Enrichment")
    st.info("💡 Enter any company name to get full sales intelligence profile.")
    st.caption("Try: `Figma` · `HubSpot` · `Postman` · `Zepto` · `Freshworks`")

    company_input = st.text_input("Company Name", placeholder="e.g. Figma")
    go = st.button("🚀 Enrich Company", use_container_width=True)

    if go:
        if not company_input.strip():
            st.warning("⚠️ Please enter a company name!")
        else:
            with st.spinner(f"� Enriching {company_input}..."):
                try:
                    r = requests.post("http://localhost:8000/enrich",
                        json={"company_name": company_input.strip()}, timeout=30)
                    r.raise_for_status()
                    data = r.json()["data"]
                    t = r.json()["processing_time_seconds"]
                    st.success(f"✅ Done in {t}s")
                    show_results(data)
                except requests.exceptions.ConnectionError:
                    st.error("❌ API not running! Open new terminal: uvicorn api.main:app --reload --port 8000")
                except Exception as e:
                    st.error(f"❌ Error: {e}")