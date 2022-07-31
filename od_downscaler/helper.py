from kubernetes import client as KubeClient
from kubernetes import config


def load_kubeconfig():
    try:
        config.load_kube_config()
    except config.ConfigException:
        config.load_incluster_config()


def get_all_namespaces():
    load_kubeconfig()
    kube_client = KubeClient.CoreV1Api()
    namespaces_list = kube_client.list_namespace()
    namespaces = [item.metadata.name for item in namespaces_list.items]
    return namespaces
