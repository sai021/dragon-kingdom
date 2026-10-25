"""Separate, unmodified esptool CLI process. No automatic device commands."""
import sys
import esptool

if __name__ == '__main__':
    esptool.main(sys.argv[1:])
