"""
Custom CSS styles for the LocateMeAI frontend application
"""

def get_custom_css():
    """Returns the custom CSS for the application"""
    return """
    <style>
    .stApp {
        background-color: #00274a !important;
    }
    /* Constrain content width to 80% */
    .block-container {
        max-width: 80% !important;
        padding-left: 5% !important;
        padding-right: 5% !important;
    }
    /* Style for tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #5a9bd5 !important;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1976d2 !important;
        border-bottom: 3px solid #64b5f6 !important;
    }
    /* Style for tab content/body */
    .stTabs [data-baseweb="tab-panel"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 2px solid #1976d2 !important;
        border-radius: 8px !important;
        padding: 20px !important;
        margin-top: 10px !important;
    }
    .st-c1 {
            background-color: #1976d2d9 !important;
    }
    /* White text for title and caption */
    h1 {
        color: white !important;
    }
    h2, h3 {
        color: white !important;
    }
    .stCaption {
        color: white !important;
    }
    p {
        color: white !important;
    }
    </style>
    """
