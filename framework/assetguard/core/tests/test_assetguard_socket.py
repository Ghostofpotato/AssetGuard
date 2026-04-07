# Copyright (C) 2015, AssetGuard Inc.
# Created by AssetGuard, Inc. <info@assetguard.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
import pytest

from assetguard.core.exception import AssetGuardException
from assetguard.core.assetguard_socket import AssetGuardSocket, AssetGuardSocketJSON, AssetGuardAsyncSocket, AssetGuardAsyncSocketJSON, \
    SOCKET_COMMUNICATION_PROTOCOL_VERSION, create_assetguard_socket_message


@patch('assetguard.core.assetguard_socket.AssetGuardSocket._connect')
def test_AssetGuardSocket__init__(mock_conn):
    """Tests AssetGuardSocket.__init__ function works"""

    AssetGuardSocket('test_path')

    mock_conn.assert_called_once_with()


@patch('assetguard.core.assetguard_socket.socket.socket.connect')
def test_AssetGuardSocket_protected_connect(mock_conn):
    """Tests AssetGuardSocket._connect function works"""

    AssetGuardSocket('test_path')

    mock_conn.assert_called_with('test_path')


@patch('assetguard.core.assetguard_socket.socket.socket.connect', side_effect=Exception)
def test_AssetGuardSocket_protected_connect_ko(mock_conn):
    """Tests AssetGuardSocket._connect function exceptions works"""

    with pytest.raises(AssetGuardException, match=".* 1013 .*"):
        AssetGuardSocket('test_path')


@patch('assetguard.core.assetguard_socket.socket.socket.connect')
@patch('assetguard.core.assetguard_socket.socket.socket.close')
def test_AssetGuardSocket_close(mock_close, mock_conn):
    """Tests AssetGuardSocket.close function works"""

    queue = AssetGuardSocket('test_path')

    queue.close()

    mock_conn.assert_called_once_with('test_path')
    mock_close.assert_called_once_with()


@patch('assetguard.core.assetguard_socket.socket.socket.connect')
@patch('assetguard.core.assetguard_socket.socket.socket.send')
def test_AssetGuardSocket_send(mock_send, mock_conn):
    """Tests AssetGuardSocket.send function works"""

    queue = AssetGuardSocket('test_path')

    response = queue.send(b"\x00\x01")

    assert isinstance(response, MagicMock)
    mock_conn.assert_called_once_with('test_path')


@pytest.mark.parametrize('msg, effect, send_effect, expected_exception', [
    ('text_msg', 'side_effect', None, 1105),
    (b"\x00\x01", 'return_value', 0, 1014),
    (b"\x00\x01", 'side_effect', Exception, 1014)
])
@patch('assetguard.core.assetguard_socket.socket.socket.connect')
def test_AssetGuardSocket_send_ko(mock_conn, msg, effect, send_effect, expected_exception):
    """Tests AssetGuardSocket.send function exceptions works"""

    queue = AssetGuardSocket('test_path')

    if effect == 'return_value':
        with patch('assetguard.core.assetguard_socket.socket.socket.send', return_value=send_effect):
            with pytest.raises(AssetGuardException, match=f'.* {expected_exception} .*'):
                queue.send(msg)
    else:
        with patch('assetguard.core.assetguard_socket.socket.socket.send', side_effect=send_effect):
            with pytest.raises(AssetGuardException, match=f'.* {expected_exception} .*'):
                queue.send(msg)

    mock_conn.assert_called_once_with('test_path')


@patch('assetguard.core.assetguard_socket.socket.socket.connect')
@patch('assetguard.core.assetguard_socket.unpack', return_value='1024')
@patch('assetguard.core.assetguard_socket.socket.socket.recv')
def test_AssetGuardSocket_receive(mock_recv, mock_unpack, mock_conn):
    """Tests AssetGuardSocket.receive function works"""

    queue = AssetGuardSocket('test_path')

    response = queue.receive()

    assert isinstance(response, MagicMock)
    mock_conn.assert_called_once_with('test_path')


@patch('assetguard.core.assetguard_socket.socket.socket.connect')
@patch('assetguard.core.assetguard_socket.socket.socket.recv', side_effect=Exception)
def test_AssetGuardSocket_receive_ko(mock_recv, mock_conn):
    """Tests AssetGuardSocket.receive function exception works"""

    queue = AssetGuardSocket('test_path')

    with pytest.raises(AssetGuardException, match=".* 1014 .*"):
        queue.receive()

    mock_conn.assert_called_once_with('test_path')


