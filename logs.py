import apprise
import os

CUSTOM_AVATAR = False

def post_to_discord(title, body):
    app = apprise.Apprise()
    app.add("discord://{}/{}/?avatar={}".format(os.environ["DISCORD_WEBHOOK_ID"], os.environ["DISCORD_WEBHOOK_TOKEN"], CUSTOM_AVATAR))
    app.notify(
        title=title,
        body=body
    )
