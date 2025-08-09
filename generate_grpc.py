from grpc_tools import protoc
import os


def generate_grpc_files():
    proto_path = "app/proto/note.proto"
    output_dir = "app/infrastructure/adapters/inbound/grpc"
    proto_include = protoc.__file__.split('grpc_tools')[0] + 'grpc_tools/_proto'
    os.makedirs(output_dir, exist_ok=True)

    result = protoc.main([
        'grpc_tools.protoc',
        f'-I{proto_include}',
        f'-Iapp/proto',
        f'--python_out={output_dir}',
        f'--grpc_python_out={output_dir}',
        proto_path
    ])

    if result != 0:
        raise RuntimeError(f"Failed to generate gRPC files for {proto_path}")

    # Исправление импортов в note_pb2_grpc.py
    grpc_file = f"{output_dir}/note_pb2_grpc.py"
    with open(grpc_file, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace("import note_pb2 as", "from . import note_pb2 as")
    with open(grpc_file, 'w', encoding='utf-8') as f:
        f.write(content)


if __name__ == "__main__":
    generate_grpc_files()