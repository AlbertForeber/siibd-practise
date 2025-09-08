from dataclasses import dataclass
from typing import Optional, Dict

@dataclass()
class VFSNode:
    name: str
    filetype: str
    data: Optional[Dict] = None
    permissions: Optional[str] = None
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.permissions is None:
            self.permissions = 'd----------' if self.filetype == 'dir' else '-----------'