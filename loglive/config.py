TORNADO_PORT = 8888
ZEROMQ_ENDPOINT = "ipc:///tmp/loglive"

COOKIE_SECRET = "erg3345iehusdrSE*&E#%)&*EW2w98$(*@"

NETWORK_DIRECTORIES = {
    "Rizon": "/home/kedo/.znc/users/rizon/moddata/log",
    "OCF": "/home/kedo/.znc/users/ocf/moddata/log",
}

# access control list where the first line that matches is used.
# format is a list of tuples in the form:
#     ("ALLOW" or "DENY", "user email addr", "server", "channel")

# "user email addr", "server", and "channel" can be wildcard "*".
# Also, it is wise to have default DENY
ACCESS_RULES = [
    ("DENY", "*", "*", "Global"),
    ("DENY", "*", "*", "HostServ"),
    ("DENY", "*", "*", "NickServ"),
    ("DENY", "*", "*", "nickserv"),
    ("DENY", "*", "*", "hopm-siglost"),
    ("DENY", "*", "*", "status"),

    ("ALLOW", "*", "Rizon", "#CAA"),

    ("DENY", "*", "*", "*"),
]