@patch('assetguard.core.assetguard_socket.AssetGuardSocket._connect')
def test_AssetGuardSocketJSON__init__(mock_conn):
    """Tests AssetGuardSocketJSON.__init__ function works"""

    AssetGuardSocketJSON('test_path')

    mock_conn.assert_called_once_with()


@patch('assetguard.core.assetguard_socket.socket.socket.connect')
@patch('assetguard.core.assetguard_socket.AssetGuardSocket.send')
def test_AssetGuardSocketJSON_send(mock_send, mock_conn):
    """Tests AssetGuardSocketJSON.send function works"""

    queue = AssetGuardSocketJSON('test_path')

    response = queue.send('test_msg')

    assert isinstance(response, MagicMock)
    mock_conn.assert_called_once_with('test_path')


@pytest.mark.parametrize('raw', [
    True, False
])
@patch('assetguard.core.assetguard_socket.socket.socket.connect')
@patch('assetguard.core.assetguard_socket.AssetGuardSocket.receive')
@patch('assetguard.core.assetguard_socket.loads', return_value={'error':0, 'message':None, 'data':'Ok'})
def test_AssetGuardSocketJSON_receive(mock_loads, mock_receive, mock_conn, raw):
    """Tests AssetGuardSocketJSON.receive function works"""
    queue = AssetGuardSocketJSON('test_path')
    response = queue.receive(raw=raw)
    if raw:
        assert isinstance(response, dict)
    else:
        assert isinstance(response, str)
    mock_conn.assert_called_once_with('test_path')


@patch('assetguard.core.assetguard_socket.socket.socket.connect')
@patch('assetguard.core.assetguard_socket.AssetGuardSocket.receive')
@patch('assetguard.core.assetguard_socket.loads', return_value={'error':10000, 'message':'Error', 'data':'KO'})
def test_AssetGuardSocketJSON_receive_ko(mock_loads, mock_receive, mock_conn):
    """Tests AssetGuardSocketJSON.receive function works"""

    queue = AssetGuardSocketJSON('test_path')

    with pytest.raises(AssetGuardException, match=".* 10000 .*"):
        queue.receive()

    mock_conn.assert_called_once_with('test_path')


@pytest.mark.parametrize('origin, command, parameters', [
    ('origin_sample', 'command_sample', {'sample': 'sample'}),
    (None, 'command_sample', {'sample': 'sample'}),
    ('origin_sample', None, {'sample': 'sample'}),
    ('origin_sample', 'command_sample', None),
    (None, None, None)
])
def test_create_assetguard_socket_message(origin, command, parameters):
    """Test create_assetguard_socket_message function."""
    response_message = create_assetguard_socket_message(origin, command, parameters)
    assert response_message['version'] == SOCKET_COMMUNICATION_PROTOCOL_VERSION
    assert response_message.get('origin') == origin
    assert response_message.get('command') == command
    assert response_message.get('parameters') == parameters


