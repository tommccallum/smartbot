import logging
import os


class FifoFile:
    """
    Fifo object that handles directory and file creation
    """

    instance_counter = 1
    """Makes any fifo name unique"""

    def __init__(self, fifo_path=None, filename_prefix = "smartbot"):
        self.fifo_filename = "{}_{}.{}".format(filename_prefix, str(FifoFile.instance_counter),"fifo")
        FifoFile.instance_counter += 1
        self.full_path = self._make_fifo(fifo_path, self.fifo_filename)

    def write(self, command):
        logging.debug("Sending command '{}' to fifo '{}'".format(command,self.full_path))
        with open(self.full_path, "w") as out_file:
            out_file.write(command + "\n")
        logging.info("Written '" + command + "' to " + self.full_path)

    def _make_fifo(self, path, filename):
        """
        Creates fifo file and returns path to it
        """
        self._create_fifo_directory(path)
        full_path = os.path.join(path, filename)
        self._create_fifo_file(full_path)
        return full_path

    def _create_fifo_file(self, full_path):
        if not os.path.exists(full_path):
            logging.info("Making fifo at {}".format(full_path))
            os.mkfifo(full_path)

    def _create_fifo_directory(self, path):
        if not os.path.isdir(path):
            logging.info("Creating directory: {}".format(path))
            os.makedirs(path)

    def delete(self):
        logging.debug("attempting to remove fifo {}".format(self.full_path))
        if self.full_path and os.path.exists(self.full_path):
            logging.debug("Removing {}".format(self.full_path))
            os.remove(self.full_path)

    def __del__(self):
        self.delete()
