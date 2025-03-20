# Telegram Post Scraper - Development Guide

## Commands
- Run: `python main.py`
- CLI usage: `python main.py -l https://t.me/somegroup/ID` or `python main.py --link https://t.me/somegroup/ID`
- Install dependencies: `pip install -r requirements.txt`
- Testing: No formal testing framework present

## Code Style Guidelines
- **Imports**: Standard library first, then third-party packages
- **Formatting**: 4-space indentation, use match-case statements for control flow
- **Classes**: Use CamelCase for class names (e.g., `TeleScraper`)
- **Methods**: Use snake_case for methods and functions (e.g., `html_to_text`)
- **Error handling**: Use try/except blocks with specific exceptions (see `run` method)
- **String formatting**: Use f-strings for string interpolation
- **Documentation**: Add comments for complex functionality
- **File operations**: Always use proper encoding (UTF-8) and file path handling
- **User feedback**: Provide clear console feedback for operations