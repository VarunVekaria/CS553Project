# Smart Load Balancer with Monitoring

This project runs multiple backend servers behind a smart load balancer with observability via Prometheus and Grafana.

## Prerequisites

- Python & Uvicorn
- Prometheus
- Grafana
- Apache Benchmark (`ab`)

---

## Setup Instructions

### 1. Start Backend Servers

Each backend server should run in its own terminal:

```bash
uvicorn backend:app --host 0.0.0.0 --port 8001
uvicorn backend:app --host 0.0.0.0 --port 8002
uvicorn backend:app --host 0.0.0.0 --port 8003
```

### 2. Start Load Balancer

Launch the smart load-balancer in a fourth terminal:

```bash
uvicorn load_balancer:app --host 0.0.0.0 --port 8080 --workers 2
```

### 3. Configure and Start Prometheus

Update `prometheus.yml` with the config provided in this repository. Then run:

```bash
prometheus --config.file=prometheus.yml
```

### 4. Start Grafana

```bash
grafana-server
```

Visit [http://localhost:3000](http://localhost:3000) and:

- Add Prometheus as a data source.
- URL: `http://localhost:9090`

---

## Traffic Generation using Apache Benchmark

### Light Load

```bash
ab -n 1000 -c 10 http://localhost:8080/test
```

### Medium Load

```bash
ab -n 5000 -c 50 http://localhost:8080/test
```

### Heavy Load

```bash
ab -n 20000 -c 200 http://localhost:8080/test
```

Wait ~5 seconds after generating traffic to allow Prometheus to scrape metrics.

---

## Fetch Metrics via Script

```bash
python prometheus_log_exporter.py
```

---

## Visualize Metrics in Grafana

Use PromQL queries to plot:

- **Throughput**
- **Latency**
- **Error rate**
- **Backend distribution**
