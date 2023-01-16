from CompilationEngine import CompilationEngine
from JackTokenizer import JackTokenizer
from VMWriter import VMWriter
import argparse
import os


def output_jack_tokens(token_type: str, token_value: str) -> str:
    return f"<{token_type}> {token_value} </{token_type}>\n"


if __name__ == "__main__":
    """usage:- python3 JackCompiler.py <path-to-jack file/directory>

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
        tokenizer.advance()
        
        output_file = os.path.join(path, file_name.replace(".jack", ".vm"))
        vm_writer = VMWriter(output_file)
        
        compilation_engine = CompilationEngine(tokenizer, vm_writer)
        compilation_engine.compileClass()
