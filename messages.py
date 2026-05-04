# messages.py

CMD_ADD_EXAMPLE = "/add BTC 80000 78000 600"
CMD_UPDATE_EXAMPLE = "/update BTC 80000 78000 600"
CMD_PRICE_EXAMPLE = "/price <symbol> [amount]\n\n"
"Examples:\n"
"/price BTC\n"
"/price ETH 1000\n\n"
"• Shows current price\n"
"• Optionally estimates swap cost if amount is provided"

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
HELP_VOLATILE = "/volatile [1h|6h|24h]\n\nExamples:\n/volatile\n/volatile 1h"
