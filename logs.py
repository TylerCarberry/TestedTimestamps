import apprise
import os


def post_to_discord(title, body):
    app = apprise.Apprise()
    app.add("discord://{}/{}/".format(os.environ["DISCORD_WEBHOOK_ID"], os.environ["DISCORD_WEBHOOK_TOKEN"]))
    app.notify(
        title=title,
        body=body
    )
