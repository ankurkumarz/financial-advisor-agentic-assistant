export APP_NAME=financial-advisor-agent 
export SERVICE_NAME=financial-advisor-agent 
adk deploy cloud_run  --project=$GOOGLE_CLOUD_PROJECT --region=$GOOGLE_CLOUD_REGION --app_name=$APP_NAME  --service_name=$SERVICE_NAME --with_ui financial_advisor_agent