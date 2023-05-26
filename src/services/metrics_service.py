import requests

def send_system_metric(metric_name: str):
    metrics_url = f"http://metrics-queue/api/metrics/system"
    response = requests.post(metrics_url, { "metric_name": metric_name })
    if response.status_code != 202: # Status code accepted
        print(f"Could not send metric {metric_name} to metrics queue")

    
