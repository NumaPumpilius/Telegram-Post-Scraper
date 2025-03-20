@echo off

echo Installing required packages...
pip install -r requirements.txt
cls

echo -----------------------------------------------------
echo Telegram Post Scraper
echo -----------------------------------------------------
echo Usage:
echo - For single posts: python main.py --link URL
echo - For bulk mode:    python main.py --bulk URL start_id count
echo - Interactive mode: python main.py
echo.
echo Example:
echo python main.py --bulk https://t.me/channelname/ 1000 10
echo.
echo Starting in interactive mode...
echo -----------------------------------------------------
echo.

python main.py