class TestAssetGuardAsyncSocket:
    """Test AssetGuardAsyncSocket class"""

    @pytest.mark.asyncio
    async def test_AssetGuardAsyncSocket__init__(self):
        """Tests AssetGuardAsyncSocket.__init__ function works"""
        socket_instance = AssetGuardAsyncSocket()

        assert socket_instance.transport is None
        assert socket_instance.protocol is None
        assert socket_instance.s is None
        assert socket_instance.loop is None

    @pytest.mark.asyncio
    @patch('assetguard.core.assetguard_socket.socket.socket')
    @patch('asyncio.get_running_loop')
    async def test_AssetGuardAsyncSocket_connect(self, mock_loop, mock_socket):
        """Tests AssetGuardAsyncSocket.connect function works"""
        mock_loop_instance = AsyncMock()
        mock_loop.return_value = mock_loop_instance
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Mock the create_connection to return transport and protocol
        mock_transport = MagicMock()
        mock_protocol = MagicMock()
        mock_loop_instance.create_connection.return_value = (mock_transport, mock_protocol)

        socket_instance = AssetGuardAsyncSocket()
        await socket_instance.connect('test_path')

        mock_socket_instance.connect.assert_called_once_with('test_path')
        mock_loop_instance.create_connection.assert_called_once()

    @pytest.mark.asyncio
    @patch('assetguard.core.assetguard_socket.socket.socket')
    @patch('asyncio.get_running_loop')
    async def test_AssetGuardAsyncSocket_connect_file_not_found(self, mock_loop, mock_socket):
        """Tests AssetGuardAsyncSocket.connect function FileNotFoundError exception"""
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.connect.side_effect = FileNotFoundError()

        socket_instance = AssetGuardAsyncSocket()

        with pytest.raises(AssetGuardException, match=".* 1013 .*"):
            await socket_instance.connect('test_path')

    @pytest.mark.asyncio
    async def test_AssetGuardAsyncSocket_is_connection_lost(self):
        """Tests AssetGuardAsyncSocket.is_connection_lost function"""
        socket_instance = AssetGuardAsyncSocket()
        socket_instance.transport = MagicMock()
        socket_instance.protocol = MagicMock()

        socket_instance.transport.is_closing.return_value = False
        socket_instance.protocol.closed = False
        assert not socket_instance.is_connection_lost()

        socket_instance.transport.is_closing.return_value = True
        assert socket_instance.is_connection_lost()

    @pytest.mark.asyncio
    async def test_AssetGuardAsyncSocket_close(self):
        """Tests AssetGuardAsyncSocket.close function works"""
        socket_instance = AssetGuardAsyncSocket()
        socket_instance.s = MagicMock()
        socket_instance.transport = MagicMock()
        socket_instance.transport.is_closing.return_value = False

        await socket_instance.close()

        socket_instance.s.close.assert_called_once()
        socket_instance.transport.close.assert_called_once()

    @pytest.mark.asyncio
    @patch('assetguard.core.assetguard_socket.pack', return_value=b'\x00\x00\x00\x02')
    async def test_AssetGuardAsyncSocket_send(self, mock_pack):
        """Tests AssetGuardAsyncSocket.send function works"""
        socket_instance = AssetGuardAsyncSocket()
        socket_instance.transport = MagicMock()
        socket_instance.protocol = MagicMock()
        socket_instance.transport.is_closing.return_value = False
        socket_instance.protocol.closed = False

        response = await socket_instance.send(b"\x00\x01")

        assert isinstance(response, int)
        socket_instance.transport.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_AssetGuardAsyncSocket_send_invalid_type(self):
        """Tests AssetGuardAsyncSocket.send function with invalid type"""
        socket_instance = AssetGuardAsyncSocket()

        with pytest.raises(AssetGuardException, match=".* 1105 .*"):
            await socket_instance.send("invalid_type")

    @pytest.mark.asyncio
    @patch('assetguard.core.assetguard_socket.pack', return_value=b'\x00\x00\x00\x00')
    async def test_AssetGuardAsyncSocket_send_zero_length(self, mock_pack):
        """Tests AssetGuardAsyncSocket.send function with zero length message"""
        socket_instance = AssetGuardAsyncSocket()
        socket_instance.transport = MagicMock()
        socket_instance.protocol = MagicMock()
        socket_instance.transport.is_closing.return_value = False
        socket_instance.protocol.closed = False

        with pytest.raises(AssetGuardException, match=".* 1014 .*"):
            await socket_instance.send(b"")

    @pytest.mark.asyncio
    @patch('assetguard.core.assetguard_socket.pack', return_value=b'\x00\x00\x00\x02')
    async def test_AssetGuardAsyncSocket_send_connection_lost(self, mock_pack):
        """Tests AssetGuardAsyncSocket.send function when connection is lost"""
        socket_instance = AssetGuardAsyncSocket()
        socket_instance.transport = MagicMock()
        socket_instance.protocol = MagicMock()
        socket_instance.transport.is_closing.return_value = True
        socket_instance.protocol.closed = False

        with patch.object(socket_instance, 'close', new_callable=AsyncMock):
            with pytest.raises(AssetGuardException, match=".* 1014 .*"):
                await socket_instance.send(b"\x00\x01")

    @pytest.mark.asyncio
    @patch('assetguard.core.assetguard_socket.unpack', return_value=[2])
    async def test_AssetGuardAsyncSocket_receive(self, mock_unpack):
        """Tests AssetGuardAsyncSocket.receive function works"""
        socket_instance = AssetGuardAsyncSocket()
        socket_instance.protocol = MagicMock()
        # Don't mock on_data_received as AsyncMock since it's not meant to be awaited
        # Instead, create a simple future that's already done
        future = asyncio.Future()
        future.set_result(None)
        socket_instance.protocol.on_data_received = future
        socket_instance.protocol.get_data.return_value = b'\x00\x00\x00\x02OK'
        socket_instance.transport = MagicMock()

        response = await socket_instance.receive()

        assert response == b'OK'
        mock_unpack.assert_called_once()

    @pytest.mark.asyncio
    @patch('assetguard.core.assetguard_socket.unpack', return_value=[5])
    async def test_AssetGuardAsyncSocket_receive_size_mismatch(self, mock_unpack):
        """Tests AssetGuardAsyncSocket.receive function with size mismatch"""
        socket_instance = AssetGuardAsyncSocket()
        socket_instance.protocol = MagicMock()
        socket_instance.protocol.on_data_received = AsyncMock()
        socket_instance.protocol.get_data.return_value = b'\x00\x00\x00\x05OK'  # Header says 5 bytes, but only 2 in data
        socket_instance.transport = MagicMock()

        with pytest.raises(AssetGuardException, match=".* 1014 .*"):
            await socket_instance.receive()

    @pytest.mark.asyncio
    async def test_AssetGuardAsyncSocket_receive_exception(self):
        """Tests AssetGuardAsyncSocket.receive function with exception"""
        socket_instance = AssetGuardAsyncSocket()
        socket_instance.protocol = MagicMock()
        socket_instance.protocol.on_data_received = AsyncMock(side_effect=Exception("Test error"))
        socket_instance.transport = MagicMock()

        with pytest.raises(AssetGuardException, match=".* 1014 .*"):
            await socket_instance.receive()


