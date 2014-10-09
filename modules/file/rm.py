from core.vectors import PhpCmd, ShellCmd, ModuleCmd, Os
from core.module import Module
from core import modules
import tempfile

class Rm(Module):

    """Remove remote file."""

    aliases = [ 'rm' ]

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments([
          { 'name' : 'rpath', 'help' : 'Remote file path' }
        ])

    def run(self, args):

        # Run unlink
        return PhpCmd("""(unlink('${rpath}') && print(1)) || print(0);""",
                        postprocess = lambda x: True if x == '1' else False
                        ).run(args)