#!/usr/bin/env python3
"""Forward a macOS serial device to one raw TCP client.

This lets the containerized ESPHome/esptool process reach a USB serial port
that Docker Desktop cannot pass through as a Linux device. It uses only the
Python standard library and intentionally serves a single connection.
"""

from __future__ import annotations

import argparse
import fcntl
import os
import select
import socket
import struct
import termios
import time
import tty


def configure_serial(fd: int, baud: int) -> None:
    speeds = {
        115200: termios.B115200,
    }
    if baud not in speeds:
        raise ValueError(f"Unsupported baud rate: {baud}")

    tty.setraw(fd)
    attrs = termios.tcgetattr(fd)
    attrs[4] = speeds[baud]
    attrs[5] = speeds[baud]
    termios.tcsetattr(fd, termios.TCSANOW, attrs)

    # Native USB CDC/JTAG logging may wait until a terminal asserts DTR.
    modem_bits = struct.pack("I", termios.TIOCM_DTR)
    fcntl.ioctl(fd, termios.TIOCMBIS, modem_bits)

    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)


def open_serial(serial_path: str, baud: int) -> int:
    serial_fd = os.open(serial_path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    configure_serial(serial_fd, baud)
    return serial_fd


def bridge(serial_path: str, host: str, port: int, baud: int) -> None:
    serial_fd = open_serial(serial_path, baud)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(1)
        print(f"Serial bridge ready: {serial_path} <-> {host}:{port}", flush=True)

        connection, address = server.accept()
        print(f"Client connected: {address[0]}:{address[1]}", flush=True)
        with connection:
            while True:
                if serial_fd is None:
                    try:
                        serial_fd = open_serial(serial_path, baud)
                        print(f"Serial device reconnected: {serial_path}", flush=True)
                    except OSError:
                        readable, _, _ = select.select([connection], [], [], 0.25)
                        if connection in readable and not connection.recv(4096):
                            break
                        time.sleep(0.25)
                        continue

                readable, _, _ = select.select([serial_fd, connection], [], [], 1.0)
                if serial_fd in readable:
                    try:
                        data = os.read(serial_fd, 4096)
                    except OSError:
                        os.close(serial_fd)
                        serial_fd = None
                        print("Serial device disconnected; waiting for it to return", flush=True)
                        continue
                    if data:
                        connection.sendall(data)
                if connection in readable:
                    data = connection.recv(4096)
                    if not data:
                        break
                    try:
                        os.write(serial_fd, data)
                    except OSError:
                        os.close(serial_fd)
                        serial_fd = None
                        print("Serial device disconnected; waiting for it to return", flush=True)

    if serial_fd is not None:
        os.close(serial_fd)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("serial_path")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=3333)
    parser.add_argument("--baud", type=int, default=115200)
    args = parser.parse_args()
    bridge(args.serial_path, args.host, args.port, args.baud)


if __name__ == "__main__":
    main()
