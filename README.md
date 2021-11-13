
# Microservices Orchestration with Python, Faust-Streaming and Kafka (Redpanda)

Example project for PythonBenin meetup. It demonstrates how to use Faust-Streaming to build a microservice using Python and Kafka/Redpanda.

## Installation

This project requires [poetry](https://python-poetry.org/docs/basic-usage/). Once `poetry` is installed, launch the following commands:

```
git clone git@github.com:lerela/orchestration-python-kafka.git
cd orchestration-python-kafka
poetry install
```

We will use [Redpanda](https://vectorized.io/redpanda/) as a replacement for Kafka, but Kafka can also be used. Start a development instance of Redpanda with (do not use this in production!):

```
docker run -d --pull=always --name=redpanda-1 --rm \
  -p 9092:9092 \
  -p 9644:9644 \
  docker.vectorized.io/vectorized/redpanda:latest \
  redpanda start \
  --overprovisioned \
  --smp 1  \
  --memory 1G \
  --reserve-memory 0M \
  --node-id 0 \
  --check=false
```

## Usage

### Start a worker

```
poetry run faust --datadir=worker-1/ -A orchestration worker --without-web -l info
```

The parameter `--datadir` is useful to start multiple workers on the same host (the folder name must be unique for each worker). `--without-web` disables the Faust web interface since we do not need it.

### Send a message on the topic

**Using Faust-Streaming:** `poetry run faust -A orchestration send @topic '{"origin": "Haie Vive", "destination": "Adogleta", "duration": "940"}'`

**Directly using Redpanda** (would work with any Kafka client):
1. Open a producer with: `docker exec -it redpanda-1 rpk topic produce zem-ride --brokers=localhost:9092`
2. Directly send the messages as JSON (press enter to send a message): `{"origin": "Calavi", "destination": "Troisième Pont", "duration": 2560}`

## Troubleshooting

### PartitionsMismatch

If you see the following error:

```
faust.exceptions.PartitionsMismatch: The source topic 'zem-ride' for table 'durations'
has 1 partitions, but the changelog
topic 'zem-app-durations-changelog' has 8 partitions.

Please make sure the topics have the same number of partitions
by configuring Kafka correctly.

```

Then Faust has wrongly created 8 partitions for the durations changelog (the topic that synchronizes the table "durations"). Just delete the topic *while the worker is running* with `docker exec -it redpanda-1 rpk topic delete zem-app-durations-changelog`, and it will be properly re-created. Alternatively, you can delete it when the worker is stopped and manually re-create the topic with `rpk topic create zem-app-durations-changelog -p 1 -r 1`. Of course, increase the partition number if you wish to use multiple workers.

## License

This micro-project is an example of a talk I gave at PythonBenin and is licensed under the MIT License.