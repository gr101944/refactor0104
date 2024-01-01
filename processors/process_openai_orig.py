import streamlit as st
from openai import OpenAI
import dotenv
import os
from uuid import uuid4
import uuid
import boto3
import json

def send_email(recipient):
    print ("sending email to ", recipient)

def run_email_function():
    print ("run_email_function ")

    dotenv.load_dotenv(".env")
    env_vars = dotenv.dotenv_values()
    for key in env_vars:
        os.environ[key] = env_vars[key]
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_ORGANIZATION = os.getenv('OPENAI_ORGANIZATION')
    client = OpenAI(organization = OPENAI_ORGANIZATION, api_key = OPENAI_API_KEY) 
    # Step 1: send the conversation and available functions to the model
    messages = [{"role": "user", "content": "What's the weather like in San Francisco, Tokyo, and Paris?"}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "send_email",
                "description": "send email to a recipient",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipient": {
                            "type": "string",
                            "description": "The recipient of the email"
                        }
                    },
                    "required": ["recipient"]
                }
            }
        }

    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "send_email": send_email,
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                recipient=function_args.get("recipient")
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response

def call_openai(user_name_logged, user_input, model_name, messages, BU_choice):
    print ("In call_openai ")

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

    # Extracting token usage information
    input_tokens = openai_response.usage.prompt_tokens
    output_tokens = openai_response.usage.completion_tokens
    total_tokens = openai_response.usage.total_tokens
    cost = 0.0
    
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

    st.session_state['current_user'] = user_name_logged
    st.session_state['current_promptName'] = promptId_random
    print ("****************st.session_state['current_promptName']**********************")
    print (st.session_state['current_promptName'])

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
    print("Total Tokens:", total_tokens)     
    return message_content, input_tokens, output_tokens, total_tokens, cost