class TestAssetGuardAsyncSocketJSON:
    """Test AssetGuardAsyncSocketJSON class"""

    @pytest.mark.asyncio
    async def test_AssetGuardAsyncSocketJSON__init__(self):
        """Tests AssetGuardAsyncSocketJSON.__init__ function works"""
        socket_instance = AssetGuardAsyncSocketJSON()

        assert socket_instance.transport is None
        assert socket_instance.protocol is None
        assert socket_instance.s is None
        assert socket_instance.loop is None

    @pytest.mark.asyncio
    @patch('assetguard.core.assetguard_socket.AssetGuardAsyncSocket.send')
    @patch('assetguard.core.assetguard_socket.dumps', return_value='{"test": "message"}')
    async def test_AssetGuardAsyncSocketJSON_send(self, mock_dumps, mock_send):
        """Tests AssetGuardAsyncSocketJSON.send function works"""
        mock_send.return_value = 10
        socket_instance = AssetGuardAsyncSocketJSON()

        response = await socket_instance.send({'test': 'message'})

        assert response == 10
        mock_dumps.assert_called_once_with({'test': 'message'})
        mock_send.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('raw', [True, False])
    @patch('assetguard.core.assetguard_socket.AssetGuardAsyncSocket.receive')
    @patch('assetguard.core.assetguard_socket.loads', return_value={'error': 0, 'message': None, 'data': 'Ok'})
    async def test_AssetGuardAsyncSocketJSON_receive(self, mock_loads, mock_receive, raw):
        """Tests AssetGuardAsyncSocketJSON.receive function works"""
        mock_receive.return_value = b'{"error": 0, "message": null, "data": "Ok"}'
        socket_instance = AssetGuardAsyncSocketJSON()

        response = await socket_instance.receive(raw=raw)

        if raw:
            assert isinstance(response, dict)
            assert response == {'error': 0, 'message': None, 'data': 'Ok'}
        else:
            assert response == 'Ok'

        mock_receive.assert_called_once()
        mock_loads.assert_called_once()

    @pytest.mark.asyncio
    @patch('assetguard.core.assetguard_socket.AssetGuardAsyncSocket.receive')
    @patch('assetguard.core.assetguard_socket.loads', return_value={'error': 10000, 'message': 'Error', 'data': 'KO'})
    async def test_AssetGuardAsyncSocketJSON_receive_error(self, mock_loads, mock_receive):
        """Tests AssetGuardAsyncSocketJSON.receive function with error response"""
        mock_receive.return_value = b'{"error": 10000, "message": "Error", "data": "KO"}'
        socket_instance = AssetGuardAsyncSocketJSON()

        with pytest.raises(AssetGuardException, match=".* 10000 .*"):
            await socket_instance.receive()

        mock_receive.assert_called_once()
        mock_loads.assert_called_once()

    @pytest.mark.asyncio
    @patch('assetguard.core.assetguard_socket.AssetGuardAsyncSocket.receive')
    @patch('assetguard.core.assetguard_socket.loads', return_value={'error': 0, 'message': None, 'data': 'Ok'})
    async def test_AssetGuardAsyncSocketJSON_receive_raw_true(self, mock_loads, mock_receive):
        """Tests AssetGuardAsyncSocketJSON.receive function with raw=True"""
        mock_receive.return_value = b'{"error": 0, "message": null, "data": "Ok"}'
        socket_instance = AssetGuardAsyncSocketJSON()

        response = await socket_instance.receive(raw=True)

        assert isinstance(response, dict)
        assert response == {'error': 0, 'message': None, 'data': 'Ok'}
        mock_receive.assert_called_once()
        mock_loads.assert_called_once()
