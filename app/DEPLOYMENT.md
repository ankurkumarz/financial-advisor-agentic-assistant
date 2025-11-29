
## Deploy to Cloud Run

- Script is available as `deploy-cloud-run.sh` and here are the instructions to run it:

- set the environment variables

```
export APP_NAME=financial-advisor-agent 
export SERVICE_NAME=financial-advisor-agent
export GOOGLE_CLOUD_REGION=us-central1
export GOOGLE_CLOUD_PROJECT=financial-advisor-agent
```

- create a secret for the google api key

```
echo $GOOGLE_API_KEY | gcloud secrets create GOOGLE_API_KEY --project=GOOGLE_CLOUD_PROJECT --data-file=-
```

- grant access to the compute service account:

```
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY --member="COMPUTE_SERVICE_ACCOUNT" --role="roles secretmanager.secretAccessor" --project="GOOGLE_CLOUD_PROJECT"
```

- run the deploy using **ADK** CLI:

```
adk deploy cloud_run  --project=$GOOGLE_CLOUD_PROJECT --region=$GOOGLE_CLOUD_REGION --app_name=$APP_NAME  --service_name=$SERVICE_NAME --with_ui financial_advisor_agent
```


## Deploy to App Engine

- set the environment variables

- create a secret for the google api key

```
echo $GOOGLE_API_KEY | gcloud secrets create GOOGLE_API_KEY --project=GOOGLE_CLOUD_PROJECT --data-file=-
```

- grant access to the compute service account:

```
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY --member="COMPUTE_SERVICE_ACCOUNT" --role="roles secretmanager.secretAccessor" --project="GOOGLE_CLOUD_PROJECT"
```

- set essential variables

```
export APP_NAME=financial_advisor_agent
export GOOGLE_CLOUD_REGION=us-central1
export GOOGLE_CLOUD_PROJECT=<project_id>
```

- run the deploy using **ADK** CLI:

```
adk deploy agent_engine $APP_NAME --project=$GOOGLE_CLOUD_PROJECT --region=$GOOGLE_CLOUD_REGION --agent_engine_config_file=financial_advisor_agent/.agent_engine_config.json --requirements_file=finacial_advisor_agent/requirements.txt --env_file .env
```

## Reference:

- [Deploy to Cloud Run](https://google.github.io/adk-docs/agents/deploy/cloud_run/)
- [Deploy to App Engine](https://google.github.io/adk-docs/agents/deploy/app_engine/)
