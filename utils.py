# Format seconds into hours, minutes, seconds with colons in between
# This format creates a hyperlink in Youtube to the correct time
# 5000 seconds --> 1:23:20
def format_seconds(seconds):
    hours = int(seconds / (60 * 60))
    seconds -= hours * 60 * 60
    minutes = int(seconds / 60)
    seconds = int(seconds - minutes * 60)

    if hours == 0:
        return "{:01d}:{:02d}".format(minutes, seconds)
    return "{:01d}:{:02d}:{:02d}".format(hours, minutes, seconds)


# Find text between two substrings
# Ex. ("This is only a test", is, a) --> only
def text_between(line, start, end):
    return line[line.index(start) + len(start): line.index(end)].strip()
