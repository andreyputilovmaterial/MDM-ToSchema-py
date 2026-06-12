
from datetime import datetime # for setting property in MDD object - not sure I need to have it captured
from pathlib import Path # for validating path to file

from .win32com_adapter import Win32Client







class MDMDocument:
    def __init__(self,mdd_path,method='open',config={}):

        self.mdmdocument = None

        if method=='open':
            # mDocument = win32com.client.Dispatch("MDM.Document")
            mDocument = Win32Client.Dispatch("MDM.Document")
            # openConstants_oNOSAVE = 3
            openConstants_oREAD = 1
            # openConstants_oREADWRITE = 2
            print('opening MDM document using method "open": "{path}"'.format(path=mdd_path))
            # we'll check that the file exists so that the error message is more informative - otherwise you see a long stack of messages that do not tell much
            if not(Path(mdd_path).is_file()):
                raise FileNotFoundError('file not found: {fname}'.format(fname=mdd_path))
            mDocument.Open( mdd_path, "", openConstants_oREAD )
            self.mdmdocument = mDocument
        elif method=='join':
            # mDocument = win32com.client.Dispatch("MDM.Document")
            mDocument = Win32Client.Dispatch("MDM.Document")
            print('opening MDM document using method "join": "{path}"'.format(path=mdd_path))
            # we'll check that the file exists so that the error message is more informative - otherwise you see a long stack of messages that do not tell much
            if not(Path(mdd_path).is_file()):
                raise FileNotFoundError('file not found: {fname}'.format(fname=mdd_path))
            mDocument.Join(mdd_path, "{..}", 1, 32|16|512)
            self.mdmdocument = mDocument
        else:
            raise ValueError('MDM Open: Unknown open method, {method}'.format(method=method))

        self.mdd_path = mdd_path
        self.read_datetime = datetime.now()
        config_default = {
        }
        self.__config = { **config_default, **config }

    # unlink document if some error happened, or if we are done processing it
    def __del__(self):
        if self.mdmdocument is not None:
            self.mdmdocument.Close()
        print('MDM document closed')

    # strange methods required by python so that I can use "with"
    # I still don't understand why this is needed as we already have __init__ and __del__ and allll should work, why on Earth __enter__ and __exit__ are necessary????
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass



