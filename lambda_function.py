from mls_reddit_bot import main

def lambda_handler(event, context):
    try:
        main.main()
        return {
            'statusCode': 200,
            'body': 'OK',
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': str(e),
        }
