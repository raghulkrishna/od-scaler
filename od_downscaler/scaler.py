from shutil import ExecError
from kubernetes import client as KubeClient
import logging
import os

from od_downscaler.helper import get_all_namespaces, load_kubeconfig


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")

file_handler = logging.FileHandler("log.log")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

REPLICA_ANNOTATATIONS = "od.downscaler/original-replicas"
CRON_JOB_ANNOTATIONS = "od.downscaler/suspended"
RESOURCES = ["Deployment", "StatefulSet", "CronJob"]
SKIP_ANNOTATION = "od.downscaler/exclude"
DOWNSCALER_EXCLUDE_ANNOTATION = "downscaler/exclude"


class DownScaler:
    def __init__(self, include_namespaces: list, exclude_namespaces: list, **kwargs):
        logger.info("Downscaler initialized")
        if "all_namespaces" in kwargs:
            if kwargs["all_namespaces"]:
                all_namespaces = get_all_namespaces()
                self.include_namespaces = all_namespaces
        else:
            self.include_namespaces = include_namespaces
        self.exclude_namespaces = exclude_namespaces
        if "downscaler_exclude" in kwargs:
            self.downscaler_exclude = kwargs["downscaler_exclude"]
        if "min_replica" in kwargs:
            self.min_replica = kwargs["min_replica"]
        else:
            self.min_replica = 0

    def down_scaler(self):
        for namespace in self.include_namespaces:
            if namespace in self.exclude_namespaces:
                pass
            else:
                self.downscale_deployments(namespace)
                self.downscale_stateful_set(namespace)
                self.down_scale_cronjobs(namespace)

    def resource_downscaler(self, resources, kube_client, resource_type, namespace):
        for resource in resources.items:
            if SKIP_ANNOTATION in resource.metadata.annotations:
                if resource.metadata.annotations[SKIP_ANNOTATION]:
                    print("skip")
            else:
                name = resource.metadata.name
                if self.downscaler_exclude:
                    logger.info(f"exclude downscale {name} {self.downscaler_exclude}")
                    # print(resource.metadata.annotations)
                    resource.metadata.annotations.update(
                        {DOWNSCALER_EXCLUDE_ANNOTATION: "true"}
                    )
                else:
                    if DOWNSCALER_EXCLUDE_ANNOTATION in resource.metadata.annotations:
                        resource.metadata.annotations.pop(DOWNSCALER_EXCLUDE_ANNOTATION)
                if resource_type != "CronJob":
                    original_replica = resource.spec.replicas
                    logger.info(self.min_replica)
                    resource.spec.replicas = self.min_replica
                    resource.metadata.annotations.update(
                        {REPLICA_ANNOTATATIONS: str(original_replica)}
                    )
                    if resource_type == "Deployment":
                        try:
                            kube_client.patch_namespaced_deployment(
                                name=name, namespace=namespace, body=resource
                            )
                        except Exception as e:
                            logger.error(e)
                    if resource_type == "StatefulSet":
                        try:
                            kube_client.patch_namespaced_stateful_set(
                                name=name, namespace=namespace, body=resource
                            )
                        except Exception as e:
                            logger.error(e)
                else:
                    if not resource.spec.suspend:
                        resource.spec.suspend = True
                        resource.metadata.annotations.update(
                            {CRON_JOB_ANNOTATIONS: "true"}
                        )
                        try:
                            kube_client.patch_namespaced_cron_job(
                                name=name,
                                namespace=namespace,
                                body=resource,
                                field_manager="MergePatch",
                            )
                        except Exception as e:
                            logger.error(e)

    def downscale_deployments(self, namespace):
        load_kubeconfig()
        kube_client = KubeClient.AppsV1Api()
        logger.info(f"downscale deployment {namespace}")
        deployments = kube_client.list_namespaced_deployment(namespace)
        self.resource_downscaler(
            deployments, kube_client, resource_type="Deployment", namespace=namespace
        )

    def downscale_stateful_set(self, namespace):
        load_kubeconfig()
        kube_client = KubeClient.AppsV1Api()
        logger.info(f"downscale statefulset {namespace}")
        statefulsets = kube_client.list_namespaced_stateful_set(namespace)
        self.resource_downscaler(
            statefulsets, kube_client, resource_type="StatefulSet", namespace=namespace
        )

    def down_scale_cronjobs(self, namespace):
        load_kubeconfig()
        kube_client = KubeClient.BatchV1beta1Api()
        logger.info(f"downscale cronjob {namespace}")
        cron_jobs = kube_client.list_namespaced_cron_job(namespace=namespace)
        self.resource_downscaler(
            cron_jobs, kube_client, resource_type="CronJob", namespace=namespace
        )


