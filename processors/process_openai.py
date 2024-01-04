import streamlit as st
from openai import OpenAI
import dotenv
import os
from uuid import uuid4
import uuid
import boto3
import json
from utils.pricing import calculate_cost_fixed





def call_azure_openai (model_name, query):
    print ("In call_azure_openai")
    from langchain.chat_models import AzureChatOpenAI
    from langchain.schema import (
        SystemMessage,
        HumanMessage,
        AIMessage
    )
    
    azuremessages = [
        SystemMessage(content = "You are a helpful assistant")
    ]
    openai_temperature = 0.7
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_API_BASE = os.getenv('AZURE_OPENAI_API_BASE')
    AZURE_OPENAI_API_VERSION_GPT432K = os.getenv('AZURE_OPENAI_API_VERSION_GPT432K')
    AZURE_OPENAI_API_TYPE = os.getenv('AZURE_OPENAI_API_TYPE')
    AZURE_EMBEDDING_MODEL_DEPLOYMENT = os.getenv('AZURE_EMBEDDING_MODEL_DEPLOYMENT')
    
    azurellm = AzureChatOpenAI(
        api_version = AZURE_OPENAI_API_VERSION_GPT432K,
        openai_api_key = AZURE_OPENAI_API_KEY,
        model_name = model_name,
        azure_endpoint = AZURE_OPENAI_API_BASE,
        openai_api_type = AZURE_OPENAI_API_TYPE,
        temperature = openai_temperature,
        
    )
    azuremessages.append (
        HumanMessage(
            content=query
        )
    )
    res = azurellm (azuremessages)
    print ("From Azure...")
    print (res)
    return res
    
def call_openai_azure_core(deployment_name, version, max_token, query):    
    print('call_openai_azure_core', deployment_name)
    import os
    
    from openai import AzureOpenAI
    
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
        api_version=version,
        azure_endpoint = os.getenv("AZURE_OPENAI_API_BASE")
    )
    
    # deployment_name= model_name #This will correspond to the custom name you chose for your deployment when you deployed a model. 
    
    # Send a completion call to generate an answer
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": query},

    ]
   
    response = client.chat.completions.create(
        model=deployment_name, 
        messages=messages, 
        max_tokens=max_token
        )
    print (response)

    return response 

def call_openai(user_name_logged, user_input, model_name, messages, BU_choice):
    print ("In call_openai")
    
    # call_azure_openai ("gpt432k", "what is the captal of France")
    # azure_query = 'Write a tagline for an ice cream shop.' 
    # azureopenai_response = call_openai_azure_core("gpt35turbo", "2023-07-01-preview", 20, azure_query)

    dotenv.load_dotenv(".env")
    env_vars = dotenv.dotenv_values()
    for key in env_vars:
        os.environ[key] = env_vars[key]
        
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_ORGANIZATION = os.getenv('OPENAI_ORGANIZATION')
    client = OpenAI(organization = OPENAI_ORGANIZATION, api_key = OPENAI_API_KEY)
    
    openai_response = client.chat.completions.create(
        model=model_name,     
        messages=messages
    )

    
    # Extracting the message content
    message_content = openai_response.choices[0].message.content
    print(message_content)
    st.session_state.messages.append({"role": "assistant", "content": message_content})


    # Extracting token usage information
    input_tokens = openai_response.usage.prompt_tokens
    output_tokens = openai_response.usage.completion_tokens
    total_tokens = openai_response.usage.total_tokens
    cost  = calculate_cost_fixed (model_name, input_tokens, output_tokens)
    

 
    
    random_string = str(uuid.uuid4())
    promptId_random = "prompt-" + random_string 
    
        
    data = {    
        "userName": user_name_logged,
        "promptName": promptId_random,
        "prompt": user_input,
        "completion": message_content,
        "summary": "No Summary",
        "inputTokens": input_tokens,
        "outputTokens": output_tokens,
        "cost": cost,
        "feedback": "",
        "domain": BU_choice
    }

    # st.session_state['current_user'] = user_name_logged
    # st.session_state['curent_promptName'] = promptId_random

    # Invoke the Lambda function
    PROMPT_INSERT_LAMBDA = os.getenv('PROMPT_INSERT_LAMBDA')
    lambda_function_name = PROMPT_INSERT_LAMBDA
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_DEFAULT_REGION')
    lambda_client = boto3.client('lambda', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)
    lambda_response = lambda_client.invoke(
        FunctionName=lambda_function_name,
        InvocationType='RequestResponse',  # Use 'Event' for asynchronous invocation
        Payload=json.dumps(data)
    )
    if lambda_response['StatusCode'] != 200:
        raise Exception(f"AWS Lambda invocation failed with status code: {lambda_response['StatusCode']}")
    else:
        print ("Success calling lambda!")
        st.session_state['current_promptName'] = promptId_random
    print("Total Tokens:", total_tokens)     
    return message_content, input_tokens, output_tokens, total_tokens, cost
# st.sidebar.write(f"**Usage Info:** ")
# st.sidebar.write(f"**Model:** {model_name}")
# st.sidebar.write(f"**Input Tokens:** {input_tokens}")
# st.sidebar.write(f"**Output Tokens:** {output_tokens}")
# st.sidebar.write(f"**Cost($):** {cost}")