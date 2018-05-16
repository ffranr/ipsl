import unittest
import ipfsapi

import ipsl


class TestAddGet(unittest.TestCase):
    def setUp(self):
        ipsl.config.TEST_MODE = True

    def tearDown(self):
        ipfs_api = ipsl.common.ipfs.connect()
        try:
            ipfs_api.files_rm(ipsl.config.TEST_CONFIG_PATH)
        except ipfsapi.exceptions.StatusError:
            pass

    def test_AddPattern_CorrectGetResult(self):
        ipsl.domains.add(pattern="*.addr")
        result = ipsl.domains.get()
        expected = {
            "patterns": [
                "*.addr"
            ],
            "seen": [],
        }
        self.assertEqual(expected, result)

    def test_AddSeen_CorrectGetResult(self):
        ipsl.domains.add(seen="www.addr.com")
        result = ipsl.domains.get()
        expected = {
            "patterns": [],
            "seen": [
                "www.addr.com"
            ],
        }
        self.assertEqual(expected, result)



if __name__ == '__main__':
    unittest.main()
