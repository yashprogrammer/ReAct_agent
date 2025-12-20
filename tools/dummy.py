from langchain.tools import tool

@tool("uppercase_tool", description="Converts input text to uppercase")
def dummy_tool(inputText:str)-> str:
    """Convert input text to uppercase. This is just for testing.
     Arguments:
        inputText {str} -- input text to be converted to uppercase
    """
    return f"Output : {inputText.upper()}"
