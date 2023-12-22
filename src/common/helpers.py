def validation_error_handler(data):
    # We can have errors in multiple keys, get the first key
    key = list(data.keys())[0]
    value = data[key]

    # We can have multiple erros related to single field
    if type(value) == list:
        message = f"{key}: {value[0]}"
    else:
        message = f"{key}: {value}"
    
    return message