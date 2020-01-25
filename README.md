Jeffy(Beta)
=======

# Description

Jeffy is Serverless **"Application"** Framework for Python, which is
suite of Utilities for Lambda functions to make it easy to develop serverless applications.

Mainly, focusing on three things.

- Logging: Providing easy to see JSON format logging, auto logging as a decorator for capturing events and responses and errors, configurable to inject additional attributes what you want to see to logs.
- Decorators: To save time to implement common things for Lambda functions, providing some useful decorators.
- Tracing: Traceable events within related functions and AWS services with generating and passing `correlation_id`.
- Environment Variables: You can define configuration for Jeffy via Environment Variables of Lambda.

# TOC

- [Jeffy(Beta)](#jeffy-beta-)
- [Description](#description)
- [Install](#install)
- [Features](#features)
  * [Logging](#logging)
    + [Basic Usage](#basic-usage)
    + [Injecting additional attributes to CloudWatchLogs](#injecting-additional-attributes-to-cloudwatchlogs)
    + [Auto Logging](#auto-logging)
  * [Decorators](#decorators)
    + [json_scheme_validator](#json-scheme-validator)
    + [api_json_scheme_validator](#api-json-scheme-validator)
    + [api](#api)
    + [sqs](#sqs)
    + [sns](#sns)
    + [kinesis_stream](#kinesis-stream)
    + [dynamodb_stream](#dynamodb-stream)
    + [s3](#s3)
    + [schedule](#schedule)
  * [Tracing](#tracing)
    + [Kinesis Clinent](#kinesis-clinent)
    + [SNS Client](#sns-client)
    + [SQS Client](#sqs-client)
    + [S3 Client](#s3-client)
    + [Environment Variables](#environment-variables)
    + [Example serverless.yml of Serverless Framework using supported environment variables](#example-serverlessyml-of-serverless-framework-using-supported-environment-variables)
- [Requirements](#requirements)
  * [Development](#development)
  * [Authors](#authors)
  * [Credits](#credits)
  * [License](#license)

# Install

```sh
$ pip install jeffy
```

# Features
## Logging
### Basic Usage
Jeffy logger automatically inject some Lambda contexts to CloudWatchLogs.
```python
from jeffy.framework import setup
app = setup()

def handler(event, context):
    app.logger.info({"foo":"bar"})
```

Output in CloudWatchLogs
```json
{
   "message": {
       "foo":"bar","item":"aa"
    },
   "aws_region":"us-east-1",
   "function_name":"jeffy-dev-hello",
   "function_version":"$LATEST",
   "function_memory_size":"1024",
   "log_group_name":"/aws/lambda/jeffy-dev-hello",
   "log_stream_name":"2020/01/21/[$LATEST]d7729c0ea59a4939abb51180cda859bf",
   "correlation_id":"f79759e3-0e37-4137-b536-ee9a94cd4f52"
}
```

### Injecting additional attributes to CloudWatchLogs
You can inject some additional attributes what you want to output with using `setup` method.

```python
from jeffy.framework import setup
app = setup()

app.logger.setup({
   "username":"user1",
   "email":"user1@example.com"
})

def handler(event, context):
    app.logger.info({"foo":"bar"})
```

Output in CloudWatchLogs
```json
{
   "message": {
       "foo":"bar","item":"aa"
    },
   "username":"user1",
   "email":"user1@example.com",
   "aws_region":"us-east-1",
   "function_name":"jeffy-dev-hello",
   "function_version":"$LATEST",
   "function_memory_size":"1024",
   "log_group_name":"/aws/lambda/jeffy-dev-hello",
   "log_stream_name":"2020/01/21/[$LATEST]d7729c0ea59a4939abb51180cda859bf",
   "correlation_id":"f79759e3-0e37-4137-b536-ee9a94cd4f52"
}
```

### Auto Logging
`auto_logging` decorator allows you to output `event`, `response` and `stacktrace` when you face Exceptions

```python
from jeffy.framework import setup
app = setup()

app.logger.setup({
   "username":"user1",
   "email":"user1@example.com"
})

@app.decorator.auto_logging
def handler(event, context):
    ...
```

Error output with auto_logging

```json
{
   "error_message": "JSONDecodeError('Expecting value: line 1 column 1 (char 0)')", 
   "stack_trace":"Traceback (most recent call last):
  File '/var/task/jeffy/decorators.py', line 41, in wrapper
    raise e
  File '/var/task/jeffy/decorators.py', line 36, in wrapper
    result = func(event, context)
  File '/var/task/handler.py', line 8, in hello
    json.loads('s')
  File '/var/lang/lib/python3.8/json/__init__.py', line 357, in loads
    return _default_decoder.decode(s)
  File '/var/lang/lib/python3.8/json/decoder.py', line 337, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
  File '/var/lang/lib/python3.8/json/decoder.py', line 355, in raw_decode
    raise JSONDecodeError('Expecting value', s, err.value) from None",
   "function_name":"jeffy-dev-hello",
   "function_version":"$LATEST",
   "function_memory_size":"1024",
   "log_group_name":"/aws/lambda/jeffy-dev-hello",
   "log_stream_name":"2020/01/21/[$LATEST]90e1f70f6e774e07b681e704646feec0"
}

```

## Decorators
Decorators make simple to implement common lamdba tasks, such as parsing array from Kinesis, SNS, SQS events etc.

Here are provided decorators

### json_scheme_validator
Decorator for Json scheme valiidator. Automatically validate `event.["body"]` with following json scheme you define. raise exception if the validation fails.

```python
from jeffy.framework import setup
app = setup()

@app.decorator.json_scheme_validator(
    json_scheme={
       "type":"object",
       "properties": {
           "message": {"type":"string"}
        }
    }
)
def handler(event, context):
    return event["body"]["foo"] 
```

### api_json_scheme_validator
Decorator for Json scheme valiidator for API Gateway. Automatically validate `event.["body"]` with following json scheme. Returns 400 error if the validation fails.

```python
from jeffy.framework import setup
app = setup()
@app.decorator.api_json_scheme_validator(
    json_scheme={
       "type":"object",
       "properties": {
           "message": {"type":"string"}
        }
    },
    response_headers={
       "Content-Type":"application/jsoset=utf-8"
    }
)
def handler(event, context):
    return event["body"]["foo"]
```

### api
Decorator for API Gateway event. Automatically parse string if `event["body"]` can be parsed as Dictionary and set correlation_id in `event["correlation_id"]` you should pass to next event, returns 500 error if unexpected error happens.

```python
from jeffy.framework import setup
app = setup()

@app.decorator.api
def handler(event, context):
    return event["body"]["foo"] # returns 500 error if unexpected error happens.
```

### sqs
Decorator for sqs event. Automaticlly parse `"event.Records"` list from SQS event source to each items for making it easy to treat it inside main process of Lambda.

```python
from jeffy.framework import setup
app = setup()

@app.decorator.sqs
def handler(event, context):
    return event["foo"]
    """
    "event.Records" list from SQS event source was parsed each items
    if event.Records value is the following,
     [
         {"foo": 1},
         {"foo": 2}
     ]

    event["foo"] value is 1 and 2, event["correlation_id"] is correlation_id you should pass to next event
    """
```

### sns
Decorator for sns event. Automaticlly parse `"event.Records"` list from SNS event source to each items for making it easy to treat it inside main process of Lambda.

```python
from jeffy.framework import setup
app = setup()

@app.decorator.sns
def handler(event, context):
    return event["foo"]
    """
    "event.Records" list from SNS event source was parsed each items
    if event.Records value is the following,
     [
         {"foo": 1},
         {"foo": 2}
     ]

    event["foo"] value is 1 and 2, event["correlation_id"] is correlation_id you should pass to next event
    """
```

### kinesis_stream
Decorator for kinesis stream event. Automaticlly parse `"event.Records"` list from Kinesis event source to each items and decode it with base64 for making it easy to treat it inside main process of Lambda.

```python
@app.decorator.kinesis_stream
def handler(event, context):
    return event["foo"]
    """
    "event.Records" list from Kinesis event source was parsed each items
    and decoded with base64 if event.Records value is the following,
     [
         <base64 encoded value>,
         <base64 encoded value>
     ]

    event["foo"] value is 1 and 2, event["correlation_id"] is correlation_id you should pass to next event
    """
```

### dynamodb_stream
Decorator for dynamodb stream event. Automaticlly parse `"event.Records"` list from Dynamodb event source to  items for making it easy to treat it inside main process of Lambda.

```python
from jeffy.framework import setup
app = setup()

@app.decorator.dynamodb_stream
def handler(event, context):
    return event["foo"]
    """
    "event.Records" list from Dynamodb event source was parsed each items
    if event.Records value is the following,
     [
         {"foo": 1},
         {"foo": 2}
     ]

    event["foo"] value is 1 and 2, event["correlation_id"] is correlation_id you should pass to next event
    """
```

### s3
Decorator for S3 event. Automatically parse body stream from triggered S3 object and S3 bucket and key name to Lambda.

```python
from jeffy.framework import setup
app = setup()

@app.decorator.s3
def handler(event, context):
    event["key"] # S3 bucket key
    event["bucket_name"] # S3 bucket name
    event["body"] # object stream from triggered S3 object
    event["correlation_id"] # correlation_id
    
```

### schedule
Decorator for schedule event. just captures correlation id before main Lambda process. do nothing other than that.

```python
from jeffy.framework import setup
app = setup()

@app.decorator.schedule
def handler(event, context):
    ...
```


## Tracing
`correlation_id` is to trace subsequent Lambda functions and services. Jeffy automatically extract correlation IDs and caputure logs from the invocation event.

Also, Jeffy provide boto3 wrapper client to create and inject `correlation_id`.

### Kinesis Clinent

```python
from jeffy.sdk.kinesis import Kinesis

def handler(event, context):
    Kinesis.put_record(
        stream_name=os.environ["STREAM_NAME"],
        data={"foo": "bar"},
        partition_key="uuid",
        correlation_id=event.get("correlation_id")
    )
```

### SNS Client

```python
from jeffy.sdk.sns import Sns

def handler(event, context):
    Sns.publish(
        topic_arn=os.environ["TOPIC_ARN"],
        message="message",
        subject="subject",
        correlation_id=event.get("correlation_id")
    )
```

### SQS Client

```python
from jeffy.sdk.sqs import Sqs

def handler(event, context):
    Sqs.send_message(
        queue_url=os.environ["QUEUE_URL"],
        message="message",
        correlation_id=event.get("correlation_id")
    )
```

### S3 Client

```python
from jeffy.sdk.s3 import S3

def handler(event, context):
    S3.upload_file(
        file_path="path/to/file", 
        bucket_name=os.environ["BUCKET_NAME"],
        object_name="path/to/object",
        correlation_id=event.get("correlation_id")
    )
```

### Environment Variables
Here is configutable values for Jeffy.

| Environment variable | Description | Default |
------------------------------------------------- | --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------
 JEFFY_LOG_LEVEL | Sets logging level | "INFO" 

### Example serverless.yml of Serverless Framework using supported environment variables

You can switch loglevel according to environment. The following example is to enable debug log other than production. 

```yaml
provider:
  name: aws
  region: us-east-1
  stage: ${opt:stage, 'dev'}
  environment:
    JEFFY_LOG_LEVEL: ${self:custom.logLevel.${self:provider.stage}, self:custom.logLevel.default}

custom:
  logLevel:
    production: ERROR
    default: DEBUG
```

# Requirements

- Python 3

Development
-----------

-   Source hosted at [GitHub](https://github.com/marcy-terui/jeffy)
-   Report issues/questions/feature requests on [GitHub
    Issues](https://github.com/marcy-terui/jeffy/issues)

Pull requests are very welcome! Make sure your patches are well tested.
Ideally create a topic branch for every separate change you make. For
example:

1.  Fork the repo
2.  Create your feature branch (`git checkout -b my-new-feature`)
3.  Commit your changes (`git commit -am"Added some feature"`)
4.  Push to the branch (`git push origin my-new-feature`)
5.  Create new Pull Request

Authors
-------

- Bought up initial idea by [Masashi Terui](https://github.com/marcy-terui) (<marcy9114@gmail.com>)
- Created and maintained by [Serverless Operations, Inc]()

Credits
-------
Jeffy is inspired by the following products.
- [Lambda Powertools](https://github.com/awslabs/aws-lambda-powertools)
- [DAZN Lambda Powertools](https://github.com/getndazn/dazn-lambda-powertools)
- [lambda_decorators](https://github.com/dschep/lambda-decorators)

License
-------

MIT License (see [LICENSE](https://github.com/marcy-terui/jeffy/blob/master/LICENSE))
