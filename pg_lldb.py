import lldb


def __lldb_init_module(debugger, _):
    lldb.formatters.Logger._lldb_formatters_debug_level = 2
    lldb.formatters.Logger._lldb_formatters_debug_filename = "/tmp/pg_lldb.log"

    res = lldb.SBCommandReturnObject()
    ci = debugger.GetCommandInterpreter()
    ci.HandleCommand("command script add -h 'print node' -C variable-path -f pg_lldb.cmd_pnode pnode", res)

    # debugger.HandleCommand("type summary add Node -F pg_lldb.pprint_node -w postgres")
    debugger.HandleCommand("type summary add --recognizer-function pg_lldb.is_node -p -F pg_lldb.pprint_node -w postgres")

    debugger.HandleCommand("type category enable postgres")


def is_node(sbtype, internal_dict):
    if len(sbtype.members) < 1:
        return False
    return sbtype.members[0].type.name == 'NodeTag'


def cmd_pnode(debugger, node_variable, result, dict):
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    frame = process.GetSelectedThread().GetSelectedFrame()
    # Get the node variable
    node_pointer = frame.FindVariable(node_variable)
    if not node_pointer:
        print(f'{node_variable} doesn''t exist')
        return

    # node_type_name value will be something like T_ProjectionPath, find the matching type
    node_type_name = node_pointer.GetChildMemberWithName('type')
    if not node_type_name:
        print(f'{node_variable} is not a node and doesn''t have a type member')
        return

    node_type_name = node_type_name.value.removeprefix('T_')
    node_type = target.FindFirstType(node_type_name)

    # Cast the node to the correct type
    node_cast = node_pointer.Cast(node_type.GetPointerType())

    # Derefence and print it
    print(node_cast.Dereference())


def pprint_node(valobj, internal_dict):
    # node_type_name value will be something like T_ProjectionPath, find the matching type
    type_field = valobj.GetChildMemberWithName('type')
    if not type_field:
        print(f'{node_variable} is not a node and doesn''t have a type member')
        return

    target = valobj.target
    print(f'type field: {type_field}')
    node_type_name = type_field.value.removeprefix('T_')
    print(f'node type name: {node_type_name}')

    node_type = target.FindFirstType(node_type_name)
    print(f'node type: {node_type}')

    if valobj.TypeIsPointerType():
        pass

    if node_type != valobj.type:
        # Cast the node to the correct type
        node_cast = valobj.Cast(node_type.GetPointerType())

        # Derefence and print it
        # return node_cast.Dereference()
        return f'Different type, {node_type}, {valobj.type}'

    return 'test'
