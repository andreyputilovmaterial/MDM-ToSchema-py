## import os, time, re, sys
from datetime import datetime
# from dateutil import tz
import argparse
from pathlib import Path
import json
import traceback, sys




if __name__ == '__main__':
    # run as a program
    from GENERATED._VERSION import _VERSION as script_version
    from make_pydantic import process_field
    from load_mdd import MDMDocument
elif '.' in __name__:
    # package
    from .GENERATED._VERSION import _VERSION as script_version
    from .make_pydantic import process_field
    from .load_mdd import MDMDocument
else:
    # included with no parent package
    from GENERATED._VERSION import _VERSION as script_version
    from make_pydantic import process_field
    from load_mdd import MDMDocument




# STDOUT_COLOR_RED = "\033[91m"
STDOUT_COLOR_RED = "\033[31m"
STDOUT_COLOR_RESET = "\033[0m"
STDOUT_COLOR_GREEN = "\033[32m"









def entry_point(*argcs,**kwargs):
    script_name = 'MDD to JSON schema script'
    try:
        time_start = datetime.now()
        parser = argparse.ArgumentParser(
            description="Build JSON schema from MDD",
            prog='mdmtoolsapram mdd_build_schema'
        )
        parser.add_argument(
            '-1',
            '--inp',
            help='Input MDD',
            type=str,
            required=True
        )
        parser.add_argument(
            '--method',
            default='open',
            help='MDD Reading Method - the same what you have in PrepData or FileTrimmer - can be mdd.open() or mdm.join()',
            choices=['open','join'],
            type=str,
            required=False
        )
        args = parser.parse_args(*argcs,**kwargs)
        inp_mdd = None
        if args.inp:
            inp_mdd = Path(args.inp)
            inp_mdd = f'{inp_mdd.resolve()}'
        else:
            raise FileNotFoundError('Inp source: file not provided; please use --inp')

        if not(Path(inp_mdd).is_file()):
            raise FileNotFoundError(f'file not found: {inp_mdd}')

        method = '{arg}'.format(arg=args.method) if args.method else 'open'

        config = {
            'script_name': script_name,
            'script_started': time_start,
            'script_version': script_version.strip(),
        }

        # print(f'{script_name}: script started at {time_start}')
        # print(f'{script_name}: MDD: {inp_mdd}')

        with MDMDocument(inp_mdd,method,config) as mdm:

            mdm.mdmdocument.Contexts.Current = 'Question'
            result_type_def, result_type_constraints = process_field(mdm.mdmdocument)
            result = result_type_def.model_json_schema()

            result_json = json.dumps(result, indent=4)
            # result_json_fname = ( Path(inp_mdd).parents[0] / '{basename}{ext}'.format(basename=Path(inp_mdd).name,ext='.schema.json') if Path(inp_mdd).is_file() else re.sub(r'^\s*?(.*?)\s*?$',lambda m: '{base}{added}'.format(base=m[1],added='.schema.json'),'{path}'.format(path=inp_mdd)) )
            # print(f'{script_name}: {STDOUT_COLOR_GREEN}saving as "{result_json_fname}"{STDOUT_COLOR_RESET}')
            # with open(result_json_fname, "w") as outfile:
            #     outfile.write(result_json)
            print(result_json)

        time_finish = datetime.now()
        # print(f'{script_name}: finished at {time_finish} (elapsed {time_finish-time_start})')
    except Exception as e:
        # for pretty-printing any issues that happened during runtime; if we hit FileNotFound I don't appreciate when a log traceback is shown, the error should be simple and clear
        # the program is designed to be user-friendly
        # that's why we reformat error messages a little bit
        # stack trace is still printed (I even made it longer to 20 steps!)
        # but the error message itself is separated and printed as the last message again

        # for example, I don't write 'print('File Not Found!');exit(1);', I just write 'raise FileNotFoundErro()'
        print('',file=sys.stderr)
        print('Stack trace:',file=sys.stderr)
        print('',file=sys.stderr)
        traceback.print_exception(e,limit=20)
        print('',file=sys.stderr)
        print('',file=sys.stderr)
        print('',file=sys.stderr)
        print(f'{STDOUT_COLOR_RED}Error:{STDOUT_COLOR_RESET}',file=sys.stderr)
        print('',file=sys.stderr)
        print(f'{STDOUT_COLOR_RED}{e}{STDOUT_COLOR_RESET}',file=sys.stderr)
        print('',file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    entry_point()
