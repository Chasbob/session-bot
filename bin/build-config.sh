#!/bin/bash

export SA_CREDS=$(cat ./credentials.json)
CONFIG=$(envsubst < ./config_template.json)
export CONFIG
