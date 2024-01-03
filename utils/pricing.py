def calculate_cost_fixed(model, input_tokens, output_tokens):
    # Fixed pricing data
    pricing_data = {
        "gpt-4-1106-preview": {"input_cost": 0.01, "output_cost": 0.03},
        "gpt-4-1106-vision-preview": {"input_cost": 0.01, "output_cost": 0.03},
        "gpt-4": {"input_cost": 0.03, "output_cost": 0.06},
        "gpt-4-32k": {"input_cost": 0.06, "output_cost": 0.12},
        "gpt-3.5-turbo-1106": {"input_cost": 0.0010, "output_cost": 0.0020},
        "gpt-3.5-turbo": {"input_cost": 0.0010, "output_cost": 0.0020},
        "text-embedding-ada-002": {"input_cost": 0.00010, "output_cost": 0},
        "gpt-3.5-turbo-instruct": {"input_cost": 0.0015, "output_cost": 0.0020}        
    }

    # Check if the model is in the pricing data
    if model not in pricing_data:
        return "Model not found in the pricing data."

    # Retrieving costs for the model
    model_costs = pricing_data[model]
    input_cost_per_1000 = model_costs["input_cost"]
    output_cost_per_1000 = model_costs["output_cost"]

    # Calculating total cost
    total_cost = (input_cost_per_1000 * (input_tokens / 1000)) + (output_cost_per_1000 * (output_tokens / 1000))
    return total_cost


