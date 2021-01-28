"""
    Usage:
    $ python command-registry.py

    Simulates a command messaging system where commands are sent, ack/nack is
    received, then subsequent command can be received and mapped back to the
    original command

    Assumptions
    - We are only sending a single command at a time until we have received the ack/nack
    - Incoming commands may be associated with a previous command or may be the ack/nack
"""

import asyncio
import attr
import logging
import random
import signal
import string
import uuid

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
)

AVAILABLE_COMMANDS = string.ascii_lowercase + string.digits
ISSUED_COMMANDS = {}


@attr.s
class Command:
    command = attr.ib()
    id = attr.ib()
    acked = attr.ib(default=attr.Factory(asyncio.Event))
    retry_count = attr.ib(repr=False, default=0)


async def store_command_result(command):
    logging.info(f"Information received for {command.id}")
    ISSUED_COMMANDS[command.id] = "fake data"


async def handle_command_response(command):
    """Simulate handling a command

    Args:
        command (Command): Command that can be acted upon
    """
    # Store command response data
    asyncio.create_task(store_command_result(command))

    # Execute the task in response to the command, still simulated as arbitrary
    # work
    await asyncio.sleep(random.random())

    logging.info(f"Completed action for {command.id}")


def execute_command(queue, command):
    logging.info(f"Executing command {command}, awaiting ack...")

    # Issue command by adding to the queue and running the task
    asyncio.create_task(queue.put(command))

    return asyncio.wait_for(command.acked.wait(), 4)


async def send_command(queue):
    """Issue a command

    Args:
        queue (asyncio.Queue): Queue to publish commands to
    """

    while True:
        # Simulate a command ID and a command action
        id = str(uuid.uuid4())
        command = "".join(random.choices(AVAILABLE_COMMANDS, k=4))

        # Create command instance
        command = Command(id=id, command=command)

        # Wait until the command is marked as acked or times out, we don't want
        # to send multiple commands to the external system until we know it's
        # been received
        for retries_remaining in range(2, -1, -1):
            try:
                await execute_command(queue, command)

                logging.info(f"Received {command.id} - acked")
                asyncio.create_task(handle_command_response(command))
                break
            # TODO: handle exceptions!
            except:
                logging.info(f"Received {command.id} - nacked. Something went wrong.")

            if retries_remaining > 0:
                logging.warning(f"Command {command.id} -  {retries_remaining} retries remaining.")
            else:
                logging.error(f"Command {command.id} -  {retries_remaining} retries exhausted.")

        # Simulate randomness of publishing commands
        await asyncio.sleep(random.random())


async def receive_command(queue):
    """Receive command and create task for handling it

    Args:
        queue (asyncio.Queue): Queue from which to consume commands
    """
    while True:
        command = await queue.get()

        # Simulate ack/nack status from the external system
        if bool(random.getrandbits(1)) is True:
            command.acked.set()


def _handle_exception(loop, context):
    """Handle exceptions

    Args:
        loop(asyncio.loop): Current event loop
        context(dict): Information about the exception including:
        - ‘message’: Error message
        - ‘exception’ (optional): Exception object
        - ‘future’ (optional): asyncio.Future instance
        - ‘handle’ (optional): asyncio.Handle instance
        - ‘protocol’ (optional): Protocol instance
        - ‘transport’ (optional): Transport instance
        - ‘socket’ (optional): socket.socket instance
    """
    # Fallback to context["message"] if context["exception"] does not exist
    msg = context.get("exception", context["message"])
    logging.error(f"Caught exception: {msg}")

    # TODO: decide how to handle specific exceptions!

    logging.info("Shutting down...")
    asyncio.create_task(_shutdown(loop))


async def _shutdown(loop, signal=None):
    """Finalize outstanding tasks."""
    if signal:
        logging.info(f"Received exit signal {signal.name}...")

    loop.stop()


def main():
    # ---------------------------- Configure loop and command storage --------------------------- #
    loop = asyncio.get_event_loop()
    command_queue = asyncio.Queue()

    # -------------------------------- Configure signal handlers -------------------------------- #
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(s, lambda s=s: asyncio.create_task(_shutdown(loop, signal=s)))

    # ------------------------------- Configure exception handler -------------------------------- #
    loop.set_exception_handler(_handle_exception)

    # ------------------------------ Run loops and handle shutdown ------------------------------ #
    try:
        loop.create_task(send_command(command_queue))
        loop.create_task(receive_command(command_queue))
        loop.run_forever()
    except RuntimeError as e:
        logging.error("RUNTIME ERROR", e)
    finally:
        logging.info("Machine has been shutdown. Program exiting.")


if __name__ == "__main__":
    main()
