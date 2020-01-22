Jeffy(Beta)
=======

# Description

Jeffy is Serverless **"Application"** Framework, which is
suite of Utilities for Lambda functions to make it easy to develop serverless applications.

Mainly, focusing on three things.

- Logging: Providing easy to see JSON format logging, auto logging as a decorator for capturing events and responses and errors, configurable to inject additional attributes what you want to see to logs.
- Tracing: Traceable events within related functions and AWS services with generating and passing `correlation_id`.
- Decorators: To save time to implement common things for Lambda functions, providing some useful decorators.

# Install

```sh
$ pip install jeffy
```

# Features
## Logger
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
`auth_logging` decorator allows you to output `event`, `response` and `stacktrace` when you face Exceptions

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

- `auto_logging`: Automatically logs payload event and return value of lambda and when error occurs.

- `schedule`: Decorator for schedule event. just captures correlation id before main process.

- `sqs`: Decorator for sqs event. Automaticlly divide"Records" for making it easy to treat it inside main process of Lambda.

- `dynamodb_stream`: Decorator for Dynamodb stream event. Automatically divide"Records" for making it easy to treat it inside main process of Lambda.

- `kinesis_stream`: Decorator for Kinesis stream event. Automatically divide"Records" for making it easy to treat it inside main process of Lambda.

- `sns`: Decorator for SNS event. Automatically divide"Records" for making it easy to treat it inside main process of Lambda.

- `s3`: Decorator for S3 event. Automatically parse object body stream to Lambda.

- `api`: Decorator for API Gateway event. Automatically parse string if the"body" can be parsed as Dictionary. Automatically returs 500 error if unexpected error happens.

Using above decorators, inject decorator name to `<decorator name>` in the folloing example.
```python
from jeffy.framework import setup
app = setup()
@app.decorator.<decorator name>
@app.decorator.sns
@app.decorator.auto_logging
def handler(event, context):
    ...
```

- `json_scheme_validator`: Decorator for Json scheme valiidator. Automatically validate body with following json scheme.
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

- `api_json_scheme_validator`: Decorator for Json scheme valiidator for api. Automatically validate body with following json scheme. Returns 400 error if the validation failes.
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

## CorrelationIDs
CorrelationID is to trace subsequent Lambda functions and services. Jeffy automatically extract correlation IDs and caputure logs from the invocation event.

Also, Jeffy provide boto3 wrapper client to create and inject correlation IDs.

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

License
-------

MIT License (see [LICENSE](https://github.com/marcy-terui/jeffy/blob/master/LICENSE))
