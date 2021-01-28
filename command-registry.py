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


@attr.s
class Command:
    command = attr.ib()
    id = attr.ib(repr=False)


async def handle_command(command):
    """Simulate handling a command

    Args:
        command (Command): Command that can be acted upon
    """
    # Pretend to do work on the command - we'll add more here!
    await asyncio.sleep(random.random())

    logging.info(f"Completed action for {command.id}")


async def send_command(queue, count):
    """Issue a command

    Args:
        queue (asyncio.Queue): Queue to publish commands to
    """
    count = 0

    while count < 5:
        id = str(uuid.uuid4())
        command = "".join(random.choices(AVAILABLE_COMMANDS, k=4))

        # Create command instance
        command = Command(id=id, command=command)

        # Issue command by adding to the queue and running the task
        asyncio.create_task(queue.put(command))
        logging.info(f"Issued command {command}")

        # Simulate randomness of publishing commands
        await asyncio.sleep(random.random())

        count += 1


async def receive_command(queue):
    """Receive command and create task for handling it

    Args:
        queue (asyncio.Queue): Queue from which to consume commands
    """
    while True:
        command = await queue.get()

        if command:
            logging.info(f"Received {command.id}")
            asyncio.create_task(handle_command(command))


async def _shutdown(loop, signal=None):
    """Finalize outstanding tasks."""
    if signal:
        logging.info(f"Received exit signal {signal.name}...")

    loop.stop()


def main():
    # --------------------------------- Configure command storage ------------------------------- #
    command_queue = asyncio.Queue()

    asyncio.run(send_command(command_queue, 5))
    asyncio.run(receive_command(command_queue))


if __name__ == "__main__":
    main()
