import sys
from StateMachine import StateMachine, Token
from dataclasses import dataclass
from typing import Any
from collections.abc import Callable

def add_to_scheme(first: str | None, second: str | None = "", third: str | None = "") -> Callable[[StateMachine, Token], None]:
    def add(sm: StateMachine, token: Token) -> None:
        begin = first 
        middle = second
        end = third
        if (begin == None):
            begin = token.object
        if (middle == None):
            middle = token.object
        if (end == None):
            end = token.object
        sm.set_var("scheme", sm.get_var("scheme") + begin + middle + end)
    return add

CLASS = Token("Class")
DATACLASS = Token("Dataclass")
ENUM = Token("Enum")
PUBLIC = Token("Visibility", "+")
PRIVATE = Token("Visibility", "-")
PROTECTED = Token("Visibility", "#")
ATTRIBUTE = Token("Attribute")
INIT = Token("Init")
METHOD = Token("Method")
NameToken = lambda a : Token("Name", a)
TypeToken = lambda a : Token("Type", a)
END = Token("End")

MermaidStateMachine = StateMachine("Empty")
MermaidStateMachine.set_var("scheme", "")
MermaidStateMachine.add_state("Class")
MermaidStateMachine.add_state("Dataclass")
MermaidStateMachine.add_state("Enum")
MermaidStateMachine.add_state("Body")
MermaidStateMachine.add_state("Visibility")
MermaidStateMachine.add_state("Field_name")
MermaidStateMachine.add_state("Attribute")
MermaidStateMachine.add_state("Method")
MermaidStateMachine.add_state("Method_with_params")
MermaidStateMachine.add_state("Method_param")

MermaidStateMachine.add_transition("Empty", "Class", "Class", add_to_scheme("class"))
MermaidStateMachine.add_transition("Empty", "Dataclass", "Dataclass", add_to_scheme("class"))
MermaidStateMachine.add_transition("Empty", "Enum", "Enum", add_to_scheme("class"))
MermaidStateMachine.add_transition("Class", "Body", "Name", add_to_scheme(" ", None, " {\n"))
MermaidStateMachine.add_transition("Dataclass", "Body", "Name", add_to_scheme(" ", None, " {\n\t<<dataclass>>\n"))
MermaidStateMachine.add_transition("Enum", "Body", "Name", add_to_scheme(" ", None, " {\n\t<<enum>>\n"))

MermaidStateMachine.add_transition("Body", "Empty", "End", add_to_scheme("}\n"))
MermaidStateMachine.add_transition("Body", "Body", "Name", add_to_scheme("\t", None, "\n"))
MermaidStateMachine.add_transition("Body", "Visibility", "Visibility", add_to_scheme("\t", None))
MermaidStateMachine.add_transition("Visibility", "Field_name", "Name", add_to_scheme(None))

MermaidStateMachine.add_transition("Field_name", "Attribute", "Attribute", add_to_scheme(":"))
MermaidStateMachine.add_transition("Attribute", "Body", "Type", add_to_scheme(" ", None, "\n"))

MermaidStateMachine.add_transition("Field_name", "Method", "Method", add_to_scheme("("))
MermaidStateMachine.add_transition("Method", "Method_param", "Name", add_to_scheme(None))
MermaidStateMachine.add_transition("Method", "Body", "Type", add_to_scheme(") ", None, "\n"))
MermaidStateMachine.add_transition("Method_param", "Method_with_params", "Type", add_to_scheme(": ", None))
MermaidStateMachine.add_transition("Method_with_params", "Method_param", "Name", add_to_scheme(", ", None))
MermaidStateMachine.add_transition("Method_with_params", "Body", "Type", add_to_scheme(") ", None, "\n"))

def ignore(sm, token):
    pass

def pass_token(sm: StateNachine, token: Token):
    mermaid: StateMachine = sm.get_var("SM")
    mermaid.enter_token(token)

def enter_add(add_token: Token):
    def enter(sm: StateMachine, token: Token):
        pass_token(sm, add_token)
        pass_token(sm, token)
    return enter

Parser = StateMachine("Empty")
Parser.set_var("SM", MermaidStateMachine)

Parser.add_state("Class")
Parser.add_state("Enum")
Parser.add_state("Dataclass")
Parser.add_state("Body")
Parser.add_state("Attr")
Parser.add_state("Attr_vis")
Parser.add_state("Attr_name")
Parser.add_state("Method")
Parser.add_state("Method_vis")
Parser.add_state("Method_name")
Parser.add_state("Method_param")
Parser.add_state("Method_with_params")

Parser.add_transition("Empty", "Class", "Class", ignore)
Parser.add_transition("Empty", "Dataclass", "Dataclass", ignore)
Parser.add_transition("Class", "Enum", "Enum", ignore)
Parser.add_transition("Class", "Body", "Name", enter_add(CLASS))
Parser.add_transition("Dataclass", "Dataclass", "Class", ignore)
Parser.add_transition("Dataclass", "Body", "Name", enter_add(DATACLASS))
Parser.add_transition("Enum", "Body", "Name", enter_add(ENUM))
Parser.add_transition("Body", "Empty", "End", pass_token)

Parser.add_transition("Body", "Attr", "Attribute", ignore)
Parser.add_transition("Attr", "Body", "Name", pass_token)
Parser.add_transition("Attr", "Attr", "Method", ignore)
Parser.add_transition("Attr", "Attr_vis", "Visibility", pass_token)
Parser.add_transition("Attr_vis", "Attr_name", "Name", pass_token)
Parser.add_transition("Attr_name", "Body", "Type", enter_add(ATTRIBUTE))

