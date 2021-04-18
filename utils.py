import os
from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter
from opencensus.trace import tracer as tracer_module
from opencensus.trace.samplers import AlwaysOnSampler


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


TRACER = None
def get_tracer():
    global TRACER
    if TRACER is None:
        exporter = stackdriver_exporter.StackdriverExporter(project_id='testedtimestamp')
        TRACER = tracer_module.Tracer(exporter=exporter, sampler=AlwaysOnSampler())
    return TRACER


def delete_file_if_exists(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)


def make_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
