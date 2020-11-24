ECHO OFF
ECHO Running Scraper...
venv\Scripts\python.exe driver.py --DATABASE "test.db" --DEBUG_INFO --TOTAL_CATEGORIES 6
PAUSE