"""
This module handels the communication with the api and the students logic.
"""
import gc
import logging
import sys
import time
from typing import List, Union

from socha.api.networking.xml_protocol_interface import XMLProtocolInterface
from socha.api.plugin.penguins.board import Move
from socha.api.plugin.penguins.game_state import GameState
from socha.api.plugin.penguins.utils import handle_move, if_last_game_state, if_not_last_game_state
from socha.api.protocol.protocol import State, Error, Join, Joined, JoinPrepared, JoinRoom, Room, Result, MoveRequest, \
    Left, Errorpacket
from socha.api.protocol.protocol_packet import ProtocolPacket


class IClientHandler:
    history: List[List[Union[GameState, Error, Result]]] = []

    def calculate_move(self) -> Move:
        """
        Calculates a move that the logic wants the server to perform in the game room.
        """

    def on_update(self, state: GameState):
        """
        If the server _send a update on the current state of the game this method is called.
        :param state: The current state that server sent.
        """

    def on_game_over(self, roomMessage: Result):
        """
        If the game has ended the server will _send a result message.
        This method will called if this happens.

        :param roomMessage: The Result the server has sent.
        """

    def on_error(self, logMessage: str):
        """
        If error occurs,
        for instance when the logic sent a move that is not rule conform,
        the server will _send an error message and closes the connection.
        If this happens, this method is called.

        :param logMessage: The message, that server sent.
        """

    def on_room_message(self, data):
        """
        If the server sends a message that cannot be handelt by anny other method,
        this will be called.

        :param data: The data the Server sent.
        """

    def on_game_prepared(self, message):
        """
        If the game has been prepared by the server this method will be called.

        :param message: The message that server sends with the response.
        """

    def on_game_joined(self, room_id):
        """
        If the client has successfully joined a game room this method will be called.

        :param room_id: The room id the client has joined.
        """

    def on_game_observed(self, message):
        """
        If the client successfully joined as observer this method will be called.

        :param message: The message that server sends with the response.
        """

    def on_game_left(self):
        """
        If the server left the room, this method will be called.
        If the client is running on survive mode it'll be running until shut downed manually.
        """

    def while_disconnected(self, player_client: 'GameClient'):
        """
        The client loop will keep calling this method while there is no active connection to a game server.
        This can be used to do tasks after a game is finished and the server left.
        Please be aware, that the client has to be shut down manually if it is in survive mode.
        The return statement is used to tell the client whether to exit or not.

        :type player_client: The player client in which the logic is integrated.
        :return: True if the client should shut down. False if the client should continue to run.
        """


class GameClient(XMLProtocolInterface):
    """
    The PlayerClient handles all incoming and outgoing objects accordingly to their types.
    """

    def __init__(self, host: str, port: int, handler: IClientHandler, reservation: str,
                 room_id: str, auto_reconnect: bool, survive: bool):
        super().__init__(host, port)
        self._game_handler = handler
        self.reservation = reservation
        self.room_id = room_id
        self.auto_reconnect = auto_reconnect
        self.survive = survive

    def join_game(self):
        self._send(Join())

    def join_game_room(self, room_id: str):
        self._send(JoinRoom(room_id=room_id))

    def join_game_with_reservation(self, reservation: str):
        self._send(JoinPrepared(reservation_code=reservation))

    def send_message_to_room(self, room_id: str, message):
        self._send(Room(room_id=room_id, data=message))

    def _on_object(self, message):
        """
        Process various types of messages related to a game.

        Args:
            message: The message object containing information about the game.

        Returns:
            None
        """
        if isinstance(message, Errorpacket):
            logging.error(f"An error occurred while handling the request: {message}")
            self._game_handler.on_error(str(message))
            self.stop()
        else:
            room_id = message.room_id
            if isinstance(message, Joined):
                self._game_handler.on_game_joined(room_id=room_id)
            elif isinstance(message, Left):
                self._game_handler.on_game_left()
            elif isinstance(message.data.class_binding, MoveRequest):
                self._on_move_request(room_id)
            elif isinstance(message.data.class_binding, State):
                self._on_state(message)
            elif isinstance(message.data.class_binding, Result):
                self._game_handler.history[-1].append(message.data.class_binding)
                self._game_handler.on_game_over(message.data.class_binding)
            elif isinstance(message, Room):
                self._game_handler.on_room_message(message.data.class_binding)

    def _on_move_request(self, room_id):
        start_time = time.time()
        move_response = self._game_handler.calculate_move()
        if move_response:
            response = handle_move(move_response)
            logging.info(f"Sent {move_response} after {round(time.time() - start_time, ndigits=3)} seconds.")
            self.send_message_to_room(room_id, response)
        else:
            logging.error(f"{move_response} is not a valid move.")

    def _on_state(self, message):
        last_game_state = None
        for item in self._game_handler.history[-1][::-1]:
            if isinstance(item, GameState):
                last_game_state = item
                break
        if last_game_state:
            _game_state = if_last_game_state(message, last_game_state)
        else:
            _game_state = if_not_last_game_state(message)
        self._game_handler.history[-1].append(_game_state)
        self._game_handler.on_update(_game_state)

    def start(self):
        """
        Starts the client loop.
        """
        self.running = True
        self._client_loop()

    def join(self) -> None:
        """
        Tries to join a game with a connected server. It uses the reservation, or room id to join.
        If their are not present it joins just without, as fallback.
        """
        if self.reservation:
            self.join_game_with_reservation(self.reservation)
        elif self.room_id:
            self.join_game_room(self.room_id)
        else:
            self.join_game()

        self.first_time = False
        self._game_handler.history.append([])

    def _handle_left(self):
        self.first_time = True
        self.disconnect()
        if self.survive:
            logging.info("The server left. Client is in survive mode and keeps running.\n"
                         "Please shutdown the client manually.")
            self._game_handler.while_disconnected(player_client=self)
        if self.auto_reconnect:
            logging.info("The server left. Client tries to reconnect to the server.")
            for _ in range(3):
                logging.info(f"Try to establish a connection with the server...")
                try:
                    self.connect()
                    if self.network_interface.connected:
                        logging.info("Reconnected to server.")
                        break
                except Exception as e:
                    logging.exception(e)
                    logging.info("The client couldn't reconnect due to a previous error.")
                    self.stop()
                time.sleep(1)
            self.join()
            return
        logging.info("The server left.")
        self.stop()

    def _client_loop(self):
        """
        The client loop is the main loop, where the client waits for messages from the server
        and handles them accordingly.
        """
        while self.running:
            if self.network_interface.connected:
                response = self._receive()
                if not response:
                    continue
                elif isinstance(response, ProtocolPacket):
                    logging.debug(f"Received new object: {response}")
                    if isinstance(response, Left):
                        self._game_handler.on_game_left()
                        self._handle_left()
                    else:
                        self._on_object(response)
                    gc.collect()
                elif self.running:
                    logging.error(f"Received a object of unknown class: {response}")
                    raise NotImplementedError("Received object of unknown class.")
            else:
                self._game_handler.while_disconnected(player_client=self)

        logging.info("Done.")
        sys.exit(0)

    def stop(self):
        """
        Disconnects from the server and stops the client loop.
        """
        logging.info("Shutting down...")
        if self.network_interface.connected:
            self.disconnect()
        self.running = False
