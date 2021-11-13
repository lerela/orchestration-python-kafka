__version__ = "0.1.0"


from collections import defaultdict
from datetime import timedelta
import faust


class ZemRide(faust.Record, validation=True):
    origin: str
    destination: str
    duration: int


app = faust.App("zem-app", broker="aiokafka://127.0.0.1:9092")
topic = app.topic("zem-ride", value_type=ZemRide, value_serializer="json")

# Shared tables
durations = app.Table("durations", default=int).tumbling(
    timedelta(seconds=60), expires=timedelta(seconds=120)
)


@app.agent(topic)
async def ride_ended(rides):
    async for ride in rides:
        durations["count"] += 1
        durations["total"] += ride.duration
        print(
            f"# Ride between {ride.origin} and {ride.destination}, took {ride.duration}s."
        )


def get_average_duration(count, total):
    return total // count if count else 0


@app.timer(interval=10.0)
async def ride_duration_average(app):
    average = get_average_duration(durations["count"].now(), durations["total"].now())
    print(f"\n# 60 seconds average of ride duration: {average}s")


if __name__ == "__main__":
    app.main()
