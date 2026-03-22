import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "8566606318:AAF8IRAwUxct4WvO2zHWSkWShoBQtg9NNrY")
CONTRACT  = "0x28b5cc805D90213D2699CC3B00e28e3f0fbeCA8e"
WEBSITE   = "https://winnowin-game.pages.dev"
EXPLORER  = "https://monad.socialscan.io"
RPC_URL   = "https://rpc.monad.xyz"
CHAIN_ID  = 143
PRICE_MON = 100

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def rpc_call(method, params):
    try:
        r = requests.post(RPC_URL, json={"jsonrpc":"2.0","id":1,"method":method,"params":params}, timeout=8)
        return r.json().get("result")
    except:
        return None

def decode_uint(h):
    return int(h, 16) if h and h != "0x" else 0

def get_supply():
    return decode_uint(rpc_call("eth_call", [{"to":CONTRACT,"data":"0x18160ddd"},"latest"])) / 1e18

def get_enabled():
    return decode_uint(rpc_call("eth_call", [{"to":CONTRACT,"data":"0x4c8d4f24"},"latest"])) != 0

def main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💶 Open EUROSPACE App", web_app=WebAppInfo(url=WEBSITE))],
        [InlineKeyboardButton("📊 Live Stats", callback_data="stats"), InlineKeyboardButton("💰 Price", callback_data="price")],
        [InlineKeyboardButton("📜 Contract", callback_data="contract"), InlineKeyboardButton("🚀 How To Buy", callback_data="howtobuy")],
        [InlineKeyboardButton("🔗 Explorer", url=f"{EXPLORER}/address/{CONTRACT}"), InlineKeyboardButton("❓ Help", callback_data="help")],
        [InlineKeyboardButton("🌐 Website", url=WEBSITE)],
    ])

def back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("💶 Buy Now", url=WEBSITE), InlineKeyboardButton("⬅️ Back", callback_data="back")]])

WELCOME = """
💶 *EURO COIN — Monad Presale*
━━━━━━━━━━━━━━━━━━━━

The Euro-pegged token on *Monad Blockchain*!

💰 Price: *100 MON = 1 EURO*
⛓ Network: Monad Mainnet · Chain ID 143
📋 Standard: ERC-20 · Decimals: 18

🌐 winnowin-game.pages.dev
━━━━━━━━━━━━━━━━━━━━
Choose an option below 👇
"""

HOW_TO_BUY = """
🚀 *HOW TO BUY EURO COIN*
━━━━━━━━━━━━━━━━━━━━

*Step 1* — Connect Wallet
MetaMask, WalletConnect, Trust Wallet or Rabby

*Step 2* — Switch to Monad
Chain ID: 143 added automatically!

*Step 3* — Enter MON Amount
100 MON = 1 EURO COIN

*Step 4* — Buy and Receive
EURO COIN sent instantly to your wallet!
━━━━━━━━━━━━━━━━━━━━
"""

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, parse_mode="Markdown", reply_markup=main_kb())

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ *Euro Coin Help*\n\n🌐 winnowin-game.pages.dev\n\n"
        "/start — Main menu\n/buy — Buy Euro Coin\n/stats — Live stats\n"
        "/price — Current price\n/contract — Contract info\n/help — This menu",
        parse_mode="Markdown", reply_markup=main_kb()
    )

async def buy_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"💶 *Buy Euro Coin*\n\n💰 Price: *{PRICE_MON} MON = 1 EURO*\n\n🌐 winnowin-game.pages.dev",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💶 Buy Now", url=WEBSITE)]])
    )

async def stats_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ Fetching live stats...")
    supply = get_supply()
    enabled = get_enabled()
    await msg.edit_text(
        f"📊 *LIVE STATS*\n━━━━━━━━━━━━━━━━━━━━\n"
        f"🪙 Total Supply: `{supply:,.2f} EURO`\n"
        f"💰 Price: `{PRICE_MON} MON per EURO`\n"
        f"🟢 Presale: `{'OPEN' if enabled else 'CLOSED'}`\n"
        f"⛓ Monad #{CHAIN_ID}\n━━━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown", reply_markup=main_kb()
    )

async def price_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"💰 *EURO COIN PRICE*\n━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ Rate: `{PRICE_MON} MON = 1 EURO`\n\n"
        f"▸ 100 MON → 1 EURO\n▸ 500 MON → 5 EURO\n"
        f"▸ 1000 MON → 10 EURO\n▸ 5000 MON → 50 EURO\n━━━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown", reply_markup=back_kb()
    )

async def contract_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📜 *CONTRACT INFO*\n━━━━━━━━━━━━━━━━━━━━\n"
        f"💶 *EURO Token ERC-20*\n`{CONTRACT}`\n\n"
        f"🔗 Monad · Chain ID: {CHAIN_ID}\n━━━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔗 Explorer", url=f"{EXPLORER}/address/{CONTRACT}"),
            InlineKeyboardButton("⬅️ Back", callback_data="back")
        ]])
    )

async def button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "back":
        await q.edit_message_text(WELCOME, parse_mode="Markdown", reply_markup=main_kb())
    elif q.data == "stats":
        supply = get_supply()
        enabled = get_enabled()
        await q.edit_message_text(
            f"📊 *LIVE STATS*\n━━━━━━━━━━━━━━━━━━━━\n"
            f"🪙 Total Supply: `{supply:,.2f} EURO`\n"
            f"💰 Price: `{PRICE_MON} MON per EURO`\n"
            f"🟢 Presale: `{'OPEN' if enabled else 'CLOSED'}`\n"
            f"⛓ Monad #{CHAIN_ID}\n━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown", reply_markup=main_kb()
        )
    elif q.data == "price":
        await q.edit_message_text(
            f"💰 *EURO COIN PRICE*\n━━━━━━━━━━━━━━━━━━━━\n"
            f"🏷️ Rate: `{PRICE_MON} MON = 1 EURO`\n\n"
            f"▸ 100 MON → 1 EURO\n▸ 500 MON → 5 EURO\n"
            f"▸ 1000 MON → 10 EURO\n▸ 5000 MON → 50 EURO\n━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown", reply_markup=back_kb()
        )
    elif q.data == "howtobuy":
        await q.edit_message_text(HOW_TO_BUY, parse_mode="Markdown", reply_markup=back_kb())
    elif q.data == "contract":
        await q.edit_message_text(
            f"📜 *CONTRACT*\n━━━━━━━━━━━━━━━━━━━━\n`{CONTRACT}`\nMonad #{CHAIN_ID}\n━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔗 Explorer", url=f"{EXPLORER}/address/{CONTRACT}"),
                InlineKeyboardButton("⬅️ Back", callback_data="back")
            ]])
        )
    elif q.data == "help":
        await q.edit_message_text(
            "❓ *Help*\n\n🌐 winnowin-game.pages.dev\n\n/start /buy /stats /price /contract /help",
            parse_mode="Markdown", reply_markup=main_kb()
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",    start))
    app.add_handler(CommandHandler("help",     help_cmd))
    app.add_handler(CommandHandler("buy",      buy_cmd))
    app.add_handler(CommandHandler("stats",    stats_cmd))
    app.add_handler(CommandHandler("price",    price_cmd))
    app.add_handler(CommandHandler("contract", contract_cmd))
    app.add_handler(CallbackQueryHandler(button))
    log.info("Euro Coin Bot started - winnowin-game.pages.dev")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
