import os

worker_domain = os.getenv("WORKER_DOMAIN")
worker_username = os.getenv("WORKER_USERNAME")
worker_password = os.getenv("WORKER_PASSWORD")
if worker_domain is None or worker_username is None or worker_password is None:
    raise Exception("No WORKER_DOMAIN, WORKER_USERNAME or WORKER_PASSWORD")

worker_base_url = f"https://{worker_domain}"
worker_base_url_with_auth = (
    f"https://{worker_username}:{worker_password}@{worker_domain}"
)
