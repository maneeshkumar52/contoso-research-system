"""Azure Service Bus publish/subscribe helpers."""
import json
import asyncio
from typing import Callable, Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class ServiceBusHelper:
    """
    Wraps Azure Service Bus operations for reliable message passing.
    Falls back to in-process simulation when LOCAL_MODE is True.
    """

    def __init__(self, connection_string: str, local_mode: bool = False) -> None:
        # If local_mode is True, treat as empty connection string to stay in-process
        self.connection_string = "" if local_mode else connection_string
        self._local_queues: Dict[str, list] = {}

    async def publish(self, queue_name: str, message_dict: Dict[str, Any]) -> str:
        """
        Publish a message to a Service Bus queue.

        Args:
            queue_name: Target queue name.
            message_dict: Message payload to serialize as JSON.

        Returns:
            Message ID.
        """
        message_id = f"msg-{queue_name}-{id(message_dict)}"
        serialized = json.dumps(message_dict)

        if not self.connection_string:
            # Local mode: store in-process
            if queue_name not in self._local_queues:
                self._local_queues[queue_name] = []
            self._local_queues[queue_name].append(message_dict)
            logger.info("service_bus_local_publish", queue=queue_name, message_id=message_id)
            return message_id

        try:
            from azure.servicebus.aio import ServiceBusClient
            async with ServiceBusClient.from_connection_string(self.connection_string) as client:
                async with client.get_queue_sender(queue_name=queue_name) as sender:
                    from azure.servicebus import ServiceBusMessage
                    msg = ServiceBusMessage(serialized)
                    await sender.send_messages(msg)
                    logger.info("service_bus_message_published", queue=queue_name)
            return message_id
        except Exception as exc:
            logger.error("service_bus_publish_failed", error=str(exc), queue=queue_name)
            raise

    async def subscribe(
        self,
        queue_name: str,
        handler_fn: Callable,
        max_wait: int = 180,
    ) -> None:
        """
        Subscribe to a queue and process messages with handler_fn.

        Args:
            queue_name: Queue to consume from.
            handler_fn: Async function to handle each message.
            max_wait: Maximum seconds to wait for messages.
        """
        if not self.connection_string:
            # Local mode: process from in-memory queue
            messages = self._local_queues.get(queue_name, [])
            for message in messages:
                await handler_fn(message)
            self._local_queues[queue_name] = []
            return

        try:
            from azure.servicebus.aio import ServiceBusClient
            async with ServiceBusClient.from_connection_string(self.connection_string) as client:
                async with client.get_queue_receiver(queue_name=queue_name, max_wait_time=max_wait) as receiver:
                    async for msg in receiver:
                        try:
                            data = json.loads(str(msg))
                            await handler_fn(data)
                            await receiver.complete_message(msg)
                        except Exception as exc:
                            logger.error("message_processing_failed", error=str(exc))
                            await receiver.dead_letter_message(msg, reason=str(exc))
        except Exception as exc:
            logger.error("service_bus_subscribe_failed", error=str(exc), queue=queue_name)
