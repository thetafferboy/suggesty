import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import io

st.title("Google Suggest Keyword Tool")
st.write(
    """
    This tool mines Google suggestions for all alphabetical variations and question formats ("Can", "How", "Where", "Versus", "For") around your keyword.
    """
)

def get_google_suggestions(query, hl='en'):
    url = f"https://www.google.com/complete/search?hl={hl}&output=toolbar&q={query}"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'xml')
    suggestions = [suggestion['data'] for suggestion in soup.find_all('suggestion')]
    return suggestions

def get_extended_suggestions(base_query, hl='en'):
    extended_suggestions = set()
    extended_suggestions.update(get_google_suggestions(base_query, hl))
    for char in 'abcdefghijklmnopqrstuvwxyz':
        extended_suggestions.update(get_google_suggestions(base_query + ' ' + char, hl))
    return list(extended_suggestions)

def capture_suggestions(header, query, all_suggestions):
    suggestions = get_extended_suggestions(query)
    all_suggestions[header] = suggestions

base_query = st.text_input("Enter a search query:")

all_suggestions = {}

if base_query:
    with st.spinner("Fetching suggestions..."):
        capture_suggestions("Google Suggest completions", base_query, all_suggestions)
        capture_suggestions("Can questions", "Can " + base_query, all_suggestions)
        capture_suggestions("How questions", "How " + base_query, all_suggestions)
        capture_suggestions("Where questions", "Where " + base_query, all_suggestions)
        capture_suggestions("Versus", base_query + " versus", all_suggestions)
        capture_suggestions("For", base_query + " for", all_suggestions)

    for header, suggestions in all_suggestions.items():
        st.subheader(header)
        for i, suggestion in enumerate(suggestions, 1):
            st.write(f"{i}. {suggestion}")

    # Data download block
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in all_suggestions.items()]))
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name='google_suggestions.csv',
        mime='text/csv'
    )
