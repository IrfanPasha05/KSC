import os, requests
API_VERSION=os.getenv("WHATSAPP_API_VERSION","v23.0")
PHONE_NUMBER_ID=os.getenv("WHATSAPP_PHONE_NUMBER_ID","")
ACCESS_TOKEN=os.getenv("WHATSAPP_ACCESS_TOKEN","")
ADMIN_NUMBER=os.getenv("WHATSAPP_ADMIN_NUMBER","")
ENABLED=os.getenv("WHATSAPP_ENABLED","false").lower()=="true"
def send_order_notification(event):
    if not ENABLED: return {"status":"skipped","reason":"WHATSAPP_ENABLED=false"}
    if not PHONE_NUMBER_ID or not ACCESS_TOKEN or not ADMIN_NUMBER: return {"status":"skipped","reason":"WhatsApp credentials not configured"}
    order=event["order"]
    body=(f"🐔 New KSC Order\nOrder: #{order['id']}\nCustomer: {order['name']}\nPhone: {order['phone']}\nCut: {order['cut']}\nQuantity: {order.get('quantity') or '-'}\nNotes: {order.get('notes') or '-'}")
    url=f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"
    r=requests.post(url,headers={"Authorization":f"Bearer {ACCESS_TOKEN}","Content-Type":"application/json"},json={"messaging_product":"whatsapp","to":ADMIN_NUMBER,"type":"text","text":{"body":body}},timeout=20)
    r.raise_for_status()
    return {"status":"sent","message_id":r.json().get("messages",[{}])[0].get("id")}
