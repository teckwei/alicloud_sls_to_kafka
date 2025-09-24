# alicloud_sls_to_kafka demo code

A Python producer pipeline that reads logs from **Alibaba Cloud SLS (Server Log Service)** and publishes them to **Apache Kafka**.

## Features

- Fetch logs from Alibaba Cloud SLS projects and logstores  
- Publish log records into Kafka topics  
- Configurable via environment variables  
- Multi-threaded processing with `ThreadPoolExecutor`  
- Built-in logging and error handling  

---

## Requirements

- Python 3.x  
- Dependencies:
  - [`aliyun-log`](https://pypi.org/project/aliyun-log/) — Alibaba Cloud SLS client SDK  
  - [`confluent-kafka`](https://pypi.org/project/confluent-kafka/) — Kafka producer client  
  - [`python-dotenv`](https://pypi.org/project/python-dotenv/) *(optional, for `.env` file support)*  

---

## Installation

```bash
git clone https://github.com/teckwei/alicloud_sls_to_kafka.git
cd alicloud_sls_to_kafka

# (optional) create virtual environment
python3 -m venv venv
source venv/bin/activate

# install dependencies
pip install aliyun-log confluent-kafka python-dotenv
```

---

## Configuration

The script is configured via environment variables. You can either:

- Export them in your shell  
- Or store them in a `.env` file (if using `python-dotenv`)  

### Required environment variables

| Variable            | Description |
|---------------------|-------------|
| `ENDPOINT`          | SLS endpoint (e.g. `cn-hangzhou.log.aliyuncs.com`) |
| `ACCESS_KEY_ID`     | Alibaba Cloud Access Key ID |
| `ACCESS_KEY_SECRET` | Alibaba Cloud Access Key Secret |
| `PROJECT`           | SLS project name |
| `LOGSTORE`          | SLS logstore name |
| `KAFKA_BROKERS`     | Comma-separated Kafka broker list (e.g. `broker1:9092,broker2:9092`) |
| `KAFKA_TOPIC`       | Kafka topic name |

### Example `.env` file

```env
ENDPOINT=cn-hangzhou.log.aliyuncs.com
ACCESS_KEY_ID=your_ak
ACCESS_KEY_SECRET=your_sk
PROJECT=ali-log-test
LOGSTORE=ali-log-test-store
KAFKA_BROKERS=broker1:9092,broker2:9092,broker3:9092
KAFKA_TOPIC=my-topic
```

---

## Usage

Run with environment variables exported:

```bash
export $(cat .env | xargs)   # if you have a .env file
python sls-kafka.py
```

Or pass variables inline:

```bash
ENDPOINT=cn-hangzhou.log.aliyuncs.com \
ACCESS_KEY_ID=your_ak \
ACCESS_KEY_SECRET=your_sk \
PROJECT=my-proj \
LOGSTORE=my-logstore \
KAFKA_BROKERS="broker1:9092,broker2:9092" \
KAFKA_TOPIC=my-topic \
python sls-kafka.py
```

---

## How It Works

1. Connects to **Alibaba Cloud SLS** using the configured project, logstore, and credentials.  
2. Fetches logs from SLS in batches.  
3. Serializes each log entry into JSON.  
4. Publishes logs to the configured **Kafka topic** using `confluent_kafka.Producer`.  
5. Uses threads (`ThreadPoolExecutor`) for parallel processing and sending.  

---

## Logging & Error Handling

- Uses Python’s built-in `logging` module.  
- Retries on transient errors when sending to Kafka.  
- Logs failures to console for debugging.  

---

## Scaling

- Multi-threaded using `ThreadPoolExecutor`  
- Increase thread count for higher throughput  
- Ensure Kafka cluster can handle the load  

---

## Limitations

- No *exactly-once* delivery guarantee  
- Log ordering is not guaranteed across partitions  
- If Kafka is down, logs may be dropped unless you implement persistence  
