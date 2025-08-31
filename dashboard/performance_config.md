# Dashboard Performance Optimization Configuration

# Streamlit Configuration
# Add this to .streamlit/config.toml for better performance

[server]
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 50

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[client]
caching = true
displayEnabled = true

# Performance tips:
# 1. Use st.cache_data for expensive computations
# 2. Set appropriate TTL values based on data update frequency
# 3. Use use_container_width=True for responsive layouts
# 4. Implement lazy loading for non-critical features
# 5. Use ThreadPoolExecutor for concurrent API calls
# 6. Minimize chart re-rendering with unique keys
# 7. Use session state for user preferences
# 8. Implement progressive disclosure (tabs, expanders)
