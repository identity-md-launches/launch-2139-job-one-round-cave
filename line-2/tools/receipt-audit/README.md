# Receipt Audit

Recheck a saved Proof Receipt against its original Ethereum account/storage
proof, an explicitly supplied trusted state root, expected contract address and
reviewed storage layout. A receipt's `verified: true` flag and self-computed
digest are not evidence on their own. This tool regenerates the entire receipt
through the unchanged Proof Receipt and Storage Fields verifiers, then compares
canonical JSON bytes, including JSON types, fields and digest. Unknown or missing
fields fail. Only the producer's optional text `demo` annotation is ignored.

Run from the repository root (Python 3.9+, standard library only):

```sh
python3 -B line-2/tools/receipt-audit/audit.py demo
```

The demo reads a saved receipt and the inherited real historical ZTO/IMD
PoolManager witness at Ethereum block 26212390. When tried, it verified one
slot and five fields, including LP fee 12500. All 13 tests passed, including an
edited field whose attacker recomputed the receipt digest, wrong external
anchors, changed layout, broken proof, JSON boolean/numeric substitutions,
duplicate JSON keys and oversized receipts. The fixed demo root is an inherited
RPC observation, not an independently authenticated checkpoint. No new chain
observation is implied. Public source: https://ethereum-rpc.publicnode.com.

To check the same saved historical receipt explicitly:

```sh
python3 -B line-2/tools/receipt-audit/audit.py check \
  line-2/tools/receipt-audit/historical-receipt.json \
  line-2/tools/state-witness/examples/zto-pool-mainnet.json \
  line-2/tools/storage-fields/pool-layout.json \
  --state-root 0x70c13580735123b57c0a9a24692875f4ef366b04c69d92af9f539561e626d512 \
  --address 0x000000000004444c5dc75cb358380d2e3de08a90
```

For other evidence replace all three files, root and address with independently
reviewed inputs. Optional `--expected-digest` takes a separately retained
lowercase 64-digit receipt SHA-256 and additionally pins exact receipt identity.
It never substitutes for proof verification. Success prints `verified: true`
and exits 0; invalid evidence prints `verified: false` on stderr and exits 1.
Input files must resolve within the working directory; receipts are limited to
64 KiB, with inherited bounds on witnesses and layouts. Run from the workspace
root. This is read-only and offline: no wallet, keys, environment inspection,
signatures, transactions, payments or posting.

```sh
python3 -B -m unittest discover -s line-2/tools/receipt-audit -v
```

The tool depends on its unchanged sibling folders `proof-receipt/`,
`storage-fields/` and `state-witness/`; carry those along when copying it.
Proof verification establishes raw historical state relative to a supplied root.
Root authentication, layout interpretation, consensus and freshness remain
caller responsibilities. This is not a current pool quote or a signature.
