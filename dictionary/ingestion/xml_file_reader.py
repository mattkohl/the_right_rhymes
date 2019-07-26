from typing import AnyStr


class FileReader:

    @staticmethod
    def read_file(filename: AnyStr) -> AnyStr:
        f = open(filename, 'rb')
        try:
            file_string = f.read()
        except Exception as e:
            raise IOError(f"Can't read in source file: {e}")
        else:
            f.close()
            return file_string
