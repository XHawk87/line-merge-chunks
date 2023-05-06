# line-merge-chunks

Merges separate lines together from standard input, escaping new line characters, and outputting them in chunks to
standard output limited by time and/or character count.

My use-case for this is to merge tailed log file output into chunks suitable for a chat bot to send to a room, while
respecting rate limits.

## Installation

To install `line-merge-chunks`, run:

`pip install line-merge-chunks`

This will install the script to your `~/.local/bin` folder.

## Usage

To use `line-merge-chunks`, simply pipe data to it via standard input:

`echo -e "Hello,\nworld!" | line-merge-chunks`

This will output the following:

`Hello,\\nworld!\\n\n`

You can also specify the maximum chunk size and wait time using the `--max-chars` and `--max-time` options:

`echo "abcdefghijklmnopqrstuvwxyz" | line-merge-chunks --max-chars 10 --max-time 0.1`

This will output the following:

`abcdefghi\njklmnopqr\nstuvwxyz\\n\n`

## License

This script is released under the GNU Affero General Public License v3 or later (AGPLv3+).
