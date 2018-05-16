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

    def test_GetIpfsAddress_ReturnAllLinks(self):
        ipsl.links.add(ipfs="addr_ipfs", https="https://addr_https/test", ftp="addr_ftp/test")
        result = ipsl.links.get(ipfs="addr_ipfs")
        expected = {
            "ipfs": "addr_ipfs",
            "https": "addr_https/test",
            "ftp": "addr_ftp/test",
        }
        self.assertEqual(expected, result)

    def test_GetHttpsAddress_ReturnAllLinks(self):
        ipsl.links.add(ipfs="addr_ipfs", https="addr_https/test", ftp="addr_ftp/test")
        result = ipsl.links.get(https="addr_https/test")
        expected = {
            "ipfs": "addr_ipfs",
            "https": "addr_https/test",
            "ftp": "addr_ftp/test",
        }
        self.assertEqual(expected, result)

    def test_GivenProtocolPrefixHttpsLink_ReturnCleanHttpsLink(self):
        ipsl.links.add(ipfs="addr_ipfs", https="https://addr_https/test")
        result = ipsl.links.get(ipfs="addr_ipfs")
        expected = {
            "ipfs": "addr_ipfs",
            "https": "addr_https/test",
        }
        self.assertEqual(expected, result)

    def test_AttemptAddWithoutIpfsAddress_AssertionError(self):
        with self.assertRaises(AssertionError) as _:
            ipsl.links.add(https="addr_https/test", ftp="addr_ftp/test")


if __name__ == '__main__':
    unittest.main()
