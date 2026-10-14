# Model tree digest — v1

Algorithm name: `compiled-tree-sha256-v1`.
The loader uses this digest for local model identity. It is not an archive hash or Python inventory hash.
The same tree algorithm can identify a source package, but source and compiled digests remain separate fields.

## Canonical bytes

1. Read every regular file below the selected root.
2. Use relative paths with `/` separators. Do not include the root directory name.
3. Reject links inside the tree and special files.
4. Sort records by relative path. The release contract uses ASCII paths.
5. Hash each file with SHA-256. Use lowercase hexadecimal output.
6. Start the stream with UTF-8 bytes for `compiled-tree-sha256-v1\n`.
7. Append each record as `path`, NUL, decimal byte count, NUL, file hash, and LF.
8. Hash that complete stream with SHA-256. Use lowercase hexadecimal output.

Here, `\n` means one LF byte. NUL means byte `0x00`.
Do not hash the visible escape characters.
Empty directories do not affect the digest. An empty tree is invalid.
The current loader limits directories and files to 1,024 each.
It limits each file to 64 MiB and the total to 128 MiB.
The source archive contract has tighter limits and remains independently enforced.

## Independent test vector

| Relative path | Exact content | Bytes | File SHA-256 |
| --- | --- | --- | --- |
| `a.bin` | Hex `00 01 ff` | 3 | `26a66b061e8f48f39927c312f25293959729eee95978e2892d49d3512a5cc092` |
| `nested/b.txt` | UTF-8 `focus` followed by LF | 6 | `1d60c3818cfb64a0802a5b25413d0062ea62268e911cdf7c066a8fab683f51f0` |

Expected tree digest: `7d6c6b1e9b9bf952e0963de83fc3348c5d599d54ad6c5110edf13ccbf1f6cac7`.
Python's standard SHA-256 implementation supplies the independent calculation. The Swift test checks the production digest against that value.
File creation order and the selected root name do not change this value.

## Trust and host limits

A matching digest proves byte identity, not model quality or distribution rights.
Get the expected archive hash from the trusted catalog before compilation.
Record the source digest, compiled digest, helper digest, OS build, and architecture separately.
Do not assume that compiled model bytes remain portable across hosts or compiler updates.
The installation receipt version is 2. Older receipts do not pass the new recovery checks.
