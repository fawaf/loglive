TORNADO_PORT = 8888
ZEROMQ_ENDPOINT = "ipc:///tmp/loglive"

COOKIE_SECRET = "erg3345iehusdrSE*&E#%)&*EW2w98$(*@"

NETWORK_DIRECTORIES = {
    "Rizon": "/home/kedo/.znc/users/rizon/moddata/log",
    "OCF": "/home/kedo/.znc/users/ocf/moddata/log",
}

# Access control list where the first line that matches is used.
# Format is a list of tuples in the form:
#     ("ALLOW" or "DENY", "user email addr", "server", "channel")

# "user email addr" and "server"  can be wildcard "*".
# However, "channel" is a regex, so its wildcard is r'.*'.
# The "channel" regex is matched using re.search, so it scans the channel
# looking for a match.
# It is wise to have default DENY
ACCESS_RULES = [
    ("DENY", "*", "*", r'^Global$'),
    ("DENY", "*", "*", r'^[Hh]ost[Ss]erv$'),
    ("DENY", "*", "*", r'^[Nn]ick[Ss]erv$'),
    ("DENY", "*", "*", r'^hopm-siglost$'),
    ("DENY", "*", "*", r'^status$'),

    ("ALLOW", "*", "Rizon", r'^#CAA$'),

    ("ALLOW", "*", "OCF", r'^#ocf$'),

    ("DENY", "*", "*", r'.*'),
]
