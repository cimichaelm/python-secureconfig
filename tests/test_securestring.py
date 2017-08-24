from __future__ import print_function

import ctypes
import gc
import sys
import unittest

from secureconfig import SecureString


def get_from_mem(ctypes_tuple):
    location = ctypes_tuple[0]
    size = ctypes_tuple[1]
    return ctypes.string_at(location, size)

def learn_mem(item):
    location = id(item)
    size = sys.getsizeof(item)
    return (location, size)

class TestSecureString(unittest.TestCase):

    def test_SecureString_has_str_methods(self):
        secret = SecureString('test')
        str_methods = set(dir(str))
        ss_methods = set(dir(secret))
        self.assertEqual([s for s in str_methods if s not in ss_methods], [])


    def test_str_methods_still_work(self):
        # not going to test every single one. a smattering will do.
        secret = SecureString("more than just a dream")
        self.assertFalse(secret.isupper())
        self.assertTrue(secret.islower())
        self.assertTrue(secret.startswith('more'))
        self.assertEqual(secret.find('than'), 5)

    def test_burn_method_zeroes__string(self):
        ss = SecureString("of all the things I've lost, I miss my mind the most")
        ctuple = learn_mem(ss._string)
        ss.burn()
        gc.collect()
        result = get_from_mem(ctuple)
        self.assertNotIn(b'things', result)
        self.assertNotIn(b'lost', result)

    def test_SecureString_zeroes_on_del(self):
        ss = SecureString("it's a secret23 to everybody")
        ctuple = learn_mem(ss._string)
        del(ss)
        gc.collect()
        result = get_from_mem(ctuple)
        with self.assertRaises(UnboundLocalError):
            print(ss)  # noqa

        self.assertNotIn(b'23', result)
        self.assertNotIn(b'everybody', result)
        self.assertNotIn(b"it's", result)


if __name__ == '__main__':
    unittest.main()