class UpScaler:
    def __init__(self, include_namespaces: list, exclude_namespaces: list, **kwargs):
        if "all_namespaces" in kwargs:
            if kwargs["all_namespaces"]:
                all_namespaces = get_all_namespaces()
                self.include_namespaces = all_namespaces
        else:
            self.include_namespaces = include_namespaces
        self.exclude_namespaces = exclude_namespaces
        if "downscaler_exclude" in kwargs:
            self.downscaler_exclude = kwargs["downscaler_exclude"]

    def up_scaler(self):
        for namespace in self.include_namespaces:
            if namespace in self.exclude_namespaces:
                pass
            else:
                self.upscale_deployments(namespace)
                self.upscale_stateful_set(namespace)
                self.upscale_cronjobs(namespace)

    def resource_upscaler(self, resources, kube_client, resource_type, namespace):
        for resource in resources.items:

            if SKIP_ANNOTATION in resource.metadata.annotations:
                if resource.metadata.annotations[SKIP_ANNOTATION]:
                    pass
            else:
                name = resource.metadata.name
                if self.downscaler_exclude:
                    
                    resource.metadata.annotations.update(
                        {DOWNSCALER_EXCLUDE_ANNOTATION: "true"}
                    )
                else:
                    if DOWNSCALER_EXCLUDE_ANNOTATION in resource.metadata.annotations:
                        resource.metadata.annotations.pop(DOWNSCALER_EXCLUDE_ANNOTATION)

                if resource_type != "CronJob":
                    if REPLICA_ANNOTATATIONS in resource.metadata.annotations.keys():
                        resource.spec.replicas = int(
                            resource.metadata.annotations[REPLICA_ANNOTATATIONS]
                        )
                        resource.metadata.annotations.pop(REPLICA_ANNOTATATIONS)
                        if resource_type == "Deployment":
                            try:
                                kube_client.replace_namespaced_deployment(
                                    name=name, namespace=namespace, body=resource
                                )
                            except Exception as e:
                                logger.error(e)
                        if resource_type == "StatefulSet":
                            try:
                                kube_client.patch_namespaced_stateful_set(
                                    name=name, namespace=namespace, body=resource
                                )
                            except Exception as e:
                                logger.error(e)
                else:
                    if CRON_JOB_ANNOTATIONS in resource.metadata.annotations.keys():
                        resource.spec.suspend = False
                        resource.metadata.annotations.pop(CRON_JOB_ANNOTATIONS)
                        kube_client.replace_namespaced_cron_job(
                            name=name, namespace=namespace, body=resource
                        )

    def upscale_deployments(self, namespace):
        load_kubeconfig()
        kube_client = KubeClient.AppsV1Api()
        logger.info(f"upscale Deployment {namespace}")
        deployments = kube_client.list_namespaced_deployment(namespace)
        self.resource_upscaler(
            deployments, kube_client, resource_type="Deployment", namespace=namespace
        )

    def upscale_stateful_set(self, namespace):
        load_kubeconfig()
        kube_client = KubeClient.AppsV1Api()
        logger.info(f"upscale StatefulSet {namespace}")
        statefulsets = kube_client.list_namespaced_stateful_set(namespace)
        self.resource_upscaler(
            statefulsets, kube_client, resource_type="StatefulSet", namespace=namespace
        )

    def upscale_cronjobs(self, namespace):
        load_kubeconfig()
        kube_client = KubeClient.BatchV1beta1Api()
        logger.info(f"upscale CronJob {namespace}")
        cron_jobs = kube_client.list_namespaced_cron_job(namespace=namespace)
        self.resource_upscaler(
            cron_jobs, kube_client, resource_type="CronJob", namespace=namespace
        )
