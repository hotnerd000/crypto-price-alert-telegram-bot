# messages.py

CMD_ADD_EXAMPLE = "/add BTC 70000 63000 60"
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