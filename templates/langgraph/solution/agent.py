try:
    import langgraph
except ImportError:
    langgraph = None


def run(input, context):
    if langgraph is not None:
        pass

    return {
        "facts": input["facts"],
        "added_facts": [],
    }
