import simplematrixbotlib as botlib
import requests
import os
import sys
import logging
import smtplib
import datetime
import time
from aiohttp.client_exceptions import ServerDisconnectedError
from email.mime.text import MIMEText
from dotenv import load_dotenv


load_dotenv()

creds = botlib.Creds(
    os.getenv("BOT_HOMESERVER"),
    os.getenv("BOT_USERNAME"),
    os.getenv("BOT_PASSWORD"),
    session_stored_file="data/session.txt"
)

bot = botlib.Bot(creds)
PREFIX = '!'


logging.basicConfig(level=logging.INFO)


@bot.listener.on_message_event
async def echo(room, message) -> None:
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and match.command("echo"):

        await bot.api.send_text_message(
            room.room_id, " ".join(arg for arg in match.args())
        )


@bot.listener.on_message_event
async def usage(room, message) -> None:
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    response = """usage:
- **!invite** <johndoe@example.org> - sends e-mail with invitation link to given mail address
- **everything else** - prints this help
    """

    if match.is_not_from_this_bot() and not match.prefix() and room.room_id:
        await bot.api.send_markdown_message(room.room_id, response)


@bot.listener.on_message_event
async def invite(room, message) -> None:
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and match.command("invite"):
        logging.info("preparing invite")
        # TODO: add validation
        mail_address = " ".join(arg for arg in match.args())

        send_invitation_mail(mail_address)
        response = "mail sent"
        await bot.api.send_text_message(room.room_id, response)


def send_invitation_mail(receiver_email):
    logging.info("sending email...")

    # make reqest to obtain registration token
    headers = {
        'Content-Type': "application/json",
        'Authorization': "SharedSecret {}".format(os.getenv("REGISTRATION_API_SHARED_SECRET"))
    }
    payload = {
        "max-usage": "1",
        "expiration_date": (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    }
    response = requests.post(os.getenv("REGISTRATION_API_URL"), headers=headers, json=payload)
    logging.info(response.text)
    logging.info(response.json())
    sender_email = os.getenv("MAIL_FROM_ADDRESS")

    body = """Hello,

you have been invited to the f2n.me matrix homeserver!

Click the following link and create your account:

{}

The link will be valid for 7 days.""".format(os.getenv("REGISTRATION_URL") + response.json()["name"])
    msg = MIMEText(body, 'plain')
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Your matrix homeserver invitation link"

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(os.getenv("SMTP_HOSTNAME"), os.getenv("SMTP_PORT"))
        server.ehlo()
        server.starttls()  # Secure the connection
        server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))  # Login to the server

        # Send the email
        server.sendmail(sender_email, receiver_email, msg.as_string())

        logging.info("Email sent successfully")
    except Exception as e:
        logging.error("Error sending mail: {}".format(e))
    finally:
        # Close the connection
        server.quit()


while True:
    try:
        bot.run()
    except (ServerDisconnectedError, ValueError):
        logging.info("connection lost, reconnecting in 5 seconds...")
        time.sleep(5)
    except KeyboardInterrupt:
        logging.info("exiting...")
        sys.exit(0)
