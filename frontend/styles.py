"""
Custom CSS styles for the LocateMeAI frontend application
"""

def get_custom_css():
    """Returns the custom CSS for the application"""
    return """
    <style>
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #00274a 0%, #003d6b 100%) !important;
    }
    
    /* Main content area */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #00274a 0%, #003d6b 100%) !important;
    }
    /* Main content area */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #00274a 0%, #003d6b 100%) !important;
    }
    
    /* Sidebar background if any */
    [data-testid="stSidebar"] {
        background-color: #001e3c !important;
    }
    
    /* Constrain content width to 80% */
    .block-container {
        max-width: 80% !important;
        padding-left: 5% !important;
        padding-right: 5% !important;
    }
    
    /* Header section */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* Style for tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #003d6b !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 5px !important;
        padding: 10px 20px !important;
        border: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #eefafd !important;
        color: black !important;
        border-bottom: 3px solid #eefafd !important;
    }
    
    /* Style for tab content/body */
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #eefafd !important;
        border: 2px solid #1976d2 !important;
        border-radius: 8px !important;
        padding: 20px !important;
        color: black !important;
    }
    
    /* Text elements inside tab panel */
    .stTabs [data-baseweb="tab-panel"] h1,
    .stTabs [data-baseweb="tab-panel"] h2,
    .stTabs [data-baseweb="tab-panel"] h3,
    .stTabs [data-baseweb="tab-panel"] h4,
    .stTabs [data-baseweb="tab-panel"] h5,
    .stTabs [data-baseweb="tab-panel"] h6,
    .stTabs [data-baseweb="tab-panel"] p,
    .stTabs [data-baseweb="tab-panel"] span,
    .stTabs [data-baseweb="tab-panel"] label,
    .stTabs [data-baseweb="tab-panel"] .stMarkdown,
    .stTabs [data-baseweb="tab-panel"] .stCaption {
        color: black !important;
    }
    
    /* File uploader and audio input inside tab panel - keep white text */
    .stTabs [data-baseweb="tab-panel"] [data-testid="stFileUploader"] label,   
    .stTabs [data-baseweb="tab-panel"] [data-testid="stFileUploader"] span,
    .stTabs [data-baseweb="tab-panel"] [data-testid="stFileUploader"] div,
    .stTabs [data-baseweb="tab-panel"] [data-testid="stAudioInput"] label,
    .stTabs [data-baseweb="tab-panel"] [data-testid="stAudioInput"] span,
    .stTabs [data-baseweb="tab-panel"] [data-testid="stAudioInput"] div {
        color: white !important;
    }    
    
    /* Emotion cache elements with white background */
    .st-emotion-cache-* {
        background-color: white !important;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #1976d2 !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
    }
    
    .stButton > button:hover {
        background-color: #1565c0 !important;
        border: none !important;
    }
    
    /* Text colors */
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    p, span, label, .stMarkdown {
        color: white !important;
    }

    .stTabs [aria-selected="true"] p {
        color: black !important;
    }
    
    .stCaption {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 2px dashed #1976d2 !important;
        border-radius: 8px !important;
        padding: 20px !important;
    }
    
    [data-testid="stFileUploader"] label {
        color: white !important;
    }
    
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] div {
        color: white !important;
    }
    
    /* Audio input (voice recorder) */
    [data-testid="stAudioInput"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 2px solid #1976d2 !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    
    [data-testid="stAudioInput"] label,
    [data-testid="stAudioInput"] p,
    [data-testid="stAudioInput"] span,
    [data-testid="stAudioInput"] div {
        color: white !important;
    }
    
    /* Text input and text area */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid #1976d2 !important;
        border-radius: 5px !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid #1976d2 !important;
    }
    
    /* Radio buttons and checkboxes */
    .stRadio > label, .stCheckbox > label {
        color: white !important;
    }
    
    /* Success/Info/Warning/Error messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 5px !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border-radius: 5px !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: white !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    </style>
    """