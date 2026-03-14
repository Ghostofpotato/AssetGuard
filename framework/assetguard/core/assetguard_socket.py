# Copyright (C) 2015, AssetGuard Inc.
# Created by AssetGuard, Inc. <info@assetguard.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import asyncio
import os.path
import socket
from json import dumps, loads
from struct import pack, unpack

from assetguard import common
from assetguard.core.exception import AssetGuardException, AssetGuardInternalError

SOCKET_COMMUNICATION_PROTOCOL_VERSION = 1


class AssetGuardSocket:
    MAX_SIZE = 65536

    def __init__(self, path):
        self.path = path
        self._connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self

    def _connect(self):
        try:
            self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.s.connect(self.path)
        except FileNotFoundError:
            raise AssetGuardInternalError(1013, extra_message=os.path.basename(self.path))
        except ConnectionRefusedError:
            raise AssetGuardInternalError(1121, extra_message=f"Socket '{os.path.basename(self.path)}' cannot receive "
                                                         "connections")
        except Exception as e:
            raise AssetGuardException(1013, str(e))

    def close(self):
        self.s.close()

    def send(self, msg_bytes, header_format="<I"):
        if not isinstance(msg_bytes, bytes):
            raise AssetGuardException(1105, "Type must be bytes")

        try:
            sent = self.s.send(pack(header_format, len(msg_bytes)) + msg_bytes)
            if sent == 0:
                raise AssetGuardException(1014, "Number of sent bytes is 0")
            return sent
        except Exception as e:
            raise AssetGuardException(1014, str(e))

    def receive(self, header_format="<I", header_size=4):

        try:
            size = unpack(header_format, self.s.recv(header_size, socket.MSG_WAITALL))[0]
            return self.s.recv(size, socket.MSG_WAITALL)
        except Exception as e:
            raise AssetGuardException(1014, str(e))


class AssetGuardSocketJSON(AssetGuardSocket):
    MAX_SIZE = 65536

    def __init__(self, path):
        AssetGuardSocket.__init__(self, path)

    def send(self, msg, header_format="<I"):
        return AssetGuardSocket.send(self, msg_bytes=dumps(msg).encode(), header_format=header_format)

    def receive(self, header_format="<I", header_size=4, raw=False):
        response = loads(AssetGuardSocket.receive(self, header_format=header_format, header_size=header_size).decode())
        if not raw:
            if 'error' in response.keys():
                if response['error'] != 0:
                    raise AssetGuardException(response['error'], response['message'], cmd_error=True)
            return response['data']
        else:
            return response


class AssetGuardAsyncProtocol(asyncio.Protocol):
    """AssetGuard implementation of asyncio.Protocol class."""

    def __init__(self, loop):
        self.loop = loop
        self.on_data_received = loop.create_future()
        self.data = None
        self.closed = False

    def connection_lost(self, exc):
        self.closed = True

    def data_received(self, data: bytes) -> None:
        self.data = data
        self.on_data_received.set_result(True)

    def get_data(self) -> bytes:
        if self.data:
            aux = self.data
            self.data = None
            self.on_data_received = self.loop.create_future()
            return aux


class AssetGuardAsyncSocket:
    """Handler class to connect and operate with sockets asynchronously."""

    def __init__(self):
        self.transport = None
        self.protocol = None
        self.s = None
        self.loop = None

    async def connect(self, path_to_socket: str):
        """Establish connection with the socket and creates both Transport and Protocol objects to operate with it.

        Parameters
        ----------
        path_to_socket : str
            Path where the socket is located.

        Raises
        ------
        AssetGuardException(1013)
            If the connection with the socket can't be established.
        """
        try:
            self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.s.connect(path_to_socket)
            self.loop = asyncio.get_running_loop()
            self.transport, self.protocol = await self.loop.create_connection(
                lambda: AssetGuardAsyncProtocol(self.loop), sock=self.s)
        except (socket.error, FileNotFoundError) as e:
            raise AssetGuardException(1013, str(e))
        except (AttributeError, ValueError, OSError) as e:
            self.s.close()
            raise AssetGuardException(1013, str(e))

    def is_connection_lost(self):
        return self.transport.is_closing() or self.protocol.closed

    async def close(self):
        """Close connection with the socket and the Transport objects."""
        self.s.close()
        if not self.transport.is_closing():
            self.transport.close()

    async def send(self, msg_bytes: bytes, header_format: str = "<I") -> int:
        """Add a header to the message and sends it to the socket. Returns the number of bytes sent.

        Parameters
        ----------
        msg_bytes : bytes
            A set of bytes to be send.
        header_format : str, optional
            Format of the header to be packed in the message. Defaults to "<I".

        Raises
        ------
        AssetGuardException(1105)
            If the `msg_bytes` type is not bytes.
        AssetGuardException(1014)
            If the message length was 0 or socket connection was closed.

        Returns
        -------
        int
            Number of bytes sent.
        """
        if not isinstance(msg_bytes, bytes):
            raise AssetGuardException(1105, "Type must be bytes")

        try:
            msg_length = len(msg_bytes)
            data = pack(header_format, msg_length) + msg_bytes
            self.transport.write(data)

            if self.is_connection_lost():
                await self.close()
                raise AssetGuardException(1014, "Socket connection was closed")

            if msg_length == 0:
                raise AssetGuardException(1014, "Number of sent bytes is 0")

            return len(data)
        except Exception as e:
            raise AssetGuardException(1014, str(e))

    async def receive(self, header_format: str = "<I", header_size: int = 4) -> bytes:
        """Return the content of the socket after reading the header to get the message size.

        Parameters
        ----------
        header_format : str, optional
            Format of the header to unpack. Defaults to "<I".
        header_size : int, optional
            Size of the header to be extracted from the message received. Defaults to 4.

        Raises
        ------
        AssetGuardException(1014)
            If there is no connection with the socket or error receiving data.

        Returns
        -------
        bytes
            Bytes received (without header).
        """
        try:
            await self.protocol.on_data_received
            full_data = self.protocol.get_data()

            # Extract and validate message size from header
            size = unpack(header_format, full_data[:header_size])[0]
            message_data = full_data[header_size:]

            if len(message_data) != size:
                raise AssetGuardException(1014, f"Expected {size} bytes but received {len(message_data)}")

            return message_data
        except Exception as e:
            self.transport.close()
            raise AssetGuardException(1014, str(e))


