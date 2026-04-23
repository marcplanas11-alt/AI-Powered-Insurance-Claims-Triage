import streamlit as st
import anthropic

st.set_page_config(page_title="AI-Powered Insurance Claims Triage", layout="wide")

st.title("AI-Powered Insurance Claims Triage")

st.write(
    "Paste a claim and policy wording to generate intake, coverage and decision analysis."
)

api_key = st.text_input("Anthropic API Key", type="password")

claim_text = st.text_area("Paste claim text", height=150)
policy_text = st.text_area("Paste policy text", height=150)


def get_client(api_key):
    return anthropic.Anthropic(api_key=api_key)


def intake_agent(client, claim_text):
    prompt = f"""
    You are an insurance claims intake analyst.

    Extract:
    - type of claim
    - cause of loss
    - estimated loss
    - relevant coverage clues

    Claim:
    {claim_text}

    Return structured markdown.
    """

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def policy_agent(client, intake_output, policy_text):
    prompt = f"""
    You are an insurance coverage analyst.

    Based on this claim:

    {intake_output}

    And policy:

    {policy_text}

    Identify:
    - coverage
    - exclusions
    - assessment

    Return structured markdown.
    """

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def decision_agent(client, intake_output, policy_output):
    prompt = f"""
    You are a claims decision agent.

    Based on:

    CLAIM:
    {intake_output}

    POLICY:
    {policy_output}

    Choose:
    - APPROVE
    - ESCALATE
    - REJECT

    Return:
    decision + reason + human review
    """

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


if st.button("Run Claims Triage"):

    if not api_key:
        st.error("Enter API key")
    elif not claim_text or not policy_text:
        st.error("Provide claim and policy text")
    else:
        client = get_client(api_key)

        with st.spinner("Running intake..."):
            intake = intake_agent(client, claim_text)

        with st.spinner("Checking policy..."):
            policy = policy_agent(client, intake, policy_text)

        with st.spinner("Making decision..."):
            decision = decision_agent(client, intake, policy)

        st.success("Done")

        tab1, tab2, tab3 = st.tabs(["Intake", "Policy", "Decision"])

        with tab1:
            st.markdown(intake)

        with tab2:
            st.markdown(policy)

        with tab3:
            st.markdown(decision)