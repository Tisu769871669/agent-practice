try:
    import langchain
except ImportError:
    langchain = None


def run(input, context):
    if langchain is not None:
        pass

    return {
        "facts": input["facts"],
        "added_facts": [],
    }
