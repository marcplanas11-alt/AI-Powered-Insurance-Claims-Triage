import streamlit as st
import anthropic
from pypdf import PdfReader

st.set_page_config(page_title="AI-Powered Insurance Claims Triage", layout="wide")

st.title("AI-Powered Insurance Claims Triage")
st.write(
    "Upload or paste a claim and policy wording to generate an intake, "
    "coverage, and decision review."
)

api_key = st.text_input("Anthropic API Key", type="password")
st.caption("Your API key is only used to run the analysis in the current session.")

use_sample = st.checkbox("Use sample claim and sample policy")
claim_file = st.file_uploader("Upload claim PDF or TXT", type=["pdf", "txt"], key="claim")
policy_file = st.file_uploader("Upload policy PDF or TXT", type=["pdf", "txt"], key="policy")

claim_text_input = st.text_area("Or paste claim text", height=140)
policy_text_input = st.text_area("Or paste policy text", height=180)


def get_client(api_key: str):
    return anthropic.Anthropic(api_key=api_key)


def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text)


def extract_text_from_txt(uploaded_file):
    return uploaded_file.read().decode("utf-8")


def load_input(uploaded_file, manual_text: str, sample_text: str):
    if use_sample:
        return sample_text
    if manual_text and manual_text.strip():
        return manual_text.strip()
    if uploaded_file is None:
        return ""
    if uploaded_file.name.lower().endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    if uploaded_file.name.lower().endswith(".txt"):
        return extract_text_from_txt(uploaded_file)
    return ""


def intake_agent(client, claim_text):
    prompt = f"""
    You are an insurance claims intake analyst.

    Extract:
    - type of claim
    - cause of loss
    - estimated loss
    - relevant policy coverage clues

    Claim:
    {claim_text}

    Return structured markdown with:
    1. Claim Summary
    2. Cause of Loss Analysis
    3. Policy Coverage Clues
    4. Risk Flag
    5. Recommended Next Steps
    """

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=700,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def policy_agent(client, intake_output, policy_text):
    prompt = f"""
    You are an insurance coverage analyst.

    Based on this claim intake summary:

    {intake_output}

    And this policy wording:

    {policy_text}

    Assess:
    - relevant covered sections
    - relevant exclusions
    - whether coverage appears plausible, doubtful, or excluded
    - reasons for that assessment

    Return structured markdown with:
    1. Covered Sections
    2. Exclusions
    3. Coverage Assessment
    4. Reasons
    """

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=700,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def decision_agent(client, intake_output, policy_review):
    prompt = f"""
    You are an insurance claims triage decision agent.

    Based on the following claim intake summary:

    {intake_output}

    And the following coverage analysis:

    {policy_review}

    Choose only ONE decision:
    - APPROVE
    - ESCALATE
    - REJECT

    Use these rules:
    - APPROVE = coverage appears clear and no major ambiguity exists
    - ESCALATE = ambiguity, dispute risk, missing evidence, or human judgement needed
    - REJECT = exclusion clearly applies and grounds are strong

    Return structured markdown with:
    1. Decision
    2. Confidence Level
    3. Reason
    4. Human Review Required (Yes/No)
    5. Next Operational Step
    """

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=700,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


SAMPLE_CLAIM = """
Policyholder reports water damage in kitchen due to pipe burst.
Estimated loss: €4,500.
Policy includes water damage but excludes wear and tear.
Incident caused by old pipe corrosion.
"""

SAMPLE_POLICY = """
Home insurance policy.

Covered:
- Water damage caused by sudden and accidental escape of water
- Damage to insured kitchen fixtures and surfaces

Excluded:
- Wear and tear
- Gradual deterioration
- Corrosion
- Damage caused by poor maintenance.
"""

if st.button("Run Claims Triage", type="primary"):
    if not api_key:
        st.error("Please enter your Anthropic API key.")
    else:
        claim_text = load_input(claim_file, claim_text_input, SAMPLE_CLAIM)
        policy_text = load_input(policy_file, policy_text_input, SAMPLE_POLICY)

        if not claim_text.strip():
            st.error("Please upload or paste claim text, or use the sample claim.")
        elif not policy_text.strip():
            st.error("Please upload or paste policy wording, or use the sample policy.")
        else:
            try:
                client = get_client(api_key)

                with st.spinner("Running intake analysis..."):
                    intake_output = intake_agent(client, claim_text)

                with st.spinner("Running policy coverage review..."):
                    policy_output = policy_agent(client, intake_output, policy_text)

                with st.spinner("Generating triage decision..."):
                    decision_output = decision_agent(client, intake_output, policy_output)

                st.success("Claims triage completed.")

                tab1, tab2, tab3 = st.tabs(["Intake", "Policy Review", "Decision"])

                with tab1:
                    st.markdown(intake_output)

                with tab2:
                    st.markdown(policy_output)

                with tab3:
                    st.markdown(decision_output)

                with st.expander("Claim text preview"):
                    st.text(claim_text[:4000])

                with st.expander("Policy text preview"):
                    st.text(policy_text[:4000])

            except Exception as e:
                st.error(f"Error: {e}")

st.info(
    "This tool is a proof of concept designed to support human review. "
    "It does not replace claims, legal, compliance, or underwriting judgement."
)
