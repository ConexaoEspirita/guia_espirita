import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
import unicodedata
import re

st.set_page_config(page_title="Guia Espírita", page_icon="🕊️", layout="wide")

st.markdown("""
<style>
.stApp { 
    background: linear-gradient(135deg, #EBF4FA 0%, #D4E8F7 100%);
}
.titulo-premium {
    background: linear-gradient(90deg, #0047AB, #1976D2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 4px 12px rgba(0,71,171,0.3);
    font-size: 2.5rem !important;
    font-weight: 800 !important;
}
.card-centro {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 20px;
    border: 1px solid rgba(0,71,171,0.1);
    box-shadow: 0 8px 32px rgba(0,71,171,0.15), 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 16px;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.card-centro:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(0,71,171,0.25);
}
.card-centro::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #0047AB, #5CACE2, #0047AB);
}
.nome-grande { 
    color: #1E3A8A !important;
    font-size: 22px !important; 
    font-weight: 800 !important; 
    line-height: 1.3;
    margin-bottom: 6px;
}
.nome-fantasia { 
    color: #3B82F6 !important;
    font-size: 15px !important; 
    font-weight: 600 !important; 
    font-style: italic; 
    margin-bottom: 10px;
}
.info-texto { 
    color: #374151 !important;
    font-size: 13px !important; 
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
}
div.stLinkButton > a { 
    background: linear-gradient(135deg, #10B981, #059669) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    height: 44px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 16px rgba(16,185,129,0.4) !important;
    transition: all 0.2s ease !important;
}
div.stLinkButton > a:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(16,185,129,0.5) !important;
}
div.stButton > button {
    background: linear-gradient(135deg, #0047AB, #1E40AF) !important;
    color: white !important;
    border-radius: 12px !important;
    height: 48px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 16px rgba(0,71,171,0.4) !important;
}
.conta-pequena { 
    font-size: 12px !important; 
    color: #6B7280 !important; 
    margin-bottom: 12px !important;
    background: rgba(255,255,255,0.7);
    padding: 6px 12px;
    border-radius: 20px;
    display:
