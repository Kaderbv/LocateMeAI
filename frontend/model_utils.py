"""Utility functions for model management with caching"""
import streamlit as st
import requests
from config import BACKEND_URL

BACKEND_ACTIVE_MODEL_URL = f"{BACKEND_URL}/active-model"

def get_active_model_cached(force_refresh=False):
    """
    Get active model with session state caching.
    
    Args:
        force_refresh: If True, bypass cache and fetch fresh data
        
    Returns:
        dict: Active model info or None if error
    """
    # Initialize cache in session state
    if 'active_model_cache' not in st.session_state:
        st.session_state.active_model_cache = None
    
    # Return cached value if available and not forcing refresh
    if not force_refresh and st.session_state.active_model_cache is not None:
        return st.session_state.active_model_cache
    
    # Fetch from backend
    try:
        response = requests.get(BACKEND_ACTIVE_MODEL_URL, timeout=5)
        if response.status_code == 200:
            st.session_state.active_model_cache = response.json()
            return st.session_state.active_model_cache
    except Exception as e:
        st.session_state.active_model_cache = None
    
    return None

def invalidate_model_cache():
    """Invalidate the cached model data (call after model switch)"""
    if 'active_model_cache' in st.session_state:
        st.session_state.active_model_cache = None

def display_active_model_info():
    """Display active model information banner"""
    model_info = get_active_model_cached()
    
    if model_info:
        active_model = model_info.get('active_model', 'yolov8n.pt')
        is_default = model_info.get('is_default', True)
        
        model_display = active_model.split('/')[-1] if '/' in active_model else active_model
        
        if is_default:
            st.info(f"🤖 **Detection Model:** Default ({model_display})")
        else:
            st.success(f"🤖 **Detection Model:** Custom Fine-tuned ({model_display})")
