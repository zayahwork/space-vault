"""
_smtp_sink.py - a fake SMTP server on localhost, for testing outreach.py --live
without mailing a real human. Accepts everything, writes each message it
receives to sink_out/<n>.eml, prints a count, exits after --expect messages.

  python _smtp_sink.py --port 8025 --expect 2
"""
import argparse
import socket
import threading
from pathlib import Path

OUT = Path(__file__).resolve().parent / "sink_out"


def handle(conn, got, expect, reject=None):
    """One connection, any number of messages on it. Returns new `got`."""
    f = conn.makefile("rwb")

    def say(s):
        f.write((s + "\r\n").encode())
        f.flush()

    say("220 sink.localhost ESMTP")   # once per connection, not per message
    data_lines, in_data = [], False
    while True:
        line = f.readline()
        if not line:
            break
        text = line.decode("utf-8", "replace").rstrip("\r\n")
        if in_data:
            if text == ".":
                in_data = False
                got += 1
                say("250 2.0.0 Ok: queued")
                OUT.mkdir(exist_ok=True)
                (OUT / f"{got}.eml").write_text("\n".join(data_lines),
                                                encoding="utf-8")
                print(f"sink received {got}", flush=True)
                data_lines = []
                continue
            data_lines.append(text[1:] if text.startswith("..") else text)
            continue
        up = text.upper()
        if up.startswith(("HELO", "EHLO")):
            say("250-sink.localhost")
            say("250 SIZE 35882577")
        elif up.startswith("RCPT TO") and reject and reject.lower() in text.lower():
            say("550 5.1.1 No such user here")   # a real dead address
        elif up.startswith(("MAIL FROM", "RCPT TO")):
            say("250 2.1.0 Ok")
        elif up.startswith("DATA"):
            in_data = True
            say("354 End data with <CR><LF>.<CR><LF>")
        elif up.startswith("QUIT"):
            say("221 2.0.0 Bye")
            break
        else:
            say("250 2.0.0 Ok")
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8025)
    ap.add_argument("--expect", type=int, default=1)
    ap.add_argument("--reject", default=None,
                    help="550 any RCPT TO containing this substring")
    args = ap.parse_args()

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", args.port))
    srv.listen(5)
    srv.settimeout(120)
    print(f"sink listening on 127.0.0.1:{args.port}, expecting {args.expect}",
          flush=True)

    got = 0
    while got < args.expect:
        try:
            conn, _ = srv.accept()
        except socket.timeout:
            print("sink timed out", flush=True)
            break
        with conn:
            got = handle(conn, got, args.expect, args.reject)
    print(f"SINK_TOTAL={got}", flush=True)


if __name__ == "__main__":
    main()
