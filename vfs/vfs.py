import os.path
import xml.etree.ElementTree as ET

from util.errors import WrongFormatError, ParseError, VFSNotFoundError
from util.utils import decode_b64
from vfs_node import VFSNode


class VFS:
    def __init__(self):
        self.current_directory = VFSNode('root', 'dir', {})


    # XML to nodes converter
    def from_xml(self, source: str):

        if not source.lower().endswith('.xml'):
            raise WrongFormatError(source)

        if not os.path.exists(source):
            raise VFSNotFoundError(source)

        try:
            tree = ET.parse(source)
        except ET.ParseError:
            raise ParseError(source)

        root_element = tree.getroot()
        self.__build_node(root_element, self.current_directory)

    def __build_node(self, parent_element, parent):
        for file in parent_element.findall('*'):
            file_type = file.get('type', 'text')
            file_name = file.get('name', file.tag)
            file_attrib = file.attrib

            if not parent.data.get(f'{file_name}'):
                if file_type == 'dir':
                    new_node = VFSNode(file_name, 'dir', {'..': parent})
                    self.__build_node(file, new_node)

                elif file_type == 'binary':
                    if 'data' not in file_attrib:
                        raise ParseError(f"Binary element {file_name} missing data element")
                    new_node = VFSNode(file_name, 'binary', {'..': parent, 'content': decode_b64(file_attrib['data'])})

                elif file_type == 'text':
                        new_node = VFSNode(file_name, 'text', {'..': parent, 'content': file_attrib['data']})

                else:
                    raise ParseError(f'Unknown filetype: {file_type}')

                if 'permission' in file_attrib:
                    new_node.permissions = file_attrib['permission']

                parent.data[f'{file_name}'] = new_node
            else:
                raise ParseError(f'Duplicated file found: {file_name}')
