from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import csv
import os

app = Flask(__name__)
user_sessions = {}

# File setup
FEEDBACK_FILE = "feedback.csv"

# Create CSV file with headers if it doesn't exist
if not os.path.exists(FEEDBACK_FILE):
    with open(FEEDBACK_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Phone Number", "Service", "Rating"])

@app.route("/whatsapp", methods=["POST"])
def reply_whatsapp():
    incoming_msg = request.values.get('Body', '').strip().lower()
    user_id = request.values.get('WaId')  # WhatsApp user's number
    resp = MessagingResponse()
    msg = resp.message()

    if user_id not in user_sessions:
        user_sessions[user_id] = {"stage": "start", "service": None}

    if incoming_msg in ['hello', 'hi']:
        user_sessions[user_id] = {"stage": "service_selection", "service": None}
        msg.body(
            "👋 *Hello, welcome to CAROMA LAUNDRY & DRY CLEANERS!*\n"
            "How can we help you today?\n\n"
            "*Our Services:*\n"
            "1. 🧺 Heap Wash, Iron & Fold\n"
            "2. 🧥 Dry Cleaning\n"
            "3. 🧼 Carpet Cleaning\n"
            "4. 🛋️ Sofa Cleaning\n"
            "5. 🛏️ Bed Sheets & Duvets Cleaning\n"
            "6. ✨ Stain Removal Services\n\n"
            "👉 *Reply with the number* of the service you're interested in (e.g., 1, 2...)"
        )
        return str(resp)

    if user_sessions[user_id]['stage'] == "service_selection":
        services = {
            '1': "Heap Wash, Iron & Fold",
            '2': "Dry Cleaning",
            '3': "Carpet Cleaning",
            '4': "Sofa Cleaning",
            '5': "Bed Sheets & Duvets Cleaning",
            '6': "Stain Removal Services"
        }

        if incoming_msg in services:
            selected = services[incoming_msg]
            user_sessions[user_id]['service'] = selected
            user_sessions[user_id]['stage'] = "awaiting_rating"
            msg.body(
                f"✅ You selected: *{selected}*.\n"
                "📞 Please call us at *0739 810 816* or visit us at *VIG omplex, Barnabas, Nakuru* to proceed.\n\n"
                "📩 Before you go, kindly rate our services from 1 to 5 (1 = poor, 5 = excellent)."
            )
        else:
            msg.body("⚠️ Invalid option. Please select a number from 1 to 6.")
        return str(resp)

    if user_sessions[user_id]['stage'] == "awaiting_rating":
        if incoming_msg in ['1', '2', '3', '4', '5']:
            rating = incoming_msg
            service = user_sessions[user_id]['service']

            # Save to CSV
            with open(FEEDBACK_FILE, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([user_id, service, rating])

            user_sessions[user_id]['stage'] = "done"
            msg.body(f"⭐ Thank you for rating us {rating} star(s) for *{service}*!\n🙏 We appreciate your feedback. Feel free to contact us again anytime!")
        else:
            msg.body("⚠️ Please rate us with a number between 1 and 5.")
        return str(resp)

    if 'bye' in incoming_msg:
        msg.body("👋 Goodbye! Thank you for contacting CAROMA. We hope to serve you again!")
        return str(resp)

    msg.body("⚠️ Sorry, I didn’t understand that.\nPlease type *hello* to start again.")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
