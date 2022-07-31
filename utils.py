import time

from od_downscaler import scaler

ds = scaler.DownScaler(
    include_namespaces=["test-namespace"],
    exclude_namespaces=["kube-system"],
    downscaler_exclude=False,
)
ds.down_scaler()
time.sleep(10)
upscale = scaler.UpScaler(
    include_namespaces=["test-namespace"],
    exclude_namespaces=["kube-system"],
    downscaler_exclude=False,
)
upscale.up_scaler()
