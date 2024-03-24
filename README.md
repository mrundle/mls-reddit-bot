# mls-reddit-bot
Reddit bot for r/MLS that pulls information from MLS and ESPN to post and maintain match threads. Automated via AWS Lambda.

First you may need to install python dependencies:
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
  * (soon) ddb table access
* environment variables set in the lambda context for reddit
  * `praw_client_id`
  * `praw_client_secret`
  * `praw_password`
  * `praw_username`
