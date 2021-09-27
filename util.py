log_enabled = True
# 1 = print everything
# 2 = print few stuff
# 3 = print fewer stuff
log_level = 2


def log(message, message_type="info", level=3):
    if not log_enabled:
        return

    log_message_type_symbols = {
        "info": "[*]",
        "warning": "[!]",
        "error": "[x]",
        "success": "[+]",
    }

    # Errors and warnings are logged anyways
    if(message_type == "error" or message_type == "warning"):
        print(log_message_type_symbols[message_type], message)
    else:
        if (level >= log_level):
            print(log_message_type_symbols[message_type], message)
