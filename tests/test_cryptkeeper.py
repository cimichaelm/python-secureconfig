from __future__ import print_function

import os
import unittest

from cryptography.fernet import InvalidToken

from secureconfig.cryptkeeper import (
    encrypt_string,
    EnvCryptKeeper,
    FileCryptKeeper,
    CryptKeeper
)

CWD = os.path.dirname(os.path.realpath(__file__))

TEST_KEYSTRING = 'sFbO-GbipIFIpj64S2_AZBIPBvX80Yozszw7PR2dVFg='
TEST_KEYSTRING_WRONG = 'UCPUOddzvewGWaJxW1ZlPKftdlS9SCUjwYUYwov0bT0='

TEST_KEYENV_NAME = 'CK_TEST_KEY'
TEST_KEYFILE_PATH = os.path.join(CWD, 'ck_test_key')

TEST_BAD_KEY = 'YOUR_MOM='

def assure_clean_env():
    os.environ[TEST_KEYENV_NAME] = ''

class TestCryptKeeper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        assure_clean_env()


    def setUp(self):
        # environment variable used here should be created on the fly.
        self.env_ck = EnvCryptKeeper(TEST_KEYENV_NAME)

        # file will be created in CWD and deleted afterwards.
        self.file_ck = FileCryptKeeper(TEST_KEYFILE_PATH)

        #
        self.string_ck = CryptKeeper(key=TEST_KEYSTRING)
        self.string_ck_wrong = CryptKeeper(key=TEST_KEYSTRING_WRONG)

    def test_FileCK_creates_keyfile(self):
        self.assertTrue(os.path.exists(TEST_KEYFILE_PATH))
        self.assertEqual(
            self.file_ck.key,
            open(TEST_KEYFILE_PATH, 'r').read().strip().encode(),
        )

    def test_EnvCK_creates_env(self):
        self.assertIn(TEST_KEYENV_NAME, os.environ)
        self.assertEqual(
            self.env_ck.key,
            os.environ.get(TEST_KEYENV_NAME).encode(),
        )


    def test_EnvCK_from_env(self):
        os.putenv('ARBITRARY_ENV_NAME', TEST_KEYSTRING)
        env_ck = EnvCryptKeeper('ARBITRARY_ENV_NAME')
        self.assertEqual(
            env_ck.key.decode(),
            os.environ['ARBITRARY_ENV_NAME']
        )

    def test_FileCK_from_file(self):
        file_ck = FileCryptKeeper(TEST_KEYFILE_PATH)
        self.assertEqual(
            file_ck.key,
            open(TEST_KEYFILE_PATH, 'r').read().strip().encode(),
        )

    def test_StringCK_key_eq_key(self):
        self.assertEquals(self.string_ck.key, TEST_KEYSTRING)

    @unittest.skip
    def test_bad_key_raises_InvalidToken(self):
        with self.assertRaises(InvalidToken):
            CryptKeeper(TEST_BAD_KEY)

    def test_wrong_key_raises_InvalidToken(self):
        enctxt = encrypt_string(TEST_KEYSTRING, 'test string')
        with self.assertRaises(InvalidToken):
            self.string_ck_wrong.decrypt(enctxt)

    def test_clean_key(self):
        key_with_whitespace = '\n' + TEST_KEYSTRING + '  '
        self.assertEqual(
            self.string_ck._clean_key(key_with_whitespace),
            TEST_KEYSTRING
        )

    def test_generate_key(self):
        new_key = CryptKeeper.generate_key()
        self.assertIsNotNone(new_key)
        #TODO
        #assert(verify_key(new_key))


if __name__ == '__main__':
    assure_clean_env()
    unittest.main()

