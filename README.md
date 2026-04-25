# FIFA Resale Scraper

## Overview
This project is a Proof of Concept (POC) for scraping FIFA resale ticket data, processing it, and preparing it for insertion into Supabase.

### The solution covers:
- Match-level data extraction
- Layer 1 availability scraping
- Seat-level (UI/cart-based) extraction
- JSON transformation
- CSV generation for Supabase upload

## Project Objective
The objective is to extract FIFA resale data and structure it according to the client-required Supabase schema.

### Final required structure:
| Field | Description |
| --- | --- |
| id | (auto-generated) |
| created_at | timestamp |
| license_hash | text |
| match_code | text |
| home | text |
| away | text |
| performance_id | text |
| seat_count | integer |
| seats | JSON array |

Each seat object contains:
- seatId
- block
- row
- seat
- category
- price
- usd
- resaleMovementId
- exclusive

## Repository Structure
- main.py → Captures availability API from FIFA site
- extract_data.py → Cleans and structures final JSON (created in latest work)
- availability_output.json → Raw API response
- layer1_clean.json → Cleaned Layer 1 data
- Output_with_seat_data.json → Seat-level extracted data
- all_final_matches.json → Final combined JSON
- all_matches.csv → CSV ready for Supabase
- requirements.txt → Dependencies
- .env → Environment variables.

## How the Project Works:
1. Open FIFA resale website.
2. Capture availability API using browser session.
3. Extract match-level + seat-level data.
4. Clean JSON into final structure.
5. Convert JSON into CSV.
6. Upload into Supabase.

## Setup Instructions:
### 1. Install dependencies:
running in terminal: 

```
pip install -r requirements.txt
```
### 2. Open Chrome with Debug Mode (IMPORTANT):
running this command in CMD:
windows:
```
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrome_profile""
```
to specify full path if needed:
```
c"\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome_profile"
```
### 3. Open FIFA Website:

after Chrome opens,
go to FIFA resale ticket page,
and open any match page (seat selection screen).
and keep the page open.

### 4. Run Scraper:
running:
```
python main.py"
```
to connect to Chrome session, capture availability API, and save raw data.

### 5. Process and Clean Data:
running:
```
python extract_data.py
```
to convert raw JSON into final structured format and prepare match-level + seat-level data.
### 6. Convert JSON to CSV (if separate script):
running:
```
python convert_to_csv.py
```
to generate `all_matches.csv`.


CSV Upload Steps
- Open Supabase project
- Go to Table Editor
- Select scan_data table
- Click "Import CSV"
- Upload all_matches.csv

Notes / Limitations
- Seat-level data is currently extracted from visible UI (cart/selection)
- Full seat-level details (seatId, resaleMovementId) require deeper API integration
- Some matches may not show data due to no ticket availability
- Refresh automation is not yet implemented
- 


Final Summary

This project demonstrates a complete pipeline:

Scraping FIFA resale data
Cleaning and structuring data
Converting to CSV
Uploading to Supabase

