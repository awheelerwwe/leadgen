import streamlit as st
import requests
import pandas as pd
import time
import io
import streamlit as st

API_KEY = st.secrets["SERPAPI_KEY"]


def serpapi_search(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": API_KEY
    }
    response = requests.get("https://serpapi.com/search", params=params)
    return response.json()

def extract_first_url(data, site_filter=None):
    for result in data.get("organic_results", []):
        url = result.get("link", "")
        if site_filter:
            if site_filter in url.lower():
                return url
        else:
            return url
    return "Not Found"

def get_company_links(company_data):
    results = []
    for name, domain in company_data:
        with st.spinner(f"Searching for {name} ({domain})..."):
            website = f"https://{domain}"

            search_query = f"{name} site:linkedin.com"
            data_li = serpapi_search(search_query)
            linkedin = extract_first_url(data_li, site_filter="linkedin.com")

            results.append({
                "Company": name,
                "Website": website,
                "LinkedIn": linkedin
            })

            time.sleep(1.5)  # Avoid hitting rate limits
    return results

# Streamlit App UI
st.title("🔍 LinkedIn Finder by Company & Domain")

st.write("Paste a list of companies in this format: `Company Name,domain.com` (one per line):")

company_input = st.text_area("Company Data", height=250, placeholder="e.g.\nOpenAI,openai.com\nStripe,stripe.com")

if st.button("Find LinkedIn Pages"):
    lines = [line.strip() for line in company_input.splitlines() if line.strip()]
    company_data = []
    for line in lines:
        parts = line.split(",")
        if len(parts) == 2:
            company_data.append((parts[0].strip(), parts[1].strip()))
        else:
            st.warning(f"Invalid format: '{line}' – please use `Company Name,domain.com` format.")
    
    if not company_data:
        st.warning("Please enter at least one valid company line.")
    else:
        result_data = get_company_links(company_data)
        df = pd.DataFrame(result_data)
        
        st.success("✅ Search complete!")
        st.dataframe(df)

        # Prepare CSV for download
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_buffer.getvalue(),
            file_name="company_links.csv",
            mime="text/csv"
        )