class AssetGuardAsyncSocketJSON(AssetGuardAsyncSocket):
    """Handler class to connect and operate asynchronously with a socket using messages in JSON format."""

    def __init__(self):
        AssetGuardAsyncSocket.__init__(self)

    async def send(self, msg: str, header_format: str = None) -> bytes:
        """Converts the message from JSON format to bytes and send it to the socket. Returns that message.

        Parameters
        ----------
        msg : str
            The message in JSON format.
        header_format : str, optional
            Format of the header to be packed in the message.

        Returns
        -------
        bytes
            Bytes sent.
        """
        return await AssetGuardAsyncSocket.send(self, dumps(msg).encode(), header_format)

    async def receive(self, header_format: str = "<I", header_size: int = 4, raw: bool = False) -> dict:
        """Get the data from the socket and converts it to JSON.

        Parameters
        ----------
        header_format : str, optional
            Format of the header to unpack. Defaults to "<I".
        header_size : int, optional
            Size of the header to be extracted from the message received. Defaults to 4.
        raw : bool, optional
            If True, return the full response. If False, return only the data field. Defaults to False.

        Raises
        ------
        AssetGuardException
            If the message obtained from the socket was an error message.

        Returns
        -------
        dict
            Data received or full response based on raw parameter.
        """
        response_bytes = await AssetGuardAsyncSocket.receive(self, header_format, header_size)
        response = loads(response_bytes.decode())

        if not raw:
            if 'error' in response.keys():
                if response['error'] != 0:
                    raise AssetGuardException(response['error'], response['message'], cmd_error=True)
            return response['data']
        else:
            return response


daemons = {
    "authd": {"protocol": "TCP", "path": common.AUTHD_SOCKET, "header_format": "<I", "size": 4},
    "task-manager": {"protocol": "TCP", "path": common.TASKS_SOCKET, "header_format": "<I", "size": 4},
    "assetguard-manager-db": {"protocol": "TCP", "path": common.WDB_SOCKET, "header_format": "<I", "size": 4},
    "remoted": {"protocol": "TCP", "path": common.REMOTED_SOCKET, "header_format": "<I", "size": 4}
}


async def assetguard_sendasync(daemon_name: str, message: str = None) -> dict:
    """Send a message to the specified daemon's socket and wait for its response.

    Parameters
    ----------
    daemon_name : str
        Name of the daemon to send the message.
    message : str, optional
        Message in JSON format to be sent to the daemon's socket.

    Returns
    -------
    dict
        Data received.
    """
    try:
        sock = AssetGuardAsyncSocket()
        await sock.connect(daemons[daemon_name]['path'])
        if isinstance(message, dict):
            message = dumps(message)
        await sock.send(msg_bytes=message.encode(), header_format=daemons[daemon_name]['header_format'])
        data = await sock.receive(header_size=daemons[daemon_name]['size'])
        await sock.close()
    except AssetGuardException as e:
        raise e
    except Exception as e:
        raise AssetGuardInternalError(1014, extra_message=e)

    return data


async def assetguard_sendsync(daemon_name: str = None, message: str = None) -> dict:
    """Send a message to the specified daemon's socket and wait for its response.

    Parameters
    ----------
    daemon_name : str
        Name of the daemon to send the message.
    message : str, optional
        Message in JSON format to be sent to the daemon's socket.

    Raises
    ------
    AssetGuardInternalError(1014)
        Error communicating with socket.

    Returns
    -------
    dict
        Data received.
    """
    try:
        sock = AssetGuardSocket(daemons[daemon_name]['path'])
        if isinstance(message, dict):
            message = dumps(message)
        sock.send(msg_bytes=message.encode(), header_format=daemons[daemon_name]['header_format'])
        data = sock.receive(header_format=daemons[daemon_name]['header_format'],
                            header_size=daemons[daemon_name]['size']).decode()
        sock.close()
    except AssetGuardException as e:
        raise e
    except Exception as e:
        raise AssetGuardInternalError(1014, extra_message=e)

    return data


def create_assetguard_socket_message(origin=None, command=None, parameters=None):
    communication_protocol_message = {'version': SOCKET_COMMUNICATION_PROTOCOL_VERSION}

    if origin:
        communication_protocol_message['origin'] = origin

    if command:
        communication_protocol_message['command'] = command

    if parameters:
        communication_protocol_message['parameters'] = parameters

    return communication_protocol_message
