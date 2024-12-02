import folium
from streamlit_folium import st_folium
import os
import streamlit as st
import requests
from dotenv import load_dotenv
from fpdf import FPDF  # Added this for PDF generation

# Load environment variables from the .env file
load_dotenv("C:/Users/Rrish/OneDrive/Desktop/JamAI Base/Credentials.env")
API_KEY = os.getenv("API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")
JamAI_TABLE_ID = "Travel_Advisor"  
BASE_URL = "https://api.jamaibase.com"

token = API_KEY  # Use the API key from the environment variable

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": f"Bearer {token}",
    "X-PROJECT-ID": PROJECT_ID
}

# Inject custom CSS for styling
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&display=swap');

        body {
            background-color: #121212;
            color: #ffffff;
            font-family: 'Montserrat', sans-serif;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff;
            text-align: center;
            font-weight: 600;
        }
        .stTextInput label, .stTextArea label {
            color: #66d9ef;
            font-size: 16px;
            font-weight: bold;
        }
        .stSidebar {
            background-color: #1f1f1f;
            padding: 20px;
        }
        .stButton button, .stDownloadButton button {
            background-color: #66d9ef;
            color: #000000;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            padding: 8px 16px;
        }
        .stButton button:hover, .stDownloadButton button:hover {
            background-color: #33ccff;
            color: #ffffff;
        }
        textarea, input {
            background-color: #1e1e1e;
            color: #66d9ef;
            border: 1px solid #66d9ef;
            border-radius: 8px;
        }
        .stTextInput div {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* Custom Styles for the Output */
        .output-section {
            padding: 15px;
            border-radius: 8px;
            background-color: #1e1e1e;
            margin-bottom: 20px;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
        }
        .output-header {
            font-size: 20px;
            color: #66d9ef;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .output-content {
            font-size: 16px;
            color: #ffffff;
            line-height: 1.5;
        }
        .output-list {
            margin-top: 10px;
            padding-left: 20px;
        }
        .output-list li {
            list-style-type: none;
            font-size: 16px;
            margin-bottom: 5px;
        }

        /* Position the GitHub icon at the bottom-left of the sidebar */
        .github-icon {
            position: absolute;  
            top: 300px;  /* Distance from the bottom */  
            left: 100px;    /* Distance from the left */
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to send travel request and get advice from JamAI API
def generate_travel_advice(home_country, desired_country, activity):
    """Send user inputs to the table and fetch travel advice."""
    with st.spinner("✨ Generating your travel advice... Please wait."):

        # Prepare the data payload
        url_add = f"{BASE_URL}/api/v1/gen_tables/action/rows/add"
        payload = {
            "data": [
                {
                    "Home Country": home_country,
                    "Desired Country": desired_country,
                    "Preferred Activity": activity
                }
            ],
            "table_id": JamAI_TABLE_ID,
            "stream": False,
        }

        # Send data to JamAI API
        response = requests.post(url_add, json=payload, headers=headers)
        if response.status_code == 200:
            st.success("Your travel details were successfully added to the table!")
            return True
        else:
            st.error(f"Failed to add travel details. Error {response.status_code}: {response.text}")
            return False

# Function to fetch the latest travel advice
def fetch_travel_advice(home_country, desired_country, activity):
    """Fetch the generated travel advice based on the user's input."""
    url = f"{BASE_URL}/api/v1/gen_tables/action/{JamAI_TABLE_ID}/rows"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        rows = response.json().get("items", [])
        if rows:
            for row in reversed(rows):  # Check from the most recent entry
                if (
                    row.get("Home Country", {}).get("value") == home_country
                    and row.get("Desired Country", {}).get("value") == desired_country
                    and row.get("Preferred Activity", {}).get("value") == activity
                ):
                    # Retrieve the specific output fields
                    flight_duration = row.get("Flight Duration", {}).get("value")
                    currency = row.get("Currency", {}).get("value")
                    activity_locations = row.get("Activity Locations", {}).get("value")
                    
                    # Return a dictionary of the required details
                    if flight_duration and currency and activity_locations:
                        return {
                            "flight_duration": flight_duration,
                            "currency": currency,
                            "activity_locations": activity_locations
                        }
                    else:
                        st.warning("Some travel details are missing. Please try again.")
                        return None
            st.warning("No matching travel advice found for the given inputs.")
            return None
        else:
            st.warning("No data found in the table.")
            return None
    else:
        st.error(
            f"Failed to fetch the travel advice. Error {response.status_code}: {response.text}"
        )
        return None

# Function to display the travel advice in Streamlit
def display_travel_advice(advice_details):
    """Display the travel advice details in the Streamlit app.""" 
    if advice_details:
        # Display flight duration
        st.markdown(f"<div class='output-section'>"
                    f"<div class='output-header'>✈️ Flight Duration:</div>"
                    f"<div class='output-content'>{advice_details['flight_duration']}</div>"
                    f"</div>", unsafe_allow_html=True)

        # Display currency
        st.markdown(f"<div class='output-section'>"
                    f"<div class='output-header'>💰 Currency:</div>"
                    f"<div class='output-content'>{advice_details['currency']}</div>"
                    f"</div>", unsafe_allow_html=True)

        # Display activity locations
        st.markdown(f"<div class='output-section'>"
                    f"<div class='output-header'>🏖️ Activity Locations:</div>"
                    f"<div class='output-content'>{advice_details['activity_locations']}</div>"
                    f"</div>", unsafe_allow_html=True)
    else:
        st.warning("No travel advice available.")


# Function to generate PDF from the travel advice details
def generate_pdf(advice_details):
    # Create a PDF object
    pdf = FPDF()

    # Add a page to the PDF
    pdf.add_page()

    # Add regular font to FPDF (using built-in font)
    pdf.set_font('Arial', '', 12)  # Simple font, 12 size for readability

    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, txt="Travel Advice Report", ln=True, align="C")
    pdf.ln(10)

    # Travel Details Section
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(200, 10, txt="Your Travel Details:", ln=True)
    pdf.set_font('Arial', '', 12)

    pdf.multi_cell(0, 10, txt=(f"Flight Duration: {advice_details['flight_duration']}\n\n"
                              f"Currency: {advice_details['currency']}\n\n"
                              f"Activity Locations: {advice_details['activity_locations']}\n"))

    # Specify the output file path
    output_file = "travel_advice_report_simple.pdf"
    
    # Save the generated PDF
    pdf.output(output_file)

    print("PDF generated successfully.")

    return output_file


# Header
st.title("✈️ Travel Advisor with JamAI Base")
st.markdown("Powered by JamAI Base and ELL Meta Llama 3.1 (8B)")

# Sidebar content
with st.sidebar:
    st.subheader("✨ Enter your Travel Details")

    home_country = st.text_input("🌍 Home Country", placeholder="Enter your home country")
    desired_country = st.text_input("🌎 Desired Country", placeholder="Enter your desired destination")
    activity = st.text_input("🏖️ Preferred Activity", placeholder="Enter your preferred activity")

    submit_button = st.button(label="🥳 Get Travel Advice")

 # GitHub link with official icon (using markdown and custom class for positioning)
    st.markdown(
        """
        <div class="github-icon">
            <a href="https://github.com/RRISHI23/Travel_Advisor/tree/main/JamAI%20Base" target="_blank">
                <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="50" height="50">
            </a>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Main content area
if not submit_button:
    # Folium Map for Location Search (only show before generating travel advice)
    st.subheader("📍 Locate Your Desired Destination")
    map_center = [4.2105, 101.9758]  # Default coordinates for Malaysia (can be adjusted)
    folium_map = folium.Map(location=map_center, zoom_start=5)

    # Allow the user to click and get the latitude and longitude of the location
    folium.Marker([4.2105, 101.9758], popup="Malaysia").add_to(folium_map)

    # Display the map with Folium in Streamlit
    map = st_folium(folium_map, width=725) 

    # Get the latitude and longitude from the user interaction (if available)
    if map and 'last_click' in map:
        lat = map['last_click']['lat']
        lon = map['last_click']['lon']
        st.write(f"Latitude: {lat}, Longitude: {lon}")
    else:
        lat, lon = None, None

# Button to generate travel advice and provide PDF download link
if submit_button:
    if home_country and desired_country and activity:
        success = generate_travel_advice(home_country, desired_country, activity)
        if success:
            travel_advice = fetch_travel_advice(home_country, desired_country, activity)
            if travel_advice:
                display_travel_advice(travel_advice)
                pdf_file = generate_pdf(travel_advice)

                # Make PDF downloadable
                with open(pdf_file, "rb") as file:
                    st.download_button(
                        label="Download PDF Report",
                        data=file,
                        file_name="Travel_Advice_Report.pdf",
                        mime="application/pdf",
                    )
            else:
                st.warning("No travel advice found.")
        else:
            st.warning("Failed to generate travel advice.")
    else:
        st.warning("Please fill in all the required fields.")
