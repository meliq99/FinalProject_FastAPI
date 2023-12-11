import time
from utils.redis_connection import redis

# Constants for the leaky bucket
BUCKET_CAPACITY = 10  # Maximum capacity of the bucket
LEAK_RATE = 1  # Leaks per second


async def leaky_bucket(request_id: str) -> bool:
    current_time = time.time()

    # Transaction block to ensure atomicity
    async with redis.pipeline(transaction=True) as pipe:
        # Get the last updated time and the current size of the bucket
        last_updated, bucket_size = await (pipe
                                           .get(f"{request_id}_last_updated")
                                           .get(f"{request_id}_bucket_size")
                                           .execute())

        last_updated = float(last_updated or current_time)
        bucket_size = int(bucket_size or 0)

        # Calculate the leaked amount
        leaked = int((current_time - last_updated) * LEAK_RATE)
        bucket_size = max(0, bucket_size - leaked)

        # Check if a request can be added
        if bucket_size < BUCKET_CAPACITY:
            bucket_size += 1
            # Update the bucket size and last updated time
            await (pipe
                   .set(f"{request_id}_last_updated", current_time)
                   .set(f"{request_id}_bucket_size", bucket_size)
                   .execute())
            return True
        return False



