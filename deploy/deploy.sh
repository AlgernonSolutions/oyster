#!/usr/bin/env bash
sam build \
    --debug \
    --profile dev \
    --use-container \
    --template deploy/template.yaml \
    --manifest deploy/requirements.txt
