def kube_scaler_block(namespaces, scale_type):
    value = "****".join(namespaces)
    kube_scale_block = [
        {"type": "section", "text": {"type": "mrkdwn", "text": f"{scale_type}"}},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Do you want to prevent downscaler?"},
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "emoji": True, "text": "yes"},
                    "style": "primary",
                    "value": value,
                    "action_id": "yes",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "emoji": True, "text": "no"},
                    "style": "danger",
                    "value": value,
                    "action_id": "no",
                },
            ],
        },
    ]
    return kube_scale_block


def namespace_block(namespaces, scaler_type="downscaler"):
    options = []
    for namespace in namespaces:
        options.append(
            {
                "text": {"type": "plain_text", "text": f"{namespace}", "emoji": True},
                "value": namespace,
            }
        )
    block = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"{scaler_type} *Cata*"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Select Namespaces To Include"},
            "accessory": {
                "type": "multi_static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select options",
                    "emoji": True,
                },
                "options": options,
                "action_id": "multi_static_select-action",
            },
        },
        {"type": "divider"},
        {"type": "divider"},
    ]
    return block