Parser.add_transition("Body", "Method", "Method", ignore)
Parser.add_transition("Method", "Body", "Init", ignore)
Parser.add_transition("Method", "Method_vis", "Visibility", pass_token)
Parser.add_transition("Method_vis", "Method_name", "Name", pass_token)
Parser.add_transition("Method_name", "Body", "Type", enter_add(METHOD))
Parser.add_transition("Method_name", "Method_param", "Name", enter_add(METHOD))
Parser.add_transition("Method_param", "Method_with_params", "Type", pass_token)
Parser.add_transition("Method_with_params", "Method_param", "Name", pass_token)
Parser.add_transition("Method_with_params", "Body", "Type", pass_token)

for i in range(1, len(sys.argv)):
    with open(sys.argv[i]) as file:
        class_fold: int = 0
        in_init: int = False
        in_class: bool = False
        is_dataclass: bool = False
        in_enum: bool = False
        is_property: bool = False
        for file_line in file:
            fold_level: int = file_line.count("    ")
            line: str = file_line.strip()
            if (line != "" and in_class and fold_level < class_fold):
                in_enum = False
                in_class = False
                is_dataclass = False
                class_fold = 0
                Parser.enter_token(END)
            if (line.startswith("@")):
                line = line.removeprefix("@")
                match (line):
                    case "dataclass":
                        if (fold_level == 0):
                            Parser.enter_token(DATACLASS)
                            is_dataclass = True
                    case "property":
                        if (fold_level == class_fold):
                            Parser.enter_token(ATTRIBUTE)
                            is_property = True
            elif (line.startswith("class ") and fold_level == 0):
                in_class = True
                class_fold = fold_level + 1
                Parser.enter_token(CLASS)
                in_init: bool = False
                line = line.removeprefix("class ")
                line = line.removesuffix(":")
                par_pos: int = line.find("(")
                extension: str = ""
                if (par_pos != -1):
                    extension = line[par_pos:]
                    line = line.removesuffix(extension)
                if (extension.find("Enum") != -1):
                    Parser.enter_token(ENUM)
                    in_enum = True
                Parser.enter_token(NameToken(line))
            elif (line.startswith("def ")):
                if (fold_level == class_fold and in_class):
                    Parser.enter_token(METHOD)
                    line = line.removeprefix("def ")
                    line = line.removesuffix(":")
                    return_type: str = line[line.find("-> ") + 3:]
                    line = line.removesuffix(" -> " + return_type)
                    params: str = line[line.find("("):]
                    line = line.removesuffix(params)
                    if (line != "__init__"):
                        in_init: bool = False
                        visibility: Token = PUBLIC
                        if (line.startswith("__")):
                            visibility = PRIVATE
                            line = line.removeprefix("__")
                        elif (line.startswith("_")):
                            visibility = PROTECTED
                            line = line.removeprefix("_")
                        Parser.enter_token(visibility)
                        if (is_property):
                            line = "/" + line
                            is_property = False
                        Parser.enter_token(NameToken(line))
                        params = params.removeprefix("(")
                        params = params.removesuffix(")")
                        params = params.replace(":", "")
                        params = params.replace(" | ", ".|.")
                        next_comma: int = params.find(',')
                        while next_comma != -1:
                            before = params[:next_comma]
                            open_brackets = before.count("[")
                            closed_brackets = before.count("]")
                            if (open_brackets == closed_brackets):
                                params = params[:next_comma] + params[next_comma+1:]
                            next_comma = params.find(",", next_comma + 1)
                        params = params.replace(", ", ",.")
                        params = params.removeprefix("self")
                        params = params.removeprefix("cls")
                        params = params.strip()
                        if (params != ""):
                            param_list: list[str] = params.split(" ")
                            for i in range(0, len(param_list), 2):
                                Parser.enter_token(NameToken(param_list[i]))
                                Parser.enter_token(TypeToken(param_list[i + 1].replace(".|.", " | ").replace(",.", ", ")))
                        Parser.enter_token(TypeToken(return_type))
                    else:
                        in_init: bool = True
                        Parser.enter_token(INIT)
            elif ((line.find(": ") != -1 or in_enum) and (line.find(" = ") != -1 or is_dataclass) and (fold_level == class_fold or (in_init and line.startswith("self.")))):
                Parser.enter_token(ATTRIBUTE)
                if (not in_enum):
                    line = line.removeprefix("self.")
                    visibility: Token = PUBLIC
                    if (line.startswith("__")):
                        visibility = PRIVATE
                        line = line.removeprefix("__")
                    elif (line.startswith("_")):
                        visibility = PROTECTED
                        line = line.removeprefix("_")
                    Parser.enter_token(visibility)
                    if (line.find(" = ") != -1):
                        line = line[:line.find(" = ")]
                    line = line.replace(":", "")
                    attr_type: str = line[line.find(" ") + 1:]
                    line = line.removesuffix(" " + attr_type)
                    Parser.enter_token(NameToken(line))
                    Parser.enter_token(TypeToken(attr_type))
                else:
                    line = line[:line.find(" ")]
                    Parser.enter_token(NameToken(line))
    Parser.enter_token(END)
print(Parser.get_var("SM").get_var("scheme"))
