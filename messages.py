# messages.py

CMD_ADD_EXAMPLE = "/add BTC 80000 78000 600"
CMD_UPDATE_EXAMPLE = "/update BTC 80000 78000 600"
CMD_PRICE_EXAMPLE = "/price BTC"

HELP_ADD = f"""
➕ Add alert:
Usage:
{CMD_ADD_EXAMPLE}

Format:
<symbol> <take-profit> <stop-loss> <interval_seconds>
"""

HELP_PRICE = f"""
📊 Check price:
Usage:
{CMD_PRICE_EXAMPLE}
"""

