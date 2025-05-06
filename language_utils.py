"""
Language utilities for managing translations and language selection.
"""
import streamlit as st
from config.translations import translations

def initialize_language():
    """
    Initialize the language setting in the session state if not already set.
    Default language is English.
    """
    if 'language' not in st.session_state:
        st.session_state.language = 'en'

def get_language():
    """
    Get the current language code from session state.
    
    Returns:
        str: Current language code ('en' or 'es_mx')
    """
    initialize_language()
    return st.session_state.language

def set_language(language_code):
    """
    Set the language in session state.
    
    Args:
        language_code (str): Language code to set ('en' or 'es_mx')
    """
    if language_code in translations:
        st.session_state.language = language_code

def get_text(key):
    """
    Get the translated text for the current language.
    
    Args:
        key (str): The key to look up in the translation dictionary
        
    Returns:
        str: Translated text for the current language, or the key itself if translation not found
    """
    lang = get_language()
    
    # Get the translation dictionary for the current language
    translation_dict = translations.get(lang, translations['en'])
    
    # Return the translated text or the key itself if not found
    return translation_dict.get(key, key)

def language_selector():
    """
    Display a language selector in the sidebar and handle language changes.
    
    Returns:
        str: Currently selected language code
    """
    # Get current language
    current_lang = get_language()
    
    # Create the language selector
    lang_options = {
        'en': get_text('english'),
        'es_mx': get_text('spanish')
    }
    
    selected_lang = st.sidebar.selectbox(
        get_text('language_selector'),
        options=list(lang_options.keys()),
        format_func=lambda x: lang_options[x],
        index=list(lang_options.keys()).index(current_lang)
    )
    
    # Update language if changed
    if selected_lang != current_lang:
        set_language(selected_lang)
        st.rerun()
    
    return current_lang