# InterPlanetary Soft Links (IPSL)
IPSL enables peers to curate a bidirectional [mapping](#content-location-address-mapping) between IPFS content addresses and location addresses.

Data that is not seeded by an IPFS peer may still be available via a location address. IPSL can be used to exploits this possibility when retrieving data.

**In its current state, this project is barely a proof-of-concept. It works as described. But it requires optimization and additional unit tests.**

## Motivation

Consider large scale open access static datasets. This class of data is currently primarily accessed via location addresses. However, addressing this data with IPFS content addresses could provided many benefits. For example:
* content integrity assurance
* better data set IDs to replace current non-cryptographic alternatives.

Content addressed access could be provided by seeding the data on the IPFS network. Both data servers and clients could act as seeding peers. However, data servers may be reluctant to seed due to the additional operational complexities. Currently, use of the filestore extension requires careful management. Seeding data without the filestore extension requires duplicating the data.

The limitations of data clients as seeding peers become obvious when very large scale datasets are concerned. Without intentional organization, clients lack the motivation to mirror a significant portion of the dataset. Especially when operational location addresses exist.

This project explores a third possibility. IPSL facilitates the retrieval of data using the IPFS client interface whilst also leveraging existing location addresses when necessary. This should encourage the proliferation of:
 * the IPFS interface for data retrieval
 * content addresses for addressing data.

## Content-Location Address Mapping
Content address to location address bidirectional mapping is stored as an IPLD DAG object. IPFS link entries consist of one-to-many mappings. All other protocol entries use one-to-one mappings.

```json
{
  "ipfs": {
    "QxmG...42gD": {
      "https": "www.ebi.ac.uk/ena/.../view/A00145%26display%3Dfasta",
      "ftp": "ftp.sra.ebi.ac.uk/vol1/.../PHESPV0057.R1.fastq.gz"
    }
  },
  "https": {
    "www.ebi.ac.uk/ena/.../view/A00145%26display%3Dfasta": {
      "ipfs": "QxmG...42gD"
    }
  },
  "ftp": {
    "ftp.sra.ebi.ac.uk/vol1/.../PHESPV0057.R1.fastq.gz": {
      "ipfs": "QxmG...42gD"
    }
  }
}
```

## Usage

```
InterPlanetary Soft Links (IPSL)

Usage:
  ipsl links show [--ipfs=<ipfs> | --https=<https> | --ftp=<ftp>]
  ipsl links add --ipfs=<ipfs> [--https=<https>] [--ftp=<ftp>]
  ipsl links merge <ipfs>
  ipsl domains show
  ipsl domains add <pattern>
  ipsl config show
  ipsl (-h | --help)
  ipsl --version

Options:
  --ipfs=<ipfs>   IPFS address
  --https=<https> HTTPS address
  --ftp=<ftp>     FTP address
  <pattern>       Unix shell-style wildcard
  -h --help       Show this screen.
  --version       Show version.

Subcommands:
  links           Add and get link entries; merge other link maps
  domains         Manage domains for merging link maps
  config
```

### Examples

#### Adding links

```
$ ipsl links add --ipfs QmZJJZ4pEa88wqvgVDjTVHy89ZKbNnemg4GecKAHgZZB7E --https www.ebi.ac.uk/ena/data/view/A00145%26display%3Dfasta
```

#### Merging other maps

Add domain of interest:
```
$ ipsl domains add *.ebi.ac.uk
```

Scrape and merge links map. Add domain matches to local map:

```
$ ipsl links merge zdpuAqkqxRf79Z7WcB7S1SRGumKQXvcVsL7Phx6NwvMQVA3vL
```

## Install
Requires Python 3.

```
$ virtualenv ipsl_venv
$ source ./ipsl_venv/bin/activate
$ pip3 install git+https://github.com/rffrancon/ipsl
```

## License

MIT