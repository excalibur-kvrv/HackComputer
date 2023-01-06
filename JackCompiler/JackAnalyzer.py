from CompilationEngine import CompilationEngine
from JackTokenizer import JackTokenizer
from tokens import LexicalElement
import argparse
import os


def output_jack_tokens(token_type: str, token_value: str) -> str:
    return f"<{token_type}> {token_value} </{token_type}>\n"


if __name__ == "__main__":
    """usage:- python3 JackAnalyzer.py <path-to-jack file/directory>

    Generates .vm files with same file names in the location of the .jack files.
    """
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("jack_file", help="Enter path of jack code file", default="")
    args = arg_parse.parse_args()

    jack_file = args.jack_file
    files_to_translate = []

    if os.path.isdir(jack_file):
        if jack_file.endswith(os.path.sep):
            jack_file = jack_file[:-1]
        files_to_translate = [
            os.path.join(jack_file, file)
            for file in os.listdir(jack_file)
            if file.endswith(".jack")
        ]
    elif jack_file.endswith(".jack"):
        files_to_translate.append(jack_file)

    if not os.path.exists(jack_file) or not len(files_to_translate):
        raise ValueError("Enter a valid jack file path or directory")
    
    for file in files_to_translate:
        path, file_name = os.path.split(file)
        tokenizer = JackTokenizer(file)
        
        # Use the below code to test if tokens are getting created correctly
        # tokens_file_path = os.path.join(path, file_name.replace(".jack", "t.xml"))
        # with open(tokens_file_path, "w") as tokens_file:
        #     tokens_file.write("<tokens>\n")
            
        #     while tokenizer.hasMoreTokens():
        #         tokenizer.advance()
        #         token_type = tokenizer.tokenType()
        #         token_str = ""
        #         if token_type == LexicalElement.KEYWORD:
        #             token_str = output_jack_tokens(LexicalElement.KEYWORD.value, tokenizer.keyWord())
        #         elif token_type == LexicalElement.SYMBOL:
        #             token_str = output_jack_tokens(LexicalElement.SYMBOL.value, tokenizer.symbol())
        #         elif token_type == LexicalElement.IDENTIFIER:
        #             token_str = output_jack_tokens(LexicalElement.IDENTIFIER.value, tokenizer.identifier())
        #         elif token_type == LexicalElement.INT_CONST:
        #             token_str = output_jack_tokens(LexicalElement.INT_CONST.value, tokenizer.intVal())
        #         elif token_type == LexicalElement.STRING_CONST:
        #             token_str = output_jack_tokens(LexicalElement.STRING_CONST.value, tokenizer.stringVal())
        #         tokens_file.write(token_str)
            
        #     tokens_file.write("</tokens>\n")
        tokenizer.advance()
        output_file = os.path.join(path, file_name.replace(".jack", "C.xml"))
        compilation_engine = CompilationEngine(tokenizer, output_file)
        compilation_engine.compileClass()