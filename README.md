# mls-reddit-bot
Reddit bot for r/MLS that pulls information from MLS and ESPN to post and maintain match threads. Automated via AWS Lambda.

## Output

https://www.reddit.com/r/MLS_Reddit_Bot/

## Build and usage notes

To build and package locally, you may need to install python dependencies:
```
python3 -m pip install setuptools lambda-setuptools praw dateutils pytest pytz
```

Next, build:
```
$ make
```

This produces a zipped Lambda "layer," which you can copy somewhere easier to access:

```
cp dist/mls_reddit_bot-1.0.0.zip ~/Downloads/
```

Next, upload that through the aws console at Lambda > Layers. From there, modify
the lambda function to use that newest version of the layer.

The actual lambda function is included for reference at the top level of this
package, but it's really just the lightest possible wrapper around
`mls_reddit_bot.main:main`.

The lambda requires a few different resources and permissions to be in place:

* aws, provided explicitly to the lambda function through aws policies
  * s3 bucket access
    * caches api results (and soon potentially reddit thread text)
  * ddb table access
    * keeps track of created match threads and related game status
* environment variables set in the lambda context for reddit
  * `praw_client_id`
  * `praw_client_secret`
  * `praw_password`
  * `praw_username`


### Local CLI

To install the package and `mls-reddit-bot-cli` wrapper locally:

```
$ make install | grep mls-reddit-bot-cli
Installing mls-reddit-bot-cli script to /Users/mrundle/Library/Python/3.9/bin
```

Assuming this is on your path, you can simply run `mls-reddit-bot-cli` to execute
the same main loop that will run under Lambda. This requires both of the following:

1. PRAW credentials either exported as environment variables or stored in `~/.config/praw.ini`
2. AWS credentials either exported as environment variables or stored as default in `~/.aws/config` and `~/.aws/credentials`

To run for a specific date and time:

```
$ mls-reddit-bot-cli --start 2024-03-22 --end 2024-03-24 --prefer-cached-espn
```
