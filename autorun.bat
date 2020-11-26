ECHO OFF
ECHO Running Scraper...
venv\Scripts\python.exe driver.py --DATABASE "test.db" --MAX_CATEGORY_WORKERS 4 --TOTAL_CATEGORIES 6 --DEBUG_INFO > autorunlog.txt
PAUSE