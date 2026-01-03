from data.worldbank import fetch_and_save_series

fetch_and_save_series("Gold")
fetch_and_save_series("Silver")

print("🎉 Historical daily CSVs created successfully.")
