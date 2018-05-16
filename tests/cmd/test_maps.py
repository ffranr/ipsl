import unittest
import ipfsapi

import ipsl


class TestGet(unittest.TestCase):
    def setUp(self):
        ipsl.config.TEST_MODE = True

    def tearDown(self):
        ipfs_api = ipsl.common.ipfs.connect()
        try:
            ipfs_api.files_rm(ipsl.config.TEST_CONFIG_PATH)
        except ipfsapi.exceptions.StatusError:
            pass

    def test_RetrieveMapContainingSingleLink_CorrectMap(self):
        ipsl.links.add(ipfs="ipfs_addr", https="https_addr", ftp="ftp_addr")
        result = ipsl.maps.get()
        expected = {
            'ftp': {
                'ftp_addr': {
                    'ipfs': 'ipfs_addr'
                }
            },
            'https': {
                'https_addr': {
                    'ipfs': 'ipfs_addr'
                }
            },
            'ipfs': {
                'ipfs_addr': {
                    'ftp': 'ftp_addr',
                    'https': 'https_addr'
                }
            }
        }
        self.assertEqual(expected, result)


class TestAdd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        secondary_map = {
            'ftp': {
                'domain1/ftp/sub': {
                    'ipfs': 'ipfs_addr_1'
                }
            },
            'https': {
                'domain1/https/sub': {
                    'ipfs': 'ipfs_addr_1'
                },
                'domain2/https/sub': {
                    'ipfs': 'ipfs_addr_2'
                }
            },
            'ipfs': {
                'ipfs_addr_1': {
                    'ftp': 'domain1/ftp/sub',
                    'https': 'domain1/https/sub'
                },
                'ipfs_addr_2': {
                    'https': 'domain2/https/sub'
                }
            }
        }
        ipfs_api = ipsl.common.ipfs.connect()
        cls.secondary_map_cid = ipfs_api.dag_put(secondary_map)

    def setUp(self):
        ipsl.config.TEST_MODE = True

    def tearDown(self):
        ipfs_api = ipsl.common.ipfs.connect()
        try:
            ipfs_api.files_rm(ipsl.config.TEST_CONFIG_PATH)
        except ipfsapi.exceptions.StatusError:
            pass

    def test_ExtractDomainWithOnlyHttps_CorrectLinksExtracted(self):
        ipsl.domains.add('domain2')
        ipsl.maps.add(self.secondary_map_cid)
        result = ipsl.maps.get()

        expected = {
            'ftp': {},
            'https': {
                'domain2/https/sub': {
                    'ipfs': 'ipfs_addr_2'
                }
            },
            'ipfs': {
                'ipfs_addr_2': {
                    'https': 'domain2/https/sub'
                }
            }
        }
        self.assertEqual(expected, result)

    def test_ExtractDomainWithFtpHttps_CorrectLinksExtracted(self):
        ipsl.domains.add('domain1')
        print(self.secondary_map_cid)
        ipsl.maps.add(self.secondary_map_cid)
        result = ipsl.maps.get()

        expected = {
            'ftp': {
                'domain1/ftp/sub': {
                    'ipfs': 'ipfs_addr_1'
                }
            },
            'https': {
                'domain1/https/sub': {
                    'ipfs': 'ipfs_addr_1'
                }
            },
            'ipfs': {
                'ipfs_addr_1': {
                    'ftp': 'domain1/ftp/sub',
                    'https': 'domain1/https/sub'
                }
            }
        }
        self.assertEqual(expected, result)

    def test_WildcardDomainCapturingAll_CorrectLinksExtracted(self):
        ipsl.domains.add('domain*')
        ipsl.maps.add(self.secondary_map_cid)
        result = ipsl.maps.get()

        expected = {
            'ftp': {
                'domain1/ftp/sub': {
                    'ipfs': 'ipfs_addr_1'
                }
            },
            'https': {
                'domain1/https/sub': {
                    'ipfs': 'ipfs_addr_1'
                },
                'domain2/https/sub': {
                    'ipfs': 'ipfs_addr_2'
                }
            },
            'ipfs': {
                'ipfs_addr_1': {
                    'ftp': 'domain1/ftp/sub',
                    'https': 'domain1/https/sub'
                },
                'ipfs_addr_2': {
                    'https': 'domain2/https/sub'
                }
            }
        }
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